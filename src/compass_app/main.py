"""
The Compass Community © 2025 - now
www.thecompass.diy
07.09.25, 17:03

Compass Bot/Application
"""

# configuring the terminal for modules to use logging
from el import terminal
_term = terminal.setup_simple_terminal()

import asyncio
import logging
from pathlib import Path
from tap import tapify
from el import terminal
from el.observable import Observable, filters

from compass_app.config import CONFIG
from compass_app.settings import Settings
from compass_app.dcbot import DiscordBot
from compass_app.database import CompassDB
from compass_app.webserver import CompassWeb
from compass_app.auth import CompassAuth
from compass_app.cli import CompassCLI
from compass_app.sleep_tracking import SleepTracking
from compass_app.habitica import CompassHabitica
from compass_app.accountability.manager import AccountabilityManager


_log = logging.getLogger(__name__)


class CompassApp:

    def __init__(
        self,
        #data: Path,
        #config: Path | None = None,
        #host: str = "0.0.0.0",
        #port: int = 8080,
    ):
        """
        Compass Community application server. This hosts the Compass community
        discord bot and other possibly integrations like webapp or third-party
        systems.

        Static configuration is supplied via environment variables, modifiable
        settings are loaded from the specified settings file.
        
        """

        # flag set to quit application
        self.exited = Observable[bool](False)

        # load dynamic settings file
        try:
            self.settings = Settings.model_load_from_disk(CONFIG.SETTINGS_FILE)
        except:
            # move erroneous file away if it exists
            if CONFIG.SETTINGS_FILE.is_file():
                CONFIG.SETTINGS_FILE.rename(CONFIG.SETTINGS_FILE.with_name(CONFIG.SETTINGS_FILE.name + ".error.bak"))
            # create new default config file
            self.settings = Settings()
            self.settings.model_save_to_disk_as(CONFIG.SETTINGS_FILE)
            

        # db needs to be setup first, so that everything else can use it
        self.db = CompassDB(self)
        self.web = CompassWeb(self)
        self.auth = CompassAuth(self)
        self.bot = DiscordBot(self)
        self.cli = CompassCLI(self)

        self.accountability = AccountabilityManager(self)
        self.sleep = SleepTracking(self)
        self.habitica = CompassHabitica(self)

        # in the future we may
        # self.mize = Instance(namespace = app.thecompass.diy)

    async def run(self):
        self.exited >> filters.call_if_true(_term.exit)
        terminal.set_root_log_level("INFO")
        logging.getLogger(__package__).setLevel("DEBUG")

        # run the application
        await asyncio.gather(
            self.db.run(),
            self.web.run(),
            self.auth.run(),
            self.bot.run(),
            self.cli.run(),

            self.accountability.run(),
            self.sleep.run(),
            self.habitica.run(),
        )

        _log.info("Exiting.")


async def main() -> int:
    await _term.setup_async_stream()
    app = tapify(CompassApp)

    _term.print("== compass-app startup ==")
    await app.run()
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
