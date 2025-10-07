"""
The Compass Community © 2025 - now
www.thecompass.diy
07.09.25, 17:03

Compass Bot/Application
"""

# configuring the terminal for modules to use logging
from el import terminal
_term = terminal.setup_simple_terminal()

import os
import asyncio
import logging
from pathlib import Path
from tap import tapify
from el import terminal
from el.observable import Observable, filters
from el.path_utils import abspath

from compass_app.config import Config, Settings
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
        data: Path = Path("data"),
        config: Path = Path("data/config.json"),
        settings: Path = Path("data/config.json"),
        db: Path = Path("data/compass.db"),
    ):
        """
        Compass Community application server. This hosts the Compass community
        discord bot and other possibly integrations like webapp or third-party
        systems.

        Static configuration is supplied via a single JSON config file,
        modifiable settings are loaded and stored in a separate JSON file.

        Parameters
        ----------
        data : Path, optional
            A folder where user generated data files are stored.
        config : Path, optional
            Static configuration JSON file. Must be at least readable.
        settings : Path, optional
            A JSON file for modifiable settings. Must be readable and writable.
        db : str, optional
            Path to the sqlite database file for storing relational user data.
        """

        # flag set to quit application
        self.exited = Observable[bool](False)

        # save expanded paths
        self.data_path = abspath(data)
        self._config_path = abspath(config)
        self._settings_path = abspath(settings)
        self.db_path = abspath(db)

        # load static config and dynamic settings file
        self.config = Config.model_load_from_disk(self._config_path)
        self.settings = Settings.model_load_from_disk(self._settings_path, create_if_missing=True)

        # core subsystems
        # db needs to be setup first, so that everything else can use it
        self.db = CompassDB(self)
        self.web = CompassWeb(self)
        self.auth = CompassAuth(self)
        self.bot = DiscordBot(self)
        self.cli = CompassCLI(self)

        # application modules
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

def entry():
    exit(asyncio.run(main()))

if __name__ == "__main__":
    entry()