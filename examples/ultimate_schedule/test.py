from glob import glob
import os
import sys
import threading
import time

sys.path.append(os.path.join(sys.path[0], '../../'))
import schedule
from instabot import Bot, utils



myfile = utils.file("hashtag_database.txt")
myfile.list
print( myfile.list)