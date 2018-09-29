"""
    ULTIMATE SCRIPT

    It uses data written in files:
        * follow_followers.txt
        * follow_following.txt
        * like_hashtags.txt
        * like_users.txt
    and do the job. This bot can be run 24/7.
"""

import os
import sys
import random
sys.path.append(os.path.join(sys.path[0], '../../'))
from instabot import Bot

bot = Bot()
bot.login()

print("Current script's schedule:")
follow_followers_list = bot.read_list_from_file("username_databases.txt")
print("Going to follow followers of:", follow_followers_list)
like_hashtags_list = bot.read_list_from_file("hashtag_database.txt")
print("Going to like hashtags:", like_hashtags_list)
like_users_list = bot.read_list_from_file("username_database.txt")
print("Going to like users:", like_users_list)

tasks_list = []
ran = random.randint(40, 60)
for item in follow_followers_list:
    tasks_list.append((bot.follow_followers, {'user_id': item, 'nfollows': ran}))
ran = random.randint(40, 60)
for item in like_hashtags_list:
    tasks_list.append((bot.like_hashtag, {'hashtag': item, 'amount': ran}))
ran = random.randint(40, 60)
for item in like_users_list:
    tasks_list.append((bot.like_user, {'user_id': item, 'amount': ran}))
tasks_list.append((bot.unfollow_non_followers_24,{None}))
                      
# shuffle(tasks_list)
for func, arg in tasks_list:
    func(**arg)
