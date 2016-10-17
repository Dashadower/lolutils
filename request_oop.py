# -*- coding:utf-8 -*-
from urllib.request import urlopen
from urllib.parse import quote
from  urllib.error import HTTPError
import json,pprint
import request



class RiotAPI():
    """Underlying class, wrapping region and apikey parameters so they can be passed along to other classes"""
    def __init__(self,region,APIKey):
        self.Region = region
        self.APIKey = APIKey
    def request(self):
        pass
class Summoner():
    """Summoner class to retrieve summoner id,tier,division,and current game"""
    def __init__(self,SummonerName,apiclass):
        """Enter summonerName specified and RiotAPI class created to the apiclass"""
        self.API = apiclass
        self.Region = self.API.Region
        self.APIKey = self.API.APIKey
        self.SummonerName = SummonerName
        self.SummonerID = request.getSummonerID(self.Region,self.SummonerName,self.APIKey)

    def getSummonerID(self):
        return self.summonerID
    def getTier(self):
        """Returns League-Tier format of the specified summoner."""
        self.division,self.tier = request.getSummonerTier(self.Region,self.SummonerID,self.APIKey).split("-")
        return ("%s-%s"%(self.division,self.tier))
    def getChampionData(self,championId):
        return request.getChampionMasteryPoints(self.Region,self.SummonerID,self.APIKey,championId)
    def getMostChampionData(self,count):
        return request.getMostChampions(self.Region,self.SummonerID,self.APIKey,count)
class Game():
    """Game class, handling currentgame data"""
    def __init__(self,SummonerObject,apiclass=None):
        """CurrentGame object. Arguments: Summoner class"""
        self.Summoner = SummonerObject
        self.SummonerName = self.Summoner.SummonerName
        self.SummonerID = self.Summoner.SummonerID
        if not apiclass:
            self.API = self.Summoner.API
        else:
            self.API = apiclass
        self.Region = self.API.Region
        self.APIKey = self.API.APIKey

        self.GameData = request.getLiveGameInfo(self.Region,self.SummonerID,self.APIKey)
        self.BluePlayers, self.RedPlayers = request.parseLiveGameData(self.GameData)
        self.BlueChampions,self.RedChampions = request.parseLiveGameChampionData(self.GameData)
        self.GameType = self.GameData["gameType"]
        self.GameMode = self.GameData["gameMode"]
        self.Duration = self.GameData["gameLength"]
        self.mapId = int(self.GameData["mapId"])
        if int(self.GameData["gameQueueConfigId"]) in [6,9,410]:
            self.QueueType = "RANKED"
        elif int(self.GameData["gameQueueConfigId"]) in [2,400]:
            self.QueueType = "NORMAL"
        elif int(self.GameData["gameQueueConfigId"]) in [7,31,32,33]:
            self.QueueType = "BOT"
        elif int(self.GameData["gameQueueConfigId"]) in [0]:
            self.QueueType = "CUSTOM"


if __name__ == "__main__":
    #Test app
    myapi = RiotAPI("kr","MY_API_KEY")
    nick = "무앤디"
    print(Summoner(nick,myapi).getMostChampionData(3))
    print(Summoner(nick,myapi).SummonerID)
    print(Summoner(nick,myapi).getTier())
    print(Game(Summoner(nick,myapi)).GameMode)

