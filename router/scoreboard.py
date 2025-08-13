from fastapi import APIRouter, HTTPException, Response, Request
from typing import Any
from pydantic import BaseModel
from .auth import db, PasswordSubmission, checkPassword
from google.cloud import firestore
import json


ScoreboardRouter = APIRouter()
@ScoreboardRouter.put("/scoreboard")
def getBoard():
    try:
        docRef = db.collection('scoreboard').document('Games')
        docRef2 = db.collection('scoreboard').document('teams')
        docRef3 = db.collection('page').document('status')

        enabled = docRef3.get().to_dict() or {'scoreboard':False}
        enabled = enabled['scoreboard']

        if enabled:
            games = docRef.get().to_dict() or {'Data':{},'Names':[],'Points':{},'Settings':{}}

            teams = docRef2.get().to_dict() or {}
        else:
            games = {'Data':{},'Names':[],'Points':{},'Settings':{}}
            teams = {}


    except Exception as e:
        return HTTPException(500,detail=f"Internal Server Error")
    return Response(json.dumps({'message':'success','games':games,'teams':teams,'enabled':enabled}), status_code=200, headers={'content-type':'application/json'})




@ScoreboardRouter.post("/scoreboard")
async def setBoard(request:Request, passwordSubmission:PasswordSubmission):


    if not checkPassword(passwordSubmission.password):
        return HTTPException(401, detail=f"Access Denied")
    # That basemodel crap wasn't working here so I just decided to go with grabbing the raw request data
    req = (await request.json())
    try:
        docRef = db.collection('scoreboard').document('Games')
        docRef2 = db.collection('scoreboard').document('teams')
        docRef3 = db.collection('page').document('status')

        batch = db.batch()
        batch.set(docRef,req['games'])
        batch.set(docRef2,req['teams'])
        batch.set(docRef3, {'scoreboard':req['enabled']})
        batch.commit()

    except KeyError as e:
        return HTTPException(422, detail="Missing fields")
    except Exception as e:
        return HTTPException(500, detail=f"Internal Server Error")
    
    return Response(status_code=200,content="Success",headers={'content-type':'text/plain'})

@ScoreboardRouter.post("/status")
def getStatus():
    try:
        docRef = db.collection('page').document('status')

        enabled = docRef.get().to_dict() or {'scoreboard':False}

    except Exception as e:
        return HTTPException(500,detail=f"Internal Server Error")
    
    return Response(status_code=200, content=json.dumps(enabled),headers={'Content-Type':'application/json'})