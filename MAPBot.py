import sys
import os

import discord
import asyncio
import requests
import json
import re
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import Bot
from discord.ext import tasks, commands
from ast import For

# Environnement variables

token = os.environ['TOKEN']
AMPUsername = os.environ['username']
AMPPass = os.environ['AccountPass']
Prefix = os.environ['Prefix']
AMPUrl = os.environ['url']

# Loading functions
def GetInstancesStatus(AMPUrl: str,
                       AMPUser: str,
                       AMPPass: str):  # start of the Function
    urlpattern = '(http|https)://\S*'  # pattern use to validate if url have http or https
    IsHTTP = re.match(urlpattern, AMPUrl)  # match the url with the pattern
    if IsHTTP:  # if url have http or https just add the paths
        Login = AMPUrl + '/API/Core/Login'
        GInstances = AMPUrl + '/API/ADSModule/GetInstances'
        UrlStatInstance = AMPUrl + '/API/ADSModule/GetInstance'
    else:  # else add the protocol and paths
        Login = 'https://' + AMPUrl + '/API/Core/Login'
        GInstances = 'https://' + AMPUrl + '/API/ADSModule/GetInstances'
        UrlStatInstance = 'https://' + AMPUrl + '/API/ADSModule/GetInstance'

    Headers = {"accept": "application/json"}  # Very important!! This is the header for the request

    data = {  # This is use to fetch the sessionID token on AMP Server
        "username": AMPUser,
        "password": AMPPass,
        "token": "",
        "rememberMe": "true"
    }

    request = requests.post(Login, headers=Headers, json=data)  # sending the request to AMP Server
    result = json.loads(request.text)  # converting the response from json format

    if result['success'] == True:  # make sure the request is success
        sessionID = result['sessionID']
    else:
        print('Login failed')

    sid = {  # SessionId we fetch from last request
        "SESSIONID": sessionID,
    }

    Instancesraw = requests.post(GInstances, headers=Headers, json=sid)  # getting all the instances from AMP Server

    Instances = json.loads(Instancesraw.text)  # converting the response from json format
    try:
        Instances = Instances['result'][0]['AvailableInstances']
    except:
        print('Permission error')
    # if Instances['result']: # in case we have a permission error
    #     Instances = Instances['result'][0]['AvailableInstances']
    # else:
    #     print('Permission error!')

    InstancesID = []  # Empty Array to store the InstanceID

    InstancesStatuses = []  # Empty Array to store the Instance Status

    for instance in Instances:  # for loop to get all the InstanceID from the server
        InstancesInfo = {"InstanceID": None}  # defining the keys we want from the response
        InstancesInfo['InstanceID'] = instance['InstanceID']  # inserting the keys we want from the response
        InstancesID.append(InstancesInfo)  # Store the InstanceID in the InstancesID array

    for status in InstancesID:  # with the instanceID we can get the status of all instances
        ID = status['InstanceID']  # for each instanceID we get the status
        InstanceStats = {  # body of the request
            "SESSIONID": sessionID,
            "InstanceId": ID
        }
        IStatsraw = requests.post(UrlStatInstance, headers=Headers,
                                  json=InstanceStats)  # getting the status of the instance
        InstancesStatuses.append(json.loads(
            IStatsraw.text))  # storing the status in the InstancesStatuses array while converting the response from json format

    FullStatus = []  # Empty Array to store the Full Status

    for InstStatus in InstancesStatuses:  # for loop to format what data we want from the response
        if InstStatus['FriendlyName'] != 'ADS01':  # excluding the ADS01/controller instances
            Status = {"FriendlyName": None, "Game": None, "Running": None, "CPU Usage": None, "Memory Usage": None,
                      "Active Users": None, "Max Users": None}  # defining the keys we want from the response
            Status['FriendlyName'] = InstStatus['FriendlyName']
            Status['Game'] = InstStatus['Module']
            Status['Running'] = InstStatus['Running']
            Status['CPU Usage'] = InstStatus['Metrics']['CPU Usage']['Percent']
            Status['Memory Usage'] = InstStatus['Metrics']['Memory Usage']['Percent']
            Status['Active Users'] = InstStatus['Metrics']['Active Users']['RawValue']
            Status['Max Users'] = InstStatus['Metrics']['Active Users']['MaxValue']
            FullStatus.append(Status)  # Store the Full Status in the FullStatus array

    return FullStatus  # return the FullStatus array


# End of functions

description = '''
    Bot made to manage and report on game servers that are hosted on Markaplay™.
'''

intents = discord.Intents.default()

OWNERS = [232011534367326230]
BLACKLIST = []
client = commands.Bot(command_prefix=Prefix, description=description, intents=intents, help_command=None)


@client.event  # Change the status of the bot
async def on_ready():
    Instances = GetInstancesStatus(AMPUrl, AMPUsername, AMPPass)
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
    AllStatus = GetInstancesStatus("amp.markaplay.net", "MapBot", AccountPass)
    for Instance in AllStatus:
        await ctx.send(
            f"```Server Name: {Instance['FriendlyName']}\nGame: {Instance['Game']}\nIsRunning: {Instance['Running']}\nCPU Usage: {Instance['CPU Usage']}%\nMemory Usage: {Instance['Memory Usage']}%\nActive Users: {Instance['Active Users']}\{Instance['Max Users']}```")


@client.command()  # command to get the result of all the metrics of specific AMP Instances
async def GetServerStatus(ctx, name):
    AllStatus = GetInstancesStatus("amp.markaplay.net", "MapBot", AccountPass)
    IsFound = []
    for Instance in AllStatus:
        if name in Instance[
            'FriendlyName']:  # match for the user reponse in the list of all the AMP Instances | powershell equivilent would be if($name -like $instance.FriendlyName)
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
