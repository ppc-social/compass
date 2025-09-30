"""
The Compass Community © 2025 - now
www.thecompass.diy
30.09.25, 13:44

Settings that can be changed dynamically at runtime.
(in opposed to config, which is static, deployment config)
"""

from pydantic import Field
from datetime import time
from el.datastore import SavableModel

from compass_app.config import CONFIG


class Settings(SavableModel):
    model_config = {
        "savable_default_dump_options": {
            "indent": 4
        }
    }

    # settings for automated accountability period creation/ending
    accountability_period_automation: bool = False
    accountability_period_weekday: int = 0
    accountability_period_time: time = Field(default_factory=time)
    # settings for automated accountability period scoring
    accountability_scoring_automation: bool = False
    accountability_scoring_weekday: int = 0
    accountability_scoring_time: time = Field(default_factory=time)
