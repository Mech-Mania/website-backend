from fastapi import APIRouter, HTTPException, Response
from .auth import db, PasswordSubmission, checkPassword
from google.cloud import firestore
import datetime, json


VisitsRouter = APIRouter()
@VisitsRouter.put("/visits")
def IncrementVisits():
    try:
        docRef = db.collection('analytics').document('visits')
        transaction = db.transaction()
        @firestore.transactional
        def runTransaction(transaction,docRef):
                time = datetime.datetime.now()
                # key consists of <year><month><day>. the K at the start is so firebase accepts it
                key = f'K{"{:04d}".format(time.year)}{"{:02d}".format(time.month)}{"{:02d}".format(time.day)}'

                if not docRef:
                    #if no doc we want to set it
                    db.collection('analytics').document('visits').set({ key: 1 })
                else:
                    # if doc exists we want to see if current key exists
                    snapshot = docRef.get(transaction=transaction)
                    new_value = 1
                    try:
                        new_value = snapshot.get(key) + 1
                    except Exception as e:
                        return e
                    transaction.update(docRef, {key: new_value})

        runTransaction(transaction,docRef)
    except Exception as e:
        return Response(status_code=500)

    return Response(status_code=200)


@VisitsRouter.post("/visits")
def GetVisits(passwordSubmission:PasswordSubmission):
    """Checks password and if correct returns the visits data from Firestore"""
    
    if not checkPassword(passwordSubmission.password):
        raise HTTPException(status_code=401, detail='Password Incorrect')

    documentRef = db.collection('analytics').document('visits')

    if documentRef is None:
        raise HTTPException(status_code=500, detail='Database Error 00B. Please notify organizers@mechmania.ca.')
    visits = documentRef.get().to_dict() or {}

    return Response(status_code=200, content=json.dumps({'visits':visits}), headers={'Content-Type':'application/json'})

