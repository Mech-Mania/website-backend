import json
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
# routers
from router.email import EmailRouter, limiter
from router.scoreboard import ScoreboardRouter
from starlette.middleware.cors import CORSMiddleware
from router.auth import checkPassword, PasswordSubmission
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.mechmania.ca", "https://mechmania.ca", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.state.limiter = limiter

app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/")
def readRoot():
    htmlContent = f"""
    <html>
        <body>
            <p style='font-family: monospace;text-indent: initial;font-size: initial;tab-size: 4;border-spacing: 0px;overflow:wrap;'>{"It seems you've reached our API page! It's all used on the backend, so there won't be much here, though if you want to peek around that's just fine by me."}</p>
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


@app.exception_handler(RateLimitExceeded)
async def HandlerRateLimit(request, exc):
    return Response(status_code=429,content=json.dumps({'status':429,'message':'Too many requests'}))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
