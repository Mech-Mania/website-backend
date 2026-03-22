from fastapi import APIRouter, Response
from pydantic import BaseModel
from util.auth import db, PasswordSubmission, checkPassword
'''
TODO: 
- Add a cache to minimize updates from the db
- Update cache with new data taken in transit from scoreboard writes
- Add a time interval where new data will be queried from the scoreboard to the cache to avoid conflicting data
'''

from typing import Any
import json

ScoreboardRouter = APIRouter()

class ArrDataReq(BaseModel):
    data:list[str]
    password:str = ""
    
class boolDataReq(BaseModel):
    data:bool
    password:str = ""

class teamWithScore(BaseModel):
    team:str
    score:int = 0

class gameScoreUpdate(BaseModel):
    data:dict[str,dict[str,int]]
    password:str = ""

@ScoreboardRouter.post("/scoreboard/game/score")
async def updateScores(arrContent:gameScoreUpdate)->Response:
    """Updates the scores of all teams for all games. Purges teams not mentioned"""
    
    #############
    ## Auth Logic
    #############


    if (not checkPassword(arrContent.password)):
        return Response(json.dumps({"message":"Invalid Password"}))
    
    ###############
    ## Parse W data
    ###############

    data:list[dict[str,str|int]] = []
    for team in arrContent.data:
        teamData = arrContent.data[team]
        temp:dict[str,str|int] = {game:teamData[game] for game in teamData}
        temp["team"] = team
        data.append(temp)
    
    ###########
    ## db Write 
    ###########

    _=db.table('scoreboard').delete().not_.in_("team",arrContent.data.keys()).execute()
    _=db.table('scoreboard').upsert(data,on_conflict="team",ignore_duplicates=False).execute()

    return Response(json.dumps({"message":"Success"}))


@ScoreboardRouter.get("/scoreboard/score")
async def getGameScores():
    """Returns a dict of teams and their scores for all games"""
    
    ##########
    ## db Read 
    ##########

    response:Any = db.table('scoreboard').select("*").execute().data

    ###############
    ## Parse R data
    ###############

    data:dict[str,dict[str,int]] = {}
    for row in response:

        data[row.get('team')] = {
            key:row.get(key) for i,key in enumerate(row) if i != 0
        }

    return Response(json.dumps({"message":"Success","content":data}))


@ScoreboardRouter.get("/scoreboard/status")
async def isEnabled():
    
    ##########
    ## db Read 
    ##########

    response:Any = db.table('status').select("status").eq("name","scoreboard_enabled").execute().data
    
    ###############
    ## Parse R data
    ###############

    data:bool = response[0].get("status")

    response:Any = db.table('sbsettings').select("*").execute().data
    settingsData:dict[str,dict[str,int]] = {}
    
    for row in response:
        settingsData[row.get('name')] = {
            key:row.get(key) for i,key in enumerate(row) if i != 0
        }
    
    return Response(json.dumps({"message":"Success","status":data, "settings":settingsData}))


@ScoreboardRouter.post("/scoreboard/status")
async def setEnabled(boolData:boolDataReq):
    
    #############
    ## Auth Logic
    #############


    if (not checkPassword(boolData.password)): 
        return Response(json.dumps({"message":"Invalid Password"}))
    
    ###########
    ## db Write 
    ###########
    
    _=db.table('status').update({"status":boolData.data}).eq("name","scoreboard_enabled").execute()

    return Response(json.dumps({"message":"Success"}))


@ScoreboardRouter.get("/scoreboard/game/names")
async def getGameNames():

    ##########
    ## db Read 
    ##########


    response:Any = db.table("scoreboard").select("*").limit(1).execute()
     
    ###############
    ## Parse R data
    ###############

    data = ["overall"]
    
    if response.data:
        data = list(response.data[0].keys())[1:]
    else:
        return Response(json.dumps({"message":"No content in database","content":data}))
    return Response(json.dumps({"message":"Success","content":data}))
