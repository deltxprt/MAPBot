import os

import asyncio
import json
import requests
import discord
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import Bot
from discord.ext import tasks, commands
#import mysql.connector
from ast import For
from datetime import datetime

# Environnement variables

token = os.environ['TOKEN']
Prefix = os.environ['Prefix']
APIUrl = os.environ['DOUrl']
SecretToken = os.environ['SecretToken']

CurrentTime = datetime.now()
CurrentTime_Format = CurrentTime.strftime("%d/%m/%Y %H:%M:%S")


# Loading functions

def AMPStatus(url, do_token):
    header = {
        "accept": "application/json",
        "Authorization": f"Basic {do_token}"
        }
    response = requests.post(url, headers=header)
    result = json.loads(response.text)
    result = result['Body']
    return result

# Starting the bot

Description = '''
    Bot made to manage and report on game servers that are hosted on Markaplay™.
'''

intents = discord.Intents.all()

OWNERS = [232011534367326230]
BLACKLIST = []
client = commands.Bot(command_prefix=Prefix,description=Description,intents=intents,help_command=None)


@client.event  # Change the status of the bot
async def on_ready():
    #UpdateDB()
    instances_status = AMPStatus(APIUrl, SecretToken)
    while instances_status:
        for instance_status in instances_status:
            await client.change_presence(status=discord.Status.online, activity=discord.Game(
                fr"{instance_status['Module']} | {instance_status['FriendlyName']} | Active Users: {instance_status['Metrics']['Active Users']['RawValue']}\{instance_status['Metrics']['Active Users']['MaxValue']}"))
            await asyncio.sleep(10)


@client.command()
async def help(ctx):
    embed = discord.Embed(
        colour=discord.Colour.orange()
    )

    embed.set_author(name='Help')
    embed.add_field(name='GetAllServersStatus', value='Get all Game Servers Status', inline=True)
    embed.add_field(name='GetServerStatus', value='Get a specific Game Server Status', inline=True)

    await ctx.send(embed=embed)


@client.command()  # command to get the result of all the metrics of all the AMP Instances
async def GetAllServersStatus(ctx):
    #UpdateDB()
    all_status = AMPStatus(APIUrl, SecretToken)
    for instance_status in all_status:
        embed = discord.Embed(
            colour=discord.Colour.blurple()
        )
        embed.set_author(name=instance_status['FriendlyName'])
        embed.add_field(name='Game', value=instance_status['Module'], inline=True)
        embed.add_field(name='Running', value=instance_status['Running'], inline=True)
        embed.add_field(name='Active Users', value=f"{instance_status['Metrics']['Active Users']['RawValue']}/{instance_status['Metrics']['Active Users']['MaxValue']}", inline=True)
        embed.add_field(name='CPU Usage', value=f"{instance_status['Metrics']['CPU Usage']['Percent']}%", inline=True)
        embed.add_field(name='Memory Usage', value=f"{instance_status['Metrics']['Memory Usage']['Percent']}%", inline=True)
        
        await ctx.send(embed=embed)


@client.command()  # command to get the result of all the metrics of specific AMP Instances
async def GetServerStatus(ctx, name):
    #UpdateDB()
    all_status = AMPStatus(APIUrl, SecretToken)
    is_found = []
    for instance_status in all_status:
        if name in instance_status['FriendlyName']:  # match for the user reponse in the list of all the AMP Instances | powershell equivilent would be if($name -like $instance.FriendlyName)
            is_found.append(True)
            embed = discord.Embed(
                colour=discord.Colour.blurple()
            )
            embed.set_author(name=instance_status['FriendlyName'])
            embed.add_field(name='Game', value=instance_status['Module'], inline=True)
            embed.add_field(name='Running', value=instance_status['Running'], inline=True)
            embed.add_field(name='Active Users', value=f"{instance_status['Metrics']['Active Users']['RawValue']}/{instance_status['Metrics']['Active Users']['MaxValue']}", inline=True)
            embed.add_field(name='CPU Usage', value=f"{instance_status['Metrics']['CPU Usage']['Percent']}%", inline=True)
            embed.add_field(name='Memory Usage', value=f"{instance_status['Metrics']['Memory Usage']['Percent']}%", inline=True)
            await ctx.send(embed=embed)
        else:
            is_found.append(False)
    if is_found[True] < 0:
        await ctx.send("Oh no! The server you are looking for is not found! :pensive:")
        
        

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"I don't understand :thinking: \n Please do {Prefix}help to see what commands i can respond to!")

client.run(token)
