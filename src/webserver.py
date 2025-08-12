
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from urllib.parse import urlencode

class CompassWeb(FastAPI):
    def __init__(self, app):
        super().__init__()

        @self.get("/")
        async def homepage():
            return "Welcome to the compass app..."


