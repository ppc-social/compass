"""
The Compass Community © 2025 - now
www.thecompass.diy
07.09.25, 20:37

Sleep tracking subsystem
"""

import typing

if typing.TYPE_CHECKING:
    from compass_app.main import CompassApp


class SleepTracking():
    def __init__(self, app: "CompassApp"):
        self._app = ...

    async def run(self) -> None:
        ...
