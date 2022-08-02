from tkinter.tix import Select

from requests import options
import discord
from discord.ext import commands
from discord.ui import Select, View
import os

class Management(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def manage(self, ctx):
        servers = Select(options=[
            discord.SelectOption(label = "test1", description = "This is a test"),
            discord.SelectOption(label = "test2", description = "This is another test"),
        ])
        view = View()
        view.add_item(servers)
        await ctx.send("Choose the server", view=view)
        
def setup(bot):
    bot.add_cog(Management(bot))
