import asyncio
import csv

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
        return '/'.join(url)

    async def _get_adjudicators(self, assocs):
        adjudicators_response = requests.get(api + '/adjudicators/')
        if adjudicators_response.status_code == 401:
            await self.ctx.send(
                "Could not access adjudicators list. Make sure the public view "
                "of participants list is enabled (under Public Features) for "
                "the tournament in Tabbycat."
            )
            return 0
        t_adjs = adjudicators_response.json()

        adj_insertions = []
        for adj in t_adjs:
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
        teams = []
        speakers = []
        for team in requests.get(api + '/teams/').json():
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
            (SELECT t.id, r.discord_name, r.tab_id FROM (VALUES ($1, $2, $3, $4)) AS r(tournament, team_tab, tab_id, discord_name)
            INNER JOIN team AS t ON t.tournament=r.tournament AND t.tab_id=r.team_tab);""",
            speakers
        )

    async def get_participants(self):
        api = self.get_api_root()

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
        venue_request = requests.get(self.get_api_root() + '/venues/')

