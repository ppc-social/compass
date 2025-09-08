"""
The Compass Community © 2025 - now
www.thecompass.diy
07.09.25, 17:41

Web API subsystem
"""

import os
import httpx
import uvicorn
import logging
import asyncio
import typing

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlencode
from el.observable import filters
from el.async_tools import synchronize

from compass_app.config import CONFIG

if typing.TYPE_CHECKING:
    from compass_app.main import CompassApp


_log = logging.getLogger(__name__)


class CompassWeb(FastAPI):
    
    def __init__(self, app: "CompassApp"):
        super().__init__()
        self._app = app

        @self.get("/")
        async def homepage():
            return "Welcome to the compass app..."
    
    async def run(self) -> None:
        config = uvicorn.Config(
            self, 
            host=CONFIG.WEB_HOST,
            port=CONFIG.WEB_PORT, 
            log_level="info"
        )
        server = uvicorn.Server(config)

        def end_uvicorn():
            server.should_exit = True
        self._app.exited >> filters.call_if_true(end_uvicorn)
        
        await server.serve()



