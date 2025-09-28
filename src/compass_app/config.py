"""
The Compass Community © 2025 - now
www.thecompass.diy
08.09.25, 08:50

Centralized place to define and load configuration
"""

import os
import pydantic

from dotenv import load_dotenv
from pathlib import Path

# load environment for other modules to use
load_dotenv(dotenv_path=Path(".env.development"), override=True)


class Config(pydantic.BaseModel):
    DISCORD_BOT_TOKEN: str
    DISCORD_GUILD_ID: int
    DISCORD_CLIENT_ID: str
    DISCORD_CLIENT_SECRET: str
    DISCORD_REDIRECT_URL: str
    WEB_HOST: str
    WEB_PORT: int
    DB_URL: str
    DISABLE_DB_IN_SHELL: bool

    ACCOUNTABILITY_CHANNEL_ID: int


CONFIG = Config(
    DISCORD_BOT_TOKEN           = os.getenv("DISCORD_BOT_TOKEN"),
    DISCORD_GUILD_ID            = os.getenv("DISCORD_GUILD_ID"),
    DISCORD_CLIENT_ID           = os.getenv("DISCORD_CLIENT_ID"),
    DISCORD_CLIENT_SECRET       = os.getenv("DISCORD_CLIENT_SECRET"),
    DISCORD_REDIRECT_URL        = os.getenv("DISCORD_REDIRECT_URL"),
    WEB_HOST                    = os.getenv("WEB_HOST"),
    WEB_PORT                    = os.getenv("WEB_PORT"),
    DB_URL                      = os.getenv("DB_URL"),
    DISABLE_DB_IN_SHELL         = os.getenv("DISABLE_DB_IN_SHELL"),
    
    ACCOUNTABILITY_CHANNEL_ID   = os.getenv("ACCOUNTABILITY_CHANNEL_ID"),
)