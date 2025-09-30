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
from el import terminal
from el.observable import Observable, filters

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

    def __init__(self):
        # flag set to quit application
        self.exited = Observable[bool](False)

        # db needs to be setup first, so that everything else can use it
        self.db = CompassDB(self)
        self.web = CompassWeb(self)
        self.auth = CompassAuth(self)
        self.bot = DiscordBot(self)
        self.sleep = SleepTracking(self)
        self.accountability = AccountabilityManager(self)
        
        # setting up the parts of the application
        self.habitica = CompassHabitica(self)
        self.cli = CompassCLI(self)

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

            self.sleep.run(),
            self.habitica.run(),
        )

        _log.info("Exiting.")


async def main() -> int:
    await _term.setup_async_stream()
    _term.print("== compass-app startup ==")

    app = CompassApp()
    await app.run()
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
