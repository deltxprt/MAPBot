import os

import asyncio
import json
import requests
import discord
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
def AMPStatus(url, do_token):
    header = {
        "accept": "application/json",
        "X-Require-Whisk-Auth": do_token
        }
    response = requests.get(url, headers=header)
    result = json.loads(response.text)
    return result

def checkTableExists(dbcon, tablename):
    dbcur = dbcon.cursor()
    dbcur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(tablename.replace('\'', '\'\'')))
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True

    dbcur.close()
    return False

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

if checkTableExists(mydb, "InstanceStatus") == False:
    mycursor.execute("CREATE TABLE InstanceStatus (FriendlyName VARCHAR(255), ActiveUsers VARCHAR(255), MaxUsers VARCHAR(255), Game VARCHAR(255), Running VARCHAR(255), CPUUsage VARCHAR(255), MemoryUsage VARCHAR(255))")
    mydb.commit()

AddData= "INSERT INTO customers (FriendlyName, ActiveUsers, MaxUsers, Game, Running, CPUUsage, MemoryUsage) VALUES (%s, %s, %s, %s, %s, %s, %s)"
for instance in AMPStatus(APIUrl,SecretToken):
    FriendlyName = instance['name']
    ActiveUsers = instance['Active Users']
    MaxUsers = instance['Max Users']
    Game = instance['Game']
    Running = instance['running']
    CPUUsage = instance['CPU Usage']
    MemoryUsage = instance['memoryUsage']
    mycursor.execute(AddData, (FriendlyName,
                               ActiveUsers,
                               MaxUsers,
                               Game,
                               Running,
                               CPUUsage,
                               MemoryUsage
                               )
                     )
    mydb.commit()

# Starting the bot

Description = '''
    Bot made to manage and report on game servers that are hosted on Markaplay™.
'''

intents = discord.Intents.default()

OWNERS = [232011534367326230]
BLACKLIST = []
client = commands.Bot(command_prefix=Prefix,
                      description=Description,
                      intents=intents,
                      help_command=None
                      )


@client.event  # Change the status of the bot
async def on_ready():
    instances_status = AMPStatus(APIUrl, SecretToken)
    while instances_status:
        for instance_status in instances_status:
            await client.change_presence(status=discord.Status.online, activity=discord.Game(
                fr"{instance_status['Game']} | {instance_status['FriendlyName']} | Active Users: {instance_status['Active Users']}\{instance_status['Max Users']}"))
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
    all_status = AMPStatus(APIUrl, SecretToken)
    for instance_status in all_status:
        await ctx.send(
            fr"```Server Name: {instance_status['FriendlyName']}\nGame: {instance_status['Game']}\nIsRunning: {instance_status['Running']}\nCPU Usage: {instance_status['CPU Usage']}%\nMemory Usage: {instance_status['Memory Usage']}%\nActive Users: {instance_status['Active Users']}\{instance_status['Max Users']}```")


@client.command()  # command to get the result of all the metrics of specific AMP Instances
async def GetServerStatus(ctx, name):
    all_status = AMPStatus(APIUrl, SecretToken)
    is_found = []
    for instance_status in all_status:
        if name in instance_status['FriendlyName']:  # match for the user reponse in the list of all the AMP Instances | powershell equivilent would be if($name -like $instance.FriendlyName)
            is_found.append(True)
            await ctx.send(
                f"```Server Name: {instance_status['FriendlyName']}\nGame: {instance_status['Game']}\nIsRunning: {instance_status['Running']}\nCPU Usage: {instance_status['CPU Usage']}%\nMemory Usage: {instance_status['Memory Usage']}%\nActive Users: {instance_status['Active Users']}\{instance_status['Max Users']}```")
        else:
            is_found.append(False)
    if is_found[True] < 0:
        await ctx.send("Oh no! The server you are looking for is not found! :pensive:")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"I don't understand :thinking: \n Please do {Prefix}help to see what commands i can respond to!")


client.run(token)
