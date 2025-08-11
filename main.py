from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic import validate_email
from fastapi.responses import HTMLResponse

from router.email import EmailRouter
from router.misc import getAndorHTML
app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    htmlContent = f"""
    <html>
        <body>
            <p style='font-family: monospace;text-indent: initial;font-size: initial;tab-size: 4;border-spacing: 0px;overflow:wrap;'>{"It seems you've reached our API page! It's all used on the backend, so there won't be much here (other than maybe a few easter eggs), though if you want to peek around that's just fine by me."}</p>
        </body>
    </html>
    """
    return HTMLResponse(content=htmlContent, status_code=200)

app.include_router(EmailRouter)



# Code for displaying a quote from my favourite TV show whenever a user is browsing normally

@app.exception_handler(404)
async def Handler_404(request, exc: HTTPException):
    return HTMLResponse(content=getAndorHTML(), status_code=404)

@app.exception_handler(405)
async def Handler_405(request, exc: HTTPException):
    return HTMLResponse(content=getAndorHTML(), status_code=405)

