"""
The Compass Community © 2025 - now
www.thecompass.diy
08.09.25, 08:50

Centralized place to define and load configuration
"""

import os
from pydantic import Field
from datetime import time
from el.datastore import SavableModel
from el.terminal import LogLevel


class Config(SavableModel):
    model_config = {
        "savable_default_dump_options": {
            "indent": 4
        },
        # config contains static, immutable settings, this must not be modifiable
        "frozen": True,
    }

    discord_bot_token: str
    discord_guild_id: int
    discord_client_id: str
    discord_client_secret: str
    discord_redirect_url: str
    
    web_host: str
    web_port: int
    
    accountability_channel_id: int


class Settings(SavableModel):
    model_config = {
        "savable_default_dump_options": {
            "indent": 4
        }
    }

    sqlalchemy_log_level: LogLevel = "WARNING"

    # settings for automated accountability period creation/ending
    accountability_period_automation: bool = False
    accountability_period_weekday: int = 0
    accountability_period_time: time = Field(default_factory=time)
    # settings for automated accountability period scoring
    accountability_scoring_automation: bool = False
    accountability_scoring_weekday: int = 0
    accountability_scoring_time: time = Field(default_factory=time)
