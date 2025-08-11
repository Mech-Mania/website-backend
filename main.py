from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import validate_email

from router.email import EmailRouter


app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

@app.get("/")
def read_root():
    return "It seems you've reached our API page! It's all used on the backend, so there won't be much here, though if you want to peek around that's just fine by me."


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


app.include_router(EmailRouter)
