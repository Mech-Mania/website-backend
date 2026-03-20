from fastapi import APIRouter, Response
from pydantic import BaseModel
from router.auth import db, PasswordSubmission, checkPassword
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
    data:list[teamWithScore] # team, score
    password:str = ""
    game:str = ""


@ScoreboardRouter.post("/scoreboard/team")
async def updateTeams(arrContent:ArrDataReq)->Response:
    """Updates teams so that the teams list reflects the given list"""
    
    if (not checkPassword(arrContent.password)): 
        return Response(json.dumps({"message":"Invalid Password"}))

    data:list[dict[str,str|int]] = [
            {"team":team} for team in arrContent.data
    ]

    _=db.table('scoreboard').delete().not_.in_("team",arrContent.data).execute()
    _=db.table('scoreboard').upsert(data,on_conflict="team",ignore_duplicates=True).execute()
    
    return Response(json.dumps({"message":"Success"}))


@ScoreboardRouter.post("/scoreboard/game/score")
async def updateScores(arrContent:gameScoreUpdate)->Response:
    """Updates the scores of all teams for an entire game"""
    

    if (not checkPassword(arrContent.password)):
        return Response(json.dumps({"message":"Invalid Password"}))
    
    if (arrContent.game == "team"): # stops the program from overwriting the team column
        return Response(json.dumps({"message":"Can not overwrite \'team\' column"}))

    data:list[dict[str,str|int]] = [
            {"team":datap.team,arrContent.game:datap.score} for datap in arrContent.data  
    ]

    # no need to be safe with updating teams since it should never happen. Leave that to implementation on website
    _=db.table('scoreboard').upsert(data,on_conflict="team",ignore_duplicates=False).execute()

    return Response(json.dumps({"message":"Success"}))


@ScoreboardRouter.get("/scoreboard/game")
async def getGameScores():
    """Returns a dict of teams and their scores for all games"""
    
    response:Any = db.table('scoreboard').select("*").execute().data

    data:dict[str,dict[str,int]] = {}
    for row in response:

        data[row.get('team')] = {
            key:row.get(key) for i,key in enumerate(row) if i != 0
        }

    return Response(json.dumps({"message":"Success","content":data}))


@ScoreboardRouter.get("/scoreboard/status")
async def isEnabled():
    
    response:Any = db.table('status').select("status").eq("name","scoreboard_enabled").execute().data
    
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
    if (not checkPassword(boolData.password)): 
        return Response(json.dumps({"message":"Invalid Password"}))

    _=db.table('status').update({"status":boolData.data}).eq("name","scoreboard_enabled").execute()

    return Response(json.dumps({"message":"Success"}))


@ScoreboardRouter.get("/scoreboard/game/names")
async def getGameNames():

    response:Any = db.table("scoreboard").select("*").limit(1).execute()
    
    data = ["overall"]
    
    if response.data:
        data = list(response.data[0].keys())[1:]
    else:
        return Response(json.dumps({"message":"No content in database","content":data}))
    return Response(json.dumps({"message":"Success","content":data}))
