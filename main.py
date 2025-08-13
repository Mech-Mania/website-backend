import json
from typing import Union
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

# routers
from router.email import EmailRouter, limiter
from router.visits import VisitsRouter
from router.scoreboard import ScoreboardRouter
from fastapi.middleware.cors import CORSMiddleware
from router.auth import checkPassword, PasswordSubmission
from router.misc import getAndorHTML
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
app = FastAPI()


app.state.limiter = limiter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://www.mechmania.ca/*", "https://mechmania.ca/*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def readRoot():
    htmlContent = f"""
    <html>
        <body>
            <p style='font-family: monospace;text-indent: initial;font-size: initial;tab-size: 4;border-spacing: 0px;overflow:wrap;'>{"It seems you've reached our API page! It's all used on the backend, so there won't be much here (other than maybe a few easter eggs), though if you want to peek around that's just fine by me."}</p>
        </body>
    </html>
    """
    return HTMLResponse(content=htmlContent, status_code=200)


@app.post("/password")
def verifyPassword(passwordSubmission:PasswordSubmission):
    result = checkPassword(passwordSubmission.password)
    return Response(status_code=200 if result else 401,content=json.dumps({'result':result}), headers={'content-type':'application/json'})

# include routers
#############################################################################################
app.include_router(ScoreboardRouter)
app.include_router(EmailRouter)
app.include_router(VisitsRouter)
# Code for displaying a quote from my favourite TV show (Andor) whenever a user is browsing normally


@app.exception_handler(405)
async def Handler405(request, exc: HTTPException):
    return HTMLResponse(content=getAndorHTML(), status_code=405)

@app.exception_handler(RateLimitExceeded)
async def HandlerRateLimit(request, exc):
    return Response(status_code=200,content=json.dumps({'status':429,'message':'Too many requests'}))
