# First priority for cleaning up and optimizing. With the amount of calls that this does, we'd rate limit after only half the day
from fastapi import APIRouter, HTTPException, Response, Request
from typing import Any
from pydantic import BaseModel
from .auth import db, PasswordSubmission, checkPassword
import json

# get the new auth key
ScoreboardRouter = APIRouter()


# Todo add new routes
