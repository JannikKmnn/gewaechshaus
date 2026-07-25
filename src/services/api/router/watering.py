import asyncio

from fastapi import APIRouter, Request, HTTPException
import os

try:
    from src.services.api.handlers import windows
except ModuleNotFoundError:
    # happens on local dev
    pass

router = APIRouter()
