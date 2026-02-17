from fastapi import APIRouter, Response
# get the new auth key
ScoreboardRouter = APIRouter()
@ScoreboardRouter.get("/scoreboard")
def getEmails():
    """Uses search params (to be implemented) to """

    return Response()


# Todo add new routes
