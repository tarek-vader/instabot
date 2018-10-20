"""
    instabot example

    Workflow:
        Like and follow users who liked the last media of input users.
""" 

import argparse
import os
import sys


from tqdm import tqdm

sys.path.append(os.path.join(sys.path[0], '../'))
from instabot import Bot, utils


def get_top_Likers(usersList):
    numberOfMedia = 10
    topLikers = []
    for username in usersList:
        f2 =utils.file(outputDir +'\\' +username+ r'.txt')
        print ("geting likers from " +username)
        medias = bot.get_last_user_medias(username, numberOfMedia)
        likersUserName = []
        if len(medias):
            for media in medias:
                likers = bot.get_media_likers(media)
                for liker in likers:
                    likersUserName.append(liker) #bot.get_username_from_user_id(liker)
                time2Sleep = random.randint(5, 15)
                print ("going to sleep " +str(time2Sleep))
                time.sleep(time2Sleep)
            topLikerDic = {liker: likersUserName.count(liker) for liker in likersUserName} # {liker, numberofLikes}
            numberOfLikes = numberOfMedia # from 10 to 1
            while(numberOfLikes > 5):
                for liker in topLikerDic.keys():
                    if(topLikerDic[liker] >= numberOfLikes):
                        completeLiker = liker + ":" + str(topLikerDic[liker])  # liker:numberofLikes
                        if(completeLiker not in topLikers):
                            topLikers.append(completeLiker)
                numberOfLikes = numberOfLikes - 1
            time2Sleep = random.randint(60, 80)
            time.sleep(time2Sleep)
    return topLikers
#         for liker in tqdm(likers):
#             bot.like_user(liker, amount=2)
#             bot.follow(liker)
