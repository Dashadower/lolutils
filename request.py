# -*- coding:utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        LolUtils
# Purpose:
#
# Author:      Dashadower
#
# Created:     15-08-2016
# Copyright:   (c) Nitro 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from urllib.request import urlopen
from urllib.parse import quote
from  urllib.error import HTTPError
import json,pprint,operator
class NoUserError(Exception):
    def __init__(self):

        self.message = "No such user"

class NoGameError(Exception):
    def __init__(self):

        self.message = "Current user is not in a game"
class TechnicalError(Exception):
    def __init__(self):
        self.message = "Unable to retrieve data"


def getSummonerID(Region,Username,APIKEY):
    """Returns Summoner ID of specified Username"""
    url = "https://%s.api.pvp.net/api/lol/%s/v1.4/summoner/by-name/%s?api_key=%s"%(Region,Region,quote(Username),APIKEY)
    try:
        req = urlopen(url)
    except HTTPError as er:
        if er.code == 404:
            raise NoUserError()
        else: raise TechnicalError()
    else:
        data = json.loads(req.read().decode("utf-8"))[Username.lower().replace(" ","")]["id"]
        return(data)

def getSummonerTier(Region,SummonerID,APIKEY):
    """Returns Summoner League, tier in League-Tier format
    ex: GOLD-V
    Leagues:
    CHALLENGE
    MASTER
    DIAMOND
    PLATINUM
    GOLD
    SILVER
    BRONZE

    Tiers:
    I
    II
    III
    IV
    V"""
    url = "https://%s.api.pvp.net/api/lol/%s/v2.5/league/by-summoner/%s?api_key=%s"%(Region,Region,SummonerID,APIKEY)
    try:
        req = urlopen(url)
    except HTTPError as er:
        if er.code == 404:
            return "UNRANKED-"
        else: return TechnicalError()
    else:
        data = json.loads(req.read().decode("utf-8"))
        league = data[str(SummonerID)][0]["tier"]
        players = data[str(SummonerID)][0]["entries"]
        for player in players:
            if player["playerOrTeamId"] == str(SummonerID):
                tier = player["division"]

        return "%s-%s"%(league,tier)

def getSummonerTiers(SummonerIds,Region,APIKEY):
    """Returns a list of (id,username, League-Tier) of multiple Summoner IDs. SummonerIds tuple must be the same format of parseLiveGameData's output
    SummonerIds example [("34353434","Username"),("4242343","Username2"),...]"""
    sumids = []
    for item in SummonerIds:
        sumids.append(item[0])
    SumIds = ",".join(sumids)
    url = "https://%s.api.pvp.net/api/lol/%s/v2.5/league/by-summoner/%s/entry?api_key=%s"%(Region,Region,SumIds,APIKEY)
    #print(url)
    req = urlopen(url)
    data = json.loads(req.read().decode("utf-8"))
    players = []
    """for player_id,player in SummonerIds:
        pdata = data[player_id]

        pleague = pdata[0]["tier"]
        for indivisual in pdata[0]["entries"]:
            if indivisual["playerOrTeamId"] == player_id:
                ptier = indivisual["division"]
        players.append((player_id,player,"%s-%s"%(pleague,ptier)))"""
    for player_id,player in SummonerIds:
        try:
            pdata = data[player_id]
        except KeyError: players.append((player_id,player,"UNRANKED"))
        else:
            pleague = pdata[0]["tier"]
            division = pdata[0]["entries"][0]["division"]
            players.append((player_id,player,"%s-%s"%(pleague,division)))



    return players



def getLiveGameInfo(Region,SummonerID,APIKEY):
    """Returns unformatted live game data in which specified summoner is playing"""
    url = "https://%s.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/%s/%s?api_key=%s"%(Region,Region.upper(),SummonerID,APIKEY)
    try:
        req = urlopen(url)
    except HTTPError as er:
        if er.code == 404:
            raise NoGameError()
        else: raise TechnicalError()
    else:
        data = json.loads(req.read().decode("utf-8"))

        return data

def getChampionMasteryPoints(Region,SummonerID,APIKEY,ChampionID):
    """Returns the champion mastery level and points of the specified SummonerID's champion in Level-Points format"""
    url = "https://%s.api.pvp.net/championmastery/location/%s/player/%s/champion/%s?api_key=%s"%(Region,Region.upper(),SummonerID,ChampionID,APIKEY)

    try:
        req = urlopen(url)
    except HTTPError as er:
        if er.code == 404:
            raise NoUserError()
        else: raise TechnicalError()
    else:
        data = json.loads(req.read().decode("utf-8"))
        level = data["championLevel"]
        points = data["championPoints"]
        return "%s-%s"%(level,points)
def getMostChampions(Region,SummonerID,APIKEY,count):
    """returns a list of the champions of the most points in the following format:
        [("Championid",level,points)...]"""
    url = "https://%s.api.pvp.net/championmastery/location/%s/player/%s/topchampions?count=%d&api_key=%s"%(Region,Region.upper(),SummonerID,count,APIKEY)
    try:
        req = urlopen(url)
    except HTTPError as er:
        if er.code == 404:
            raise NoUserError()
        else: raise TechnicalError()
    else:
        data = json.loads(req.read().decode("utf-8"))
        champs = []
        for x in sorted(data,key=lambda k: k["championPoints"],reverse=True):
            champs.append((x["championId"],x["championLevel"],x["championPoints"]))
        return champs
def parseLiveGameData(gameData):
    """Returns a tuple contaning 2 lists blueteam,redteam, each list consisting a list where each in item is a tuple of (summonerId,summonerName)
    ex ([("4234235234","User1"),...],[("41414124","User2"),...])"""
    gametype = gameData["gameType"]
    gamemode = gameData["gameMode"]
    players = gameData["participants"]
    BlueTeam = []
    RedTeam = []
    for player in players:
        if player["teamId"] == 100:
            BlueTeam.append((str(player["summonerId"]),str(player["summonerName"])))
        elif player["teamId"] == 200:
            RedTeam.append((str(player["summonerId"]),str(player["summonerName"])))

    return (BlueTeam,RedTeam)

def parseLiveGameChampionData(gameData):
    BlueTeam = []
    RedTeam = []
    players = gameData["participants"]
    for player in players:
        if player["teamId"] == 100:
            BlueTeam.append((str(player["summonerId"]),str(player["summonerName"]),str(player["championId"])))
        elif player["teamId"] == 200:
            RedTeam.append((str(player["summonerId"]),str(player["summonerName"]),str(player["championId"])))

    return BlueTeam, RedTeam

if __name__ == "__main__":
	#test script
    APIKEY = "MY_API_KEY"

    #print(getSummonerID("kr","Dashadower"))
    #print(getSummonerID("kr","무앤디"))
    #print(getSummonerTiers((("45662000","원산학사"),("32891296","순 띠")),"kr"))


    print(getMostChampions("kr","32891296",APIKEY,3))
