from glob import glob
import os
import sys
import threading
import time

sys.path.append(os.path.join(sys.path[0], '../../'))
import schedule
from instabot import Bot, utils

bot = Bot()

bot.login()
bot.logger.info("ULTIMATE script. Safe to run 24/7!")
time.sleep(5)
bot.last_collected_hashtag = "xxxx"

bot.logout()