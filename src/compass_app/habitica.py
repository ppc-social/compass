"""
The Compass Community © 2025 - now
www.thecompass.diy
07.09.25, 20:37

Habitica integration
"""

import typing

if typing.TYPE_CHECKING:
    from compass_app.main import CompassApp


class CompassHabitica():
    def __init__(self, app: "CompassApp"):
        self._app = app

    async def run(self) -> None:
        ...
    


