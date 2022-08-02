import os

import asyncio
import json
import requests
import discord
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import Bot
from discord.ext import tasks, commands
from discord.ui import Select, View
import mysql.connector
from ast import For
from datetime import datetime

# Environnement variables

token = os.environ['TOKEN']
Prefix = os.environ['Prefix']
APIUrl = os.environ['DOUrl']
SecretToken = os.environ['SecretToken']
DBName = os.environ['DBName']
DBPassword = os.environ['DBPassword']
DBUser = os.environ['DBUser']
DBHost = os.environ['DBHost']

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

def UpdateDB():
    mydb = mysql.connector.connect(
    host=os.environ['DBHost'],
    port="25060",
    user=os.environ['DBUser'],
    password=os.environ['DBPassword'],
    database=os.environ['DBName']
    )

    # Writing to Database

    mycursor = mydb.cursor()

    if checkTableExists(mydb, "InstanceStatus") == False:
        mycursor.execute("SET @ORIG_SQL_REQUIRE_PRIMARY_KEY = @@SQL_REQUIRE_PRIMARY_KEY")
        mycursor.execute("SET SQL_REQUIRE_PRIMARY_KEY = 0")
        mycursor.execute("CREATE TABLE InstanceStatus (FriendlyName VARCHAR(255), ActiveUsers INT, MaxUsers INT, Game VARCHAR(255), Running BOOL, CPUUsage INT, MemoryUsage INT, timestamp DATETIME)")
        mydb.commit()

    for instance in AMPStatus(APIUrl, SecretToken):
        CurrentTime = datetime.now()
        CurrentTime_Format = CurrentTime.strftime("%d/%m/%Y %H:%M:%S")
        FriendlyName = instance['FriendlyName']
        ActiveUsers = instance['Metrics']['Active Users']['RawValue']
        MaxUsers = instance['Metrics']['Active Users']['MaxValue']
        Game = instance['Module']
        Running = instance['Running']
        CPUUsage = instance['Metrics']['CPU Usage']['Percent']
        MemoryUsage = instance['Metrics']['Memory Usage']['Percent']
        Find_Instance = '''SELECT * FROM InstanceStatus WHERE FriendlyName = %s'''
        Found_Instance = mycursor.execute(Find_Instance, (FriendlyName))
        if  Found_Instance is None:
            AddData = "INSERT INTO InstanceStatus (FriendlyName, ActiveUsers, MaxUsers, Game, Running, CPUUsage, MemoryUsage, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            Data = (FriendlyName, ActiveUsers, MaxUsers, Game, Running, CPUUsage, MemoryUsage, CurrentTime_Format)
            mycursor.execute(AddData, Data)
            mydb.commit()
        else:
            UpdateData= "UPDATE InstanceStatus SET ActiveUsers = %s, MaxUsers = %s , Game = %s, Running = %s, CPUUsage = %s, MemoryUsage = %s, timestamp = %s WHERE FriendlyName = %s"
            Data = (ActiveUsers, MaxUsers, Game, Running, CPUUsage, MemoryUsage, CurrentTime_Format, FriendlyName)
            mycursor.execute(UpdateData, Data)
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
        
        

@client.command()
async def manage(self, ctx):
    servers = Select(options=[
        discord.SelectOption(label = "test1", description = "This is a test"),
        discord.SelectOption(label = "test2", description = "This is another test"),
    ])
    view = View()
    view.add_item(servers)
    await ctx.send("Choose the server", view=view)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"I don't understand :thinking: \n Please do {Prefix}help to see what commands i can respond to!")

client.run(token)
