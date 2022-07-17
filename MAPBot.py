import sys
import os

import discord
import asyncio
import requests
import json
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import Bot
from discord.ext import tasks, commands
import mysql.connector
from ast import For

# Environnement variables

token = os.environ['TOKEN']
Prefix = os.environ['Prefix']
APIUrl = os.environ['DOUrl']
SecretToken = os.environ['SecretToken']
DBName = os.environ['DBName']
DBPassword = os.environ['DBPassword']
DBUser = os.environ['DBUser']
DBHost = os.environ['DBHost']


# Loading functions
def AMPStatus(url,SecretToken):
    header = {
        "accept": "application/json",
        "X-Require-Whisk-Auth": SecretToken
        }
    response = requests.get(url, headers=header)
    result = json.loads(response.text)
    return result

# Connecting to the database

mydb = mysql.connector.connect(
  host=DBHost,
  port="25060",
  user=DBUser,
  password=DBPassword,
  database=DBName
)

# Writing to Database

mycursor = mydb.cursor()

TableCheck=mycursor.execute("SHOW TABLES")
if 'InstanceStatus' not in TableCheck:
    mycursor.execute("CREATE TABLE InstanceStatus (FriendlyName VARCHAR(255), 'Active Users' VARCHAR(255), 'Max Users' VARCHAR(255), Game VARCHAR(255), Running VARCHAR(255), 'CPU Usage' VARCHAR(255), 'Memory Usage' VARCHAR(255)")
    mydb.commit()

AddData= "INSERT INTO customers (FriendlyName, 'Active Users', 'Max Users', Game, Running, 'CPU Usage', 'Memory Usage') VALUES (%s, %s, %s, %s, %s, %s, %s)"
for instance in AMPStatus(APIUrl,SecretToken):
    FriendlyName = instance['name']
    ActiveUsers = instance['Active Users']
    MaxUsers = instance['Max Users']
    Game = instance['Game']
    Running = instance['running']
    CPUUsage = instance['CPU Usage']
    MemoryUsage = instance['memoryUsage']
    mycursor.execute(AddData, (FriendlyName, ActiveUsers, MaxUsers, Game, Running, CPUUsage, MemoryUsage))
    mydb.commit()
# Starting the bot

description = '''
    Bot made to manage and report on game servers that are hosted on Markaplay™.
'''

intents = discord.Intents.default()

OWNERS = [232011534367326230]
BLACKLIST = []
client = commands.Bot(command_prefix=Prefix, description=description, intents=intents, help_command=None)


@client.event  # Change the status of the bot
async def on_ready():
    Instances = AMPStatus(APIUrl, SecretToken)
    while Instances:
        for Instance in Instances:
            await client.change_presence(status=discord.Status.online, activity=discord.Game(
                f"{Instance['Game']} | {Instance['FriendlyName']} | Active Users: {Instance['Active Users']}\{Instance['Max Users']}"))
            await asyncio.sleep(10)


@client.command()
async def help(ctx):
    embed = discord.Embed(
        colour=discord.Colour.orange()
    )

    embed.set_author(name='Help')
    embed.add_field(name='GetAllServerStatus', value='Get all Game Servers Status', inline=True)
    embed.add_field(name='GetServerStatus', value='Get a specific Game Server Status', inline=True)

    await ctx.send(embed=embed)


@client.command()  # command to get the result of all the metrics of all the AMP Instances
async def GetAllServerStatus(ctx):
    AllStatus = AMPStatus(APIUrl, SecretToken)
    for Instance in AllStatus:
        await ctx.send(
            f"```Server Name: {Instance['FriendlyName']}\nGame: {Instance['Game']}\nIsRunning: {Instance['Running']}\nCPU Usage: {Instance['CPU Usage']}%\nMemory Usage: {Instance['Memory Usage']}%\nActive Users: {Instance['Active Users']}\{Instance['Max Users']}```")


@client.command()  # command to get the result of all the metrics of specific AMP Instances
async def GetServerStatus(ctx, name):
    AllStatus = AMPStatus(APIUrl, SecretToken)
    IsFound = []
    for Instance in AllStatus:
        if name in Instance['FriendlyName']:  # match for the user reponse in the list of all the AMP Instances | powershell equivilent would be if($name -like $instance.FriendlyName)
            IsFound.append(True)
            await ctx.send(
                f"```Server Name: {Instance['FriendlyName']}\nGame: {Instance['Game']}\nIsRunning: {Instance['Running']}\nCPU Usage: {Instance['CPU Usage']}%\nMemory Usage: {Instance['Memory Usage']}%\nActive Users: {Instance['Active Users']}\{Instance['Max Users']}```")
        else:
            IsFound.append(False)
    if IsFound[True] < 0:
        await ctx.send("Oh no! The server you are looking for is not found! :pensive:")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("I don't understand :thinking: \n Please do !help to see what commands i can respond to!")


client.run(token)
