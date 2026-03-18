from fastapi import APIRouter, Response
from pydantic import BaseModel
from router.auth import db, PasswordSubmission, checkPassword
import json

ScoreboardRouter = APIRouter()



class ArrDataReq(BaseModel):
    data:list[str]
    password:str = ""
    


@ScoreboardRouter.post("/scoreboard/team/update")
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

# Todo add new routes
