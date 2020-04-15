import asyncio


class BaseTabIntegration:
    """Abstract protocol/interface on which specific tab integrations should
    build on. This class provides stub methods (basically declarations) of which
    must be implemented.

    This represents operations that need to use the API provided by a debate
    tabulation service or software. Such an abstraction is needed as the
    formats, requirements, and returns may not be identical. As such, different
    calls would be required.

    Methods here can access both tab and Discord APIs, but direct interaction
    with Discord is to be avoided."""

    async def __init__(self, tournament, client=None):
        self.tournament = tournament
        self.client = client

    async def _get_api_root(self):
        """This method needs to obtain the URL to the applicable API root by the
        URL provided in the database, assuming that URL is the public homepage
        and not the API root for conviviality."""
        raise NotImplementedError

    async def get_participants(self):
        """This method is to populate the bot's `Adjudicator`, `Team`, and
        `Speaker` tables with the results of the tab's API (as well as the
        message attachment if needed)"""
        raise NotImplementedError

    async def add_participant(self):
        """Rather than bulk-adding participants, this is to find a participant's
        ID by name from the API and associate it with a Discord username."""
        raise NotImplementedError

    async def get_rooms(self):
        """Fetches the rooms from the tab to populate the `Room` table. This
        method should not effect Discord channels."""
        raise NotImplementedError

    async def get_pairings(self):
        """This method should return the list of pairings for which to move
        participants to specific channels. The format of each item in the list
        should be:

        {
            "room",
            "teams": [{"id", "name"}],
            "adjudicators": [ids],
            "observers": [ids]
        }

        The first adjudicator in the list will be considered the chair, and
        trainees (non-voting) should be in the "observers" list.

        With this standardized format, queries to get the Discord values for
        all the objects can be made outside integration classes."""
        raise NotImplementedError
