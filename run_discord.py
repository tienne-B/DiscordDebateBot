# import asyncio

from discord.ext.commands import Bot
# import psycopg2

from debatebot.timer import TimerCog


description = "The Debate Bot, for all argumentive needs!"
bot = Bot(command_prefix="!", description=description)

cogs = [TimerCog]

@bot.event
async def on_ready():
    for cog in cogs:
        bot.load_cog(cog)
