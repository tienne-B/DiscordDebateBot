import asyncio
import csv
import itertools

import asyncpg
import requests

from .base import BaseTabIntegration


class TabbycatIntegration(BaseTabIntegration):

    async def get_api_root(self):
        """The database URL format is <domain>/<tournament_slug> while the API
        root is <domain>/api/v1/tournaments/<tournament_slug> for the specified
        tournament."""
        url = self.tournament['url'].split('/')
        if not url[-1]:  # Slash at the end
            url.pop()
        url.insert(-1, 'api/v1')
        if requests.get('/'.join(url) + '/').status_code == 404:
            await self.ctx.send("Does not support versions of Tabbycat < 2.4. Please upgrade.")
        return '/'.join(url)

    async def _get_adjudicators(self, assocs):
        adjudicators_response = requests.get(self.get_api_root() + '/adjudicators')
        if adjudicators_response.status_code == 401:  # Unauthorized
            await self.ctx.send(
                "Could not access adjudicators list. Make sure the public view "
                "of participants list is enabled (under Public Features) for "
                "the tournament in Tabbycat."
            )
            return 0

        adj_insertions = []
        for adj in adjudicators_response.json():
            try:
                username = assocs[adj['name']]
                del assocs[adj['name']]
            except KeyError:
                continue
            adj_insertions.append((self.tournament['id'], adj['id'], username))

        await self.db.executemany(
            "INSERT INTO adjudicator(tournament, discord_name, tab_id) VALUES ($1, $2, $3);",
            adj_insertions
        )

    async def _get_teams(self, assocs):
        teams_response = requests.get(self.get_api_root() + '/teams')
        if teams_response.status_code == 401:  # Unauthorized
            return 0  # Error message shown with adjs

        teams = []
        speakers = []
        for team in teams_response.json():
            teams.append((self.tournament['id'], team['id']))

            for speaker in team['speakers']:
                try:
                    username = assocs[speaker['name']]
                    del assocs[speaker['name']]
                except KeyError:
                    continue
                speakers.append((self.tournament['id'], team['id'], speaker['id'], username))

        await self.db.executemany(
            "INSERT INTO team(tournament, tab_id) VALUES ($1, $2);",
            teams
        )
        await self.db.executemany(
            """INSERT INTO speaker(team, tab_id, discord_name)
            (SELECT t.id, r.discord_name, r.tab_id FROM
            (VALUES ($1, $2, $3, $4)) AS r(tournament, team_tab, tab_id, discord_name)
            INNER JOIN team AS t ON t.tournament=r.tournament AND t.tab_id=r.team_tab);""",
            speakers
        )

    async def get_participants(self):

        try:
            attachment = self.ctx.message.attachments[0]
        except IndexError:
            await self.ctx.send(
                "File not found. Please attach a CSV file associating "
                "participants' names with their Discord usernames."
            )
            return 0
        assocs = {r[0]: r[1] for r in csv.reader(attachment.decode('utf-8'))}

        adjs = asyncio.create_task(self._get_adjudicators(assocs))
        teams = asyncio.create_task(self._get_teams(assocs))

        await adjs
        await teams

        unresolved = ["%s — %s" % (p, d) for p, d in assocs.items()]
        if len(unresolved) > 0:
            await self.ctx.send(
                "Participants partially added. Missing participants:\n%s" %
                "\n".join(unresolved)
            )
        else:
            await self.ctx.send("All participants added.")

    def get_rooms(self):
        venue_request = requests.get(self.get_api_root() + '/venues')
        return [(v['id'], v['display_name']) for v in venue_request.json()]

    def get_pairings(self, round):
        pairings_req = requests.get(self.get_api_root() + '/rounds/' + round + '/pairings')
        if pairings_req.status_code == 401:  # Unauthorized
            await self.ctx.send(
                """Could not access pairings. Make sure the round is released and
                the public view is activated."""
            )
            return 0

        teams_req = requests.get(self.get_api_root() + '/teams')
        if pairings_req.status_code == 401:  # Unauthorized
            await self.ctx.send(
                """Could not access team list. Make sure the public view of the
                participants' list is activated."""
            )
            return 0
        team_names = {t['id']: t.get('short_name', t['code_name']) for t in teams_req.json()}

        channels_query = await self.db.fetch(
            "SELECT channel, tab_id FROM room WHERE tournament=$1;",
            self.tournament['id']
        )
        channels = {q['tab_id']: q['channel'] for q in channels_query}

        teams_query = await self.db.fetch(
            "SELECT id, tab_id FROM team WHERE tournament=$1;",
            self.tournament['id']
        )
        teams = {q['tab_id']: q['id'] for q in teams_query}

        speakers_query = await self.db.fetch(
            "SELECT team, discord_name FROM speaker WHERE team IN $1 ORDER BY team;",
            list(teams.values())
        )
        speakers = {k: [v['discord_name'] for v in g] for k, v in itertools.groupby(
            speakers_query, lambda x: x['team']
        )}

        adj_query = await self.db.fetch(
            "SELECT tab_id, discord_name FROM adjudicator WHERE tournament=$1",
            self.tournament['id']
        )
        adjs = {a['tab_id']: a['discord_name'] for a in adj_query}

        results = []
        for pairing in pairings_req.json():
            p_teams = []
            for team in pairing.teams:
                tab_id = team.split('/')[-2]
                p_teams.append({
                    "name": team_names[tab_id],
                    "speakers": speakers[teams[tab_id]]
                })

            p_adjs = [adjs[pairing['adjudicators']['chair']]]
            p_adjs += [adjs[a] for a in pairing['adjudicators']['panellists']]
            p_obs = [adjs[a] for a in pairing['adjudicators']['trainees']]
            p_info = {
                "channel": channels[pairing.venue.split('/')[-2]],
                "teams": p_teams,
                "adjudicators": p_adjs,
                "observers": p_objs
            }
            results.append(p_info)
        return results
