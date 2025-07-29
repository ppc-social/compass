
import os
import sys
from threading import Thread

from discord_bot import init_bot
from database import init_db
from webserver import init_web

from parts.sleep_tracker import init_sleep_tracker
from parts.habitica import CompassHabitica

class CompassApp:
    def __init__(self):
        # db needs to be setup first, so that everything else can use it
        self.db = init_db(self)
        self.web = init_web(self)
        self.bot = init_bot(self)

        # in the future we may
        # self.mize = Instance(namespace = app.thecompass.diy)

        # setting up the parts of the application
        self.sleep_tracker = init_sleep_tracker(self)
        self.habitica = CompassHabitica(self)
        

    def run(self):
        print("running the CompassApp", file=sys.stderr)

        # run the discord bot
        token = os.getenv("DISCORD_BOT_TOKEN")
        bot_thread = Thread(target=self.bot.run, args=(token,))
        bot_thread.start()

        # wait for all the threads
        bot_thread.join()

if __name__ == "__main__":
    CompassApp().run()

