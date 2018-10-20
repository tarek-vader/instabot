# -*- coding: utf-8 -*-

from glob import glob
import os
import sys
import threading
import time
import get_top_likers

sys.path.append(os.path.join(sys.path[0], '../../'))
import schedule
from instabot import Bot, utils

import config

bot = Bot(comments_file=config.COMMENTS_FILE,
          blacklist_file=config.BLACKLIST_FILE,
          whitelist_file=config.WHITELIST_FILE,
          friends_file=config.FRIENDS_FILE)
bot.login()
bot.logger.info("ULTIMATE script. Safe to run 24/7!")

topLiker_file = utils.file(config.TOPLIKER_FILE)
random_user_file = utils.file(config.USERS_FILE)
random_hashtag_file = utils.file(config.HASHTAGS_FILE)
photo_captions_file = utils.file(config.PHOTO_CAPTIONS_FILE)
posted_pic_list = utils.file(config.POSTED_PICS_FILE).list

pics = sorted([os.path.basename(x) for x in
               glob(config.PICS_PATH + "/*.jpg")])


bot.topLiker_lock = threading.Lock()
bot.follow_lock = threading.Lock()

def stats():
    while(true):
        bot.save_user_stats(bot.user_id)
        time.sleep(60*60*6)


def like_hashtags():
    bot.like_hashtag(random_hashtag_file.random().strip(), amount=700 // 24)


def like_timeline():
    bot.like_timeline(amount=300 // 24)

def like_and_follow():
    while(true):
        for user in topLiker_file.list[0:100]:
            user_id= user.strip()
            bot.follow_with_time(user_id)
            bot.like_user(user_id, amount=2, filtration=False)
            self.topLiker_lock.acquire()
            try:
                topLiker_file.remove(user)
            finally:
                self.topLiker_lock.release()
        time.sleep(60)

def collect_topLiker():
    while(true):
        for hashtag in random_hashtag_file.list:
            hastagusers = bot.get_hashtag_users(hashtag.strip())
            for user in hashtagusers[0:10]:
                topLikers = get_top_likers(user)
                bot.topLiker_lock.acquire()
                try:
                    topLiker_file.append_list(topLikers)
                finally:
                    self.topLiker_lock.release()
                while len(topLiker_file.list) > 500:
                    time.sleep(60*15) # 15 min
                    
                

def like_followers_from_random_user_file():
    bot.like_followers(random_user_file.random().strip(), nlikes=3)


def follow_followers():
    bot.follow_followers(random_user_file.random().strip(), nfollows=config.NUMBER_OF_FOLLOWERS_TO_FOLLOW)


def comment_medias():
    bot.comment_medias(bot.get_timeline_medias())


def unfollow_non_followers():
    while(true):
        bot.unfollow_non_followers_24(n_to_unfollows=config.NUMBER_OF_NON_FOLLOWERS_TO_UNFOLLOW)
        time.sleep(60)


def follow_users_from_hastag_file():
    bot.follow_users(bot.get_hashtag_users(random_hashtag_file.random().strip()))


def comment_hashtag():
    hashtag = random_hashtag_file.random().strip()
    bot.logger.info("Commenting on hashtag: " + hashtag)
    bot.comment_hashtag(hashtag)


def upload_pictures():  # Automatically post a pic in 'pics' folder
    try:
        for pic in pics:
            if pic in posted_pic_list:
                continue

            caption = photo_captions_file.random()
            full_caption = caption + "\n" + config.FOLLOW_MESSAGE
            bot.logger.info("Uploading pic with caption: " + caption)
            bot.upload_photo(config.PICS_PATH + pic, caption=full_caption)
            if bot.api.last_response.status_code != 200:
                bot.logger.error("Something went wrong, read the following ->\n")
                bot.logger.error(bot.api.last_response)
                break

            if pic not in posted_pic_list:
                # After posting a pic, comment it with all the hashtags specified
                # In config.PICS_HASHTAGS
                posted_pic_list.append(pic)
                with open('pics.txt', 'a') as f:
                    f.write(pic + "\n")
                bot.logger.info("Succesfully uploaded: " + pic)
                bot.logger.info("Commenting uploaded photo with hashtags...")
                medias = bot.get_your_medias()
                last_photo = medias[0]  # Get the last photo posted
                bot.comment(last_photo, config.PICS_HASHTAGS)
                break
    except Exception as e:
        bot.logger.error("Couldn't upload pic")
        bot.logger.error(str(e))


def put_non_followers_on_blacklist():  # put non followers on blacklist
    try:
        bot.logger.info("Creating non-followers list")
        followings = set(bot.following)
        followers = set(bot.followers)
        friends = bot.friends_file.set  # same whitelist (just user ids)
        non_followers = followings - followers - friends
        for user_id in non_followers:
            bot.blacklist_file.append(user_id, allow_duplicates=False)
        bot.logger.info("Done.")
    except Exception as e:
        bot.logger.error("Couldn't update blacklist")
        bot.logger.error(str(e))


like_follow_thread = threading.Thread(name='like_and_follow', target=like_and_follow)
topLiker_thread =  threading.Thread(name='get_top_liker', target=collect_topLiker)
unfollow_thread = threading.Thread(name='unfollow_non_followers', target=unfollow_non_followers)
like_hashtags_thread = threading.Thread(name='like_hashtags', target=like_hashtags)
stats_thread = threading.Thread(name='stats', target=stats)


like_follow_thread.start()
unfollow_thread.start()
#like_hashtags_thread.start()
stats_thread.start()


while True:
    schedule.run_pending()
    time.sleep(1)
