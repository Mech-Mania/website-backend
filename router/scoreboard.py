from fastapi import APIRouter, Response
from pydantic import BaseModel
from router.auth import db, PasswordSubmission, checkPassword
import json

ScoreboardRouter = APIRouter()



class ArrDataReq(BaseModel):
    data:list[str]
    password:str = ""
    
class teamWithScore(BaseModel):
    team:str
    score:int = 0

class gameScoreUpdate(BaseModel):
    data:list[teamWithScore] # team, score
    password:str = ""
    game:str = ""


@ScoreboardRouter.post("/scoreboard/team")
async def updateTeams(arrContent:ArrDataReq):
    """Updates teams so that the teams list reflects the given list"""
    
    if (not checkPassword(arrContent.password)): 
        return Response(json.dumps({"message":"Invalid Password"}))

    data:list[dict[str,str|int]] = [
            {"team":team} for team in arrContent.data
    ]

    _=db.table('scoreboard').delete().not_.in_("team",arrContent.data).execute()
    _=db.table('scoreboard').upsert(data,on_conflict="team",ignore_duplicates=True).execute()
    
    return Response(json.dumps({"message":"Success"}))


@ScoreboardRouter.post("/scoreboard/team/score")
async def updateScores(arrContent:gameScoreUpdate):
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
