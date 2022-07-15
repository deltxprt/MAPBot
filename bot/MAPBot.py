import sys
import os

sys.path.insert(0, '/module_folder') # adding the function we made in module_folder

import discord
import asyncio
import requests
import json
import re
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import Bot
from discord.ext import tasks, commands
from amp import GetInstancesStatus
from ast import For

description = '''
    Bot made to manage and report on game servers that are hosted on Markaplay™.
'''

intents = discord.Intents.default()

token = os.environ['TOKEN']
AMPUsername = os.environ['username']
AMPPass = os.environ['AccountPass']
Prefix = os.environ['Prefix']
AMPUrl = os.environ['url']

OWNERS = [232011534367326230]
BLACKLIST = []
client = commands.Bot(command_prefix=Prefix, description=description, intents=intents, help_command=None)

@client.event # Change the status of the bot
async def on_ready(): 
    Instances = GetInstancesStatus(AMPUrl, AMPUsername, AMPPass)
    while Instances:
        for Instance in Instances:
            await client.change_presence(status=discord.Status.online, activity=discord.Game(f"{Instance['Game']} | {Instance['FriendlyName']} | Active Users: {Instance['Active Users']}\{Instance['Max Users']}"))
            await asyncio.sleep(10)

@client.command()
async def help(ctx):
    
    embed = discord.Embed(
        colour = discord.Colour.orange()
    )
    
    embed.set_author(name='Help')
    embed.add_field(name='GetAllServerStatus', value='Get all Game Servers Status', inline=True)
    embed.add_field(name='GetServerStatus', value='Get a specific Game Server Status', inline=True)
    
    await ctx.send(embed=embed)

@client.command() # command to get the result of all the metrics of all the AMP Instances
async def GetAllServerStatus(ctx):
    AllStatus = GetInstancesStatus("amp.markaplay.net", "MapBot", AccountPass)
    for Instance in AllStatus:
        await ctx.send(f"```Server Name: {Instance['FriendlyName']}\nGame: {Instance['Game']}\nIsRunning: {Instance['Running']}\nCPU Usage: {Instance['CPU Usage']}%\nMemory Usage: {Instance['Memory Usage']}%\nActive Users: {Instance['Active Users']}\{Instance['Max Users']}```")

@client.command() # command to get the result of all the metrics of specific AMP Instances
async def GetServerStatus(ctx, name):
    AllStatus = GetInstancesStatus("amp.markaplay.net", "MapBot", AccountPass)
    IsFound = []
    for Instance in AllStatus:
        if name in Instance['FriendlyName']: # match for the user reponse in the list of all the AMP Instances | powershell equivilent would be if($name -like $instance.FriendlyName)
            IsFound.append(True)
            await ctx.send(f"```Server Name: {Instance['FriendlyName']}\nGame: {Instance['Game']}\nIsRunning: {Instance['Running']}\nCPU Usage: {Instance['CPU Usage']}%\nMemory Usage: {Instance['Memory Usage']}%\nActive Users: {Instance['Active Users']}\{Instance['Max Users']}```")
        else:
            IsFound.append(False)
    if IsFound[True] < 0:
        await ctx.send("Oh no! The server you are looking for is not found! :pensive:")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("I don't understand :thinking: \n Please do !help to see what commands i can respond to!")

client.run(token)