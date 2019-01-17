# -*- coding: utf-8 -*-

from glob import glob
import os
import random
import sys
import threading
import time


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


bot.topLiker_lock = threading.Lock()
bot.follow_lock = threading.Lock()

def stats():
    while(True):
        bot.save_user_stats(bot.user_id)
        time.sleep(60*60*24)


def like_hashtags():
    bot.like_hashtag(random_hashtag_file.random().strip(), amount=700 // 24)


def like_timeline():
    bot.like_timeline(amount=300 // 24)

def only_like():
    while(True):
        for user in topLiker_file.list[150:250]:
            while( bot.reached_limit('likes')):
                bot.console_print('likes is sleeping, limit reached ')
                time.sleep(60)
            try:
                user_id= user.strip()
                print (user_id)
                bot.like_user(user_id, amount=1, filtration=False)
                time.sleep(3)
            except Exception as e:
                bot.logger.error("error while like: " + str(e))
                break
            bot.topLiker_lock.acquire()
            try:
                topLiker_file.remove(user_id)
            finally:
                bot.topLiker_lock.release()
        time.sleep(60)

def like_and_follow():
    while(True):
        for user in topLiker_file.list[0:100]:
            while( bot.reached_limit('likes') and bot.reached_limit('follows')):
                bot.console_print('follow is sleeping, limit reached ')
                time.sleep(60)
            try:
                user_id= user.strip()
                just_followed= False
                if not bot.reached_limit('follows'):
                    just_followed = bot.follow_with_time(user_id)
                #if not bot.reached_limit('likes'):
                #    bot.like_user(user_id, amount=2, filtration=True)
            except Exception as e:
                bot.logger.error("error while follow and like: " + str(e))
                break
            bot.topLiker_lock.acquire()
            try:
                topLiker_file.remove(user_id)
            finally:
                bot.topLiker_lock.release()
        time.sleep(60)

def collect_topLiker():
    foundHashtag = False
    while(True):
        random_hashtag_file = utils.file(config.HASHTAGS_FILE)
        for hashtag in random_hashtag_file.list:
            while len(topLiker_file.list) > 2400:
                bot.console_print("collect_topLiker is sleeping, current topliker: " + str(len(topLiker_file.list)), 'yellow')
                time.sleep(60*15) # 15 min
            if( bot.last_collected_hashtag != ""):
                if(foundHashtag == False and bot.last_collected_hashtag != hashtag):
                    bot.console_print("collect topLiker: skipping hashtag: " +str(hashtag.encode('utf-8')), 'yellow')
                    continue
                elif (foundHashtag == False):
                    foundHashtag = True
                    continue
            bot.console_print("collect_topLiker collect from hashtag: " +str(hashtag.strip().encode('utf-8')), 'yellow')
            hastagusers = bot.get_hashtag_users(hashtag.strip())
            if(hastagusers != None):
                topLikers = bot.get_top_Likers(hastagusers[0:10])
                topLikers = list(set(topLikers))
                bot.topLiker_lock.acquire()
                try:
                    topLiker_file.append_list(topLikers)
                    clean_list = topLiker_file.set - bot.skipped_file.set- bot.unfollowed_file.set - bot.friends_file.set - bot.blacklist_file.set 
                    topLiker_file.save_list(clean_list)
                finally:
                    bot.topLiker_lock.release()
            bot.last_collected_hashtag = hashtag
            foundHashtag = True
        time.sleep(60) 
                

def like_followers_from_random_user_file():
    bot.like_followers(random_user_file.random().strip(), nlikes=3)


def follow_followers():
    bot.follow_followers(random_user_file.random().strip(), nfollows=config.NUMBER_OF_FOLLOWERS_TO_FOLLOW)

def unfollow_lost():
    bot.unfollow_non_followers_lost()
    
def comment_medias():
    bot.comment_medias(bot.get_timeline_medias())


            

def unfollow_non_followers():
    while(True):
        try:
            bot.unfollow_non_followers_24(n_to_unfollows=config.NUMBER_OF_NON_FOLLOWERS_TO_UNFOLLOW)
        except Exception as e:
             bot.logger.error("error while unfollow " + str(e))
        while(bot.reached_limit('unfollows')):
            time.sleep(60)
            bot.console_print('unfollow is sleeping, limit reached ')


def follow_users_from_hastag_file():
    bot.follow_users(bot.get_hashtag_users(random_hashtag_file.random().strip()))


def comment_hashtag():
    hashtag = random_hashtag_file.random().strip()
    bot.logger.info("Commenting on hashtag: " + hashtag)
    bot.comment_hashtag(hashtag)

def pictures_job():
    #time.sleep(60*2)
    time.sleep(2)
    while(True):
        upload_pictures()
        i=1
        while(i>=0):
            bot.console_print("uploading pictures will begin in " +str(i) +" hours", 'yellow')
            time.sleep(60*60)  # one hour
            i=i-1
            
        
def upload_pictures():  # Automatically post a pic in 'pics' folder
    posted_pic_list = utils.file(config.POSTED_PICS_FILE).list
    pics = sorted([os.path.basename(x) for x in
               glob(config.PICS_PATH + "/*.jpg")])

    try:
        for pic in pics:
            if pic in posted_pic_list:
                continue
            
            cap_file = config.PICS_PATH + pic.replace(".jpg", ".txt")            
            if(os.path.exists(cap_file) != True):
                bot.logger.error("caption file not found " + cap_file)
                return
            full_caption = open(cap_file , encoding="utf-8").read() 
            #caption = photo_captions_file.random()
            #full_caption = caption + "\n" + config.FOLLOW_MESSAGE
            
            bot.logger.info("Uploading pic with caption: " + str(full_caption))
            bot.upload_photo(config.PICS_PATH + pic, caption=str(full_caption))
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

unfollow_lost_thread = threading.Thread(name='unfollow_lost', target=unfollow_lost)
like_follow_thread = threading.Thread(name='like_and_follow', target=like_and_follow)
only_like_thread = threading.Thread(name='only_like', target=only_like)
topLiker_thread =  threading.Thread(name='get_top_liker', target=collect_topLiker)
unfollow_thread = threading.Thread(name='unfollow_non_followers', target=unfollow_non_followers)
like_hashtags_thread = threading.Thread(name='like_hashtags', target=like_hashtags)
stats_thread = threading.Thread(name='stats', target=stats)
pics_thread = threading.Thread(name='pictures', target=pictures_job)

#unfollow_lost_thread.start()
like_follow_thread.start()
only_like_thread.start()
unfollow_thread.start()
stats_thread.start()
#pics_thread.start()
topLiker_thread.start()

#while True:
#    schedule.run_pending()
#    time.sleep(1)
