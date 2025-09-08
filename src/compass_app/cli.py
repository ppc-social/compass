"""
The Compass Community © 2025 - now
www.thecompass.diy
07.09.25, 19:10

CLI command handler for administrative purposes
"""

import shlex
import logging
import typing
from el import terminal

if typing.TYPE_CHECKING:
    from compass_app.main import CompassApp

_log = logging.getLogger(__name__)
_term = terminal.get_term()


class CompassCLI:

    def __init__(self, app: "CompassApp") -> None:
        self._app = app

    async def run(self) -> None:
        line: str = ""

        # wait for command or app exit
        while (line := await _term.next_command()) is not None:
            # grab arguments
            argv = shlex.split(line)
            if len(argv) == 0:
                continue

            cmd = argv[0]
            match cmd:
                case "q" | "quit":
                    self._app.exited.value = True
                    return
                case "s" | "sync":
                    count = await self._app.bot.sync()
                    _term.print(f"Synced {count} commands to target guild.")
                case "gs" | "gsync":
                    count = await self._app.bot.sync_global()
                    _term.print(f"Synced {count} commands globally.")
