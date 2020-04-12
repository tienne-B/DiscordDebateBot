import asyncio

import discord.ext.commands
# import psycopg2

description = "The Debate Bot, for all argumentive needs!"
bot = commands.Bot(command_prefix="!", description=description)

cogs = ['debatebot.timer']

@bot.event
async def on_ready():
	for cog in cogs:
		bot.load_extension(cog)
