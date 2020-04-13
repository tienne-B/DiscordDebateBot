from discord.ext import commands


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
        username_list = ctx.message.attachments[0]
