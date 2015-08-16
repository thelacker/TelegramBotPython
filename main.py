# -*- coding: utf-8 -*-
import time
import telegramBot as tel
import pickle
"""
help - Краткая информация о использовании
grouplist - Прислать список группы
clear - Стереть историю переписки с сервера

"""

def main():
    t = tel.telegramBot()
    # Telegram Bot Authorization Token
    # This will be our global variable to keep the latest update_id when requesting
    # for updates. It starts with the latest update_id if available.
    try:
        t.Last_Update_ID = t.AI.getUpdates()[-1].update_id
    except IndexError:
        t.Last_Update_ID = None

    while True:
        t.listener()
        time.sleep(3)

if __name__ == '__main__':
    main()