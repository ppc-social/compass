
import os
import sys
import uvicorn
from threading import Thread

from discord_bot import init_bot
from database import CompassDB
from webserver import CompassWeb
from auth import CompassAuth

from parts.sleep_tracker import init_sleep_tracker
from parts.habitica import CompassHabitica

from dotenv import load_dotenv
from pathlib import Path


load_dotenv(dotenv_path=Path(".env.development"), override=True)


class CompassApp:
    WEB_HOST = os.getenv("WEB_HOST")
    WEB_PORT = os.getenv("WEB_PORT", "80")

    def __init__(self):

        # db needs to be setup first, so that everything else can use it
        self.db = CompassDB(self)
        self.web = CompassWeb(self)
        self.auth = CompassAuth(self)
        self.bot = init_bot(self)

        # in the future we may
        # self.mize = Instance(namespace = app.thecompass.diy)

        # setting up the parts of the application
        self.sleep_tracker = init_sleep_tracker(self)
        self.habitica = CompassHabitica(self)
        

    def run(self):
        print("running the CompassApp", file=sys.stderr)

        # run the webserver
        web_thread = Thread(target=uvicorn.run, args=(self.web,), kwargs={"host": self.WEB_HOST, "port": int(self.WEB_PORT)})
        web_thread.start()

        # run the discord bot
        token = os.getenv("DISCORD_BOT_TOKEN")
        bot_thread = Thread(target=self.bot.run, args=(token,))
        bot_thread.start()

        # wait for all the threads
        bot_thread.join()
        web_thread.join()

if __name__ == "__main__":
    CompassApp().run()

