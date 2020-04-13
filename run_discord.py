import asyncio
import os

from discord.ext.commands import Bot
import asyncpg

from debatebot import DataCog, TimerCog


description = "The Debate Bot, for all argumentive needs!"
cogs = [DataCog, TimerCog]


class DebateBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db = None
        self.loop.create_task(self.connect_to_db())

    async def connect_to_db(self):
        try:
            self.db = await asyncpg.create_pool(os.environ.get("DATABASE_URL"))
        except Exception as e:
            print("[DB] An error occurred: {0}\n".format(e))


bot = DebateBot(command_prefix="!", description=description)


@bot.event
async def on_ready():
    for cog in cogs:
        bot.add_cog(cog(bot))

@bot.event
async def on_guild_join(guild):
    db_exists = await bot.db.fetchval("SELECT COUNT(*) FROM tournament WHERE guild_id=$1", guild.id)
    if not bool(db_exists):
        await bot.db.execute("INSERT INTO tournament(guild_id) VALUES ($1)", guild.id)


bot.run(os.environ.get("DISCORD_TOKEN"))
