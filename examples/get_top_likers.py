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


parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-u', type=str, help="username")
parser.add_argument('-p', type=str, help="password")
parser.add_argument('-proxy', type=str, help="proxy")
parser.add_argument('filename', type=str, help="filename")
parser.add_argument('users', type=str, nargs='+', help='users')
args = parser.parse_args()

bot = Bot()
bot.login(username=args.u, password=args.p,
          proxy=args.proxy)


f = utils.file(args.filename)

#python get_top_likers.py likers.txt mister.da.vinci
numberOfMedia = 10
for username in args.users:
    medias = bot.get_last_user_medias(username, numberOfMedia)
    likersUserName = []
    if len(medias):
        for media in medias:
            likers = bot.get_media_likers(media)
            for liker in likers:
                likersUserName.append(liker) #bot.get_username_from_user_id(liker)

        topLikers = []
        topLikerDic = {i: likersUserName.count(i) for i in likersUserName}
        numberOfLikes = numberOfMedia
        while(numberOfLikes > 1):
            for liker in topLikerDic.keys():
                if(topLikerDic[liker] >= numberOfLikes):
                    completeLiker = liker + ":" + str(topLikerDic[liker])
                    if(completeLiker not in topLikers):
                        topLikers.append(completeLiker)
            numberOfLikes = numberOfLikes - 1
            if(len(topLikers) > 10):
                break
        usernameList = []
        for liker in topLikers:
            usernameList.append(bot.get_username_from_user_id(liker.split(':')[0]))
        f.save_list(usernameList)
#         for liker in tqdm(likers):
#             bot.like_user(liker, amount=2)
#             bot.follow(liker)
