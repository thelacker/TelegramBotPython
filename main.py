# -*- coding: utf-8 -*-

from GroupHelperClass import GroupHelper
import json
import time
import pickle


def main():
    bot = GroupHelper(token=json.load(open("bot.bot"))['token'])

    try:
        chatData = open('chatdata.txt', 'rb')
        bot.ChatsIDs.update(pickle.load(chatData))
        chatData.close()
    except Exception as e:
            print(e)

    while True:
        bot.check_update()
        time.sleep(1)


if __name__ == '__main__':
    main()