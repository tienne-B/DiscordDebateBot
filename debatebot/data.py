from discord.ext import commands

from .integrations import get_integration


class DataCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.has_role("Convenor")
    async def delete_data(self, ctx, *args):
        await self.bot.db.execute("DELETE FROM tournament WHERE guild_id=$1;", ctx.guild.id)
        await ctx.send("All data pertaining to this tournament has been deleted from this bot's database.")

    @commands.command(pass_context=True)
    @commands.has_role("Convenor")
    async def import_participants(self, ctx, *args):
        tournament = await self.bot.db.fetchrow("SELECT * FROM tournament WHERE guild_id=$1;", ctx.guild.id)
        integration = await get_integration(tournament, ctx, self.bot.db)
        await integration.get_participants()
