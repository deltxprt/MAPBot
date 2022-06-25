# importing required modules
from ast import For

import requests # request is use for web requests/API calls

import json # json is use for manipulating JSON data

import re # re is use for regular expressions/regex


def GetInstancesStatus(AMPUrl, AMPUser, AMPPass): #start of the Function
    urlpattern = '(http|https)://\S*' # pattern use to validate if url have http or https
    IsHTTP = re.match(urlpattern, AMPUrl) # match the url with the pattern
    if IsHTTP: # if url have http or https just add the paths
        Login = AMPUrl + '/API/Core/Login'
        GInstances = AMPUrl + '/API/ADSModule/GetInstances'
        UrlStatInstance = AMPUrl + '/API/ADSModule/GetInstance'
    else: # else add the protocol and paths
        Login = 'https://' + AMPUrl + '/API/Core/Login'
        GInstances = 'https://' + AMPUrl + '/API/ADSModule/GetInstances'
        UrlStatInstance = 'https://' + AMPUrl + '/API/ADSModule/GetInstance'

    Headers = { "accept" : "application/json" } # Very important!! This is the header for the request

    data = { # This is use to fetch the sessionID token on AMP Server
        "username":AMPUser,
        "password":AMPPass,
        "token":"",
        "rememberMe":"true"
    }

    request = requests.post(Login, headers=Headers, json=data) # sending the request to AMP Server
    result = json.loads(request.text) # converting the response from json format

    if result['success'] == True: # make sure the request is success
        sessionID = result['sessionID']
    else:
        print('Login failed')

    sid = { # SessionId we fetch from last request
            "SESSIONID":sessionID,
    }

    Instancesraw = requests.post(GInstances, headers=Headers, json=sid) # getting all the instances from AMP Server

    Instances = json.loads(Instancesraw.text) # converting the response from json format
    try:
        Instances = Instances['result'][0]['AvailableInstances']
    except:
        print('Permission error')
    # if Instances['result']: # in case we have a permission error
    #     Instances = Instances['result'][0]['AvailableInstances']
    # else:
    #     print('Permission error!')

    InstancesID = [] # Empty Array to store the InstanceID

    InstancesStatuses = [] # Empty Array to store the Instance Status

    for instance in Instances: # for loop to get all the InstanceID from the server
        InstancesInfo = {"InstanceID":None} # defining the keys we want from the response
        InstancesInfo['InstanceID'] = instance['InstanceID'] # inserting the keys we want from the response
        InstancesID.append(InstancesInfo) # Store the InstanceID in the InstancesID array

    for status in InstancesID: # with the instanceID we can get the status of all instances
        ID = status['InstanceID'] # for each instanceID we get the status
        InstanceStats = { # body of the request
            "SESSIONID":sessionID,
            "InstanceId":ID
        }
        IStatsraw = requests.post(UrlStatInstance, headers=Headers, json=InstanceStats) # getting the status of the instance
        InstancesStatuses.append(json.loads(IStatsraw.text)) # storing the status in the InstancesStatuses array while converting the response from json format

    FullStatus = [] # Empty Array to store the Full Status

    for InstStatus in InstancesStatuses: # for loop to format what data we want from the response
        if InstStatus['FriendlyName'] != 'ADS01': # excluding the ADS01/controller instances
            Status = {"FriendlyName":None, "Game":None, "Running":None, "CPU Usage":None, "Memory Usage":None, "Active Users":None, "Max Users":None} #defining the keys we want from the response
            Status['FriendlyName'] = InstStatus['FriendlyName']
            Status['Game'] = InstStatus['Module']
            Status['Running'] = InstStatus['Running']
            Status['CPU Usage'] = InstStatus['Metrics']['CPU Usage']['Percent']
            Status['Memory Usage'] = InstStatus['Metrics']['Memory Usage']['Percent']
            Status['Active Users'] = InstStatus['Metrics']['Active Users']['RawValue']
            Status['Max Users'] = InstStatus['Metrics']['Active Users']['MaxValue']
            FullStatus.append(Status) # Store the Full Status in the FullStatus array

    return FullStatus # return the FullStatus array