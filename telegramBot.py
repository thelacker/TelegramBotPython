# -*- coding: utf-8 -*-
import frases as frz
import random
import logging
import telegram
import time
import pickle
import datetime

class telegramBot:

    def __init__(self, token = "131812558:AAF5R9TJsowf4-8LRxj8Z38VIZvrLEYPgFo", last_update_id = None):
        self.Token = token
        self.Last_Update_ID = last_update_id
        self.Reply_Markup = telegram.ReplyKeyboardHide()
        self.AI = telegram.Bot(self.Token)
        self.ChatsIDs = {}
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
    def listener(self, encoding = 'utf-8'):
        # Request updates from last updated_id
        for update in self.AI.getUpdates(offset=self.Last_Update_ID):
            if self.Last_Update_ID < update.update_id:
                # chat_id is required to reply any message
                chat_id = update.message.chat_id
                self.AI.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                message = update.message.text.encode(encoding)
                if (message):
                    self.Last_Update_ID = update.update_id
                    if message[0] == '/':
                        self.slashCommands(message.lower(), chat_id)
                    # Reply the message
                    else:
                        self.checkConversationStatus(chat_id, message)
                        self.responseToMessage(message.lower(), chat_id, update)
                    # Updates global offset to get the new updates

    def sendMessage(self, chat_id, message):
        self.AI.sendMessage(chat_id=chat_id, text=message, reply_markup=self.Reply_Markup)

    def slashCommands(self, message, chat_id):
        if message == '/start':
            self.sendMessage(chat_id, random.choice(frz.HelloFrase) + frz.IntroFrase + telegram.Emoji.SMIRKING_FACE)
            self.greeting(chat_id, message)
        elif message == '/help':
            self.sendMessage(chat_id,frz.HelpMessage + telegram.Emoji.KISSING_FACE)
        elif message == '/grouplist':
            self.sendGroupList(chat_id, message)
        elif message == '/reboot':
            self.reboot(chat_id,message)
        elif message == '/save':
            chatData = open('chatdata.txt', 'w')
            pickle.dump(self.ChatsIDs, chatData)
            chatData.close()
            self.sendMessage(chat_id, 'Данные сохранены')
        elif message == '/clear':
            if chat_id in self.ChatsIDs.keys():
                self.ChatsIDs.__delitem__(chat_id)
                self.Reply_Markup = telegram.ReplyKeyboardHide()
                self.sendMessage(chat_id, 'Ваша история общения удалена')
        elif message == '/spam':
            for chatid in self.ChatsIDs:
                self.sendMessage(chatid, 'Ты тут, ' + self.ChatsIDs[chatid][0] + '?')
        else:
            self.sendMessage(chat_id, 'Данная команда не определена')

    def responseToMessage(self, message, chat_id, update):
        if message == 'как дела?' or message == 'как ты?' or message == 'как делишки?':
            self.sendMessage(chat_id, random.choice(frz.HowAreYouFrases))
        elif 'почему' in message:
            self.sendMessage(chat_id, random.choice(frz.WhyFrases))
            time.sleep(3)
            self.sendMessage(chat_id, 'Шутить я не умею :(')
        elif "?" in message:
            self.sendMessage(chat_id, 'Я чувствую вопрос. Но, к сожалению, не могу его распознать ' + telegram.Emoji.FACE_SCREAMING_IN_FEAR)

    def checkConversationStatus(self, chat_id, message):
        if chat_id in self.ChatsIDs.keys():
            if self.ChatsIDs[chat_id][0][0] == '_':
                self.greeting(chat_id, message)
            elif self.ChatsIDs[chat_id][1][0] == '_':
                self.sendGroupList(chat_id, message)
            elif self.ChatsIDs[chat_id][2][0] == '_':
                self.reboot(chat_id, message)
        else:
            self.ChatsIDs[chat_id] = ['0', '0', '0']

    def sendGroupList(self, chat_id, message):
        if self.ChatsIDs[chat_id][1] == '0':
            custom_keyboard = [[ "Текст"],["PDF"]]
            self.Reply_Markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            self.sendMessage(chat_id, 'В каком виде прислать список группы?')
            self.ChatsIDs[chat_id][1] = '_0'

        elif self.ChatsIDs[chat_id][1] == '_0':
            self.Reply_Markup = telegram.ReplyKeyboardHide()
            if message == 'Текст':
                self.sendMessage(chat_id, frz.GroupList)
                self.ChatsIDs[chat_id][1] = '0'
            elif message == 'PDF':
                self.AI.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_DOCUMENT)
                time.sleep(3)
                self.AI.sendDocument(chat_id, document=open('GroupList.pdf', 'rb'), reply_markup=self.Reply_Markup)
                self.ChatsIDs[chat_id][1] = '0'
            else:
                self.sendMessage(chat_id, "Прошу прощения, я Вас не понял")

    def greeting(self, chat_id, message):
        if chat_id in self.ChatsIDs.keys():
            if self.ChatsIDs[chat_id][0] == '0':
                custom_keyboard = [[ "Да", "Нет" ]]
                self.Reply_Markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
                self.sendMessage(chat_id, "Хотите познакомиться?")
                self.ChatsIDs[chat_id][0] = '_0'

            elif self.ChatsIDs[chat_id][0] == '_0':
                self.Reply_Markup = telegram.ReplyKeyboardHide()
                if message == 'Да':
                    self.sendMessage(chat_id, "Как Вас зовут?")
                    self.ChatsIDs[chat_id][0] = '_1'
                elif message == 'Нет':
                    self.sendMessage(chat_id, "Ваше право!")
                    self.ChatsIDs[chat_id][0] = 'Аноним'
                else:
                    self.sendMessage(chat_id, "Прошу прощения, я Вас не понял")

            elif self.ChatsIDs[chat_id][0] == '_1':
                self.ChatsIDs[chat_id][0] = message
                self.sendMessage(chat_id, "Очень приятно, " + message + "! А меня можете называть Бот")
        else:
            self.ChatsIDs[chat_id] = ['0', '0', '0']
            self.greeting(chat_id,message)

    def reboot(self, chat_id, message):
        if chat_id in self.ChatsIDs.keys():
            if self.ChatsIDs[chat_id][2] == '0':
                custom_keyboard = [["Отмена"]]
                self.Reply_Markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
                self.sendMessage(chat_id, 'Введите пароль для данной операции ' + telegram.Emoji.CAT_FACE_WITH_WRY_SMILE)
                self.ChatsIDs[chat_id][2] = '_0'

            elif self.ChatsIDs[chat_id][2] == '_0':
                self.Reply_Markup = telegram.ReplyKeyboardHide()
                if message == 'admin':
                    self.sendMessage(chat_id, 'rebooting...')
                    self.AI.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.FIND_LOCATION)
                    self.ChatsIDs = {}
                    chatData = open('chatdata.txt', 'r')
                    self.ChatsIDs.update(pickle.load(chatData))
                    chatData.close()
                    self.ChatsIDs[chat_id][2] = '0'
                elif message == "Отмена":
                    self.sendMessage(chat_id, 'Видимо, мне не нужна перезагрузка ' + telegram.Emoji.AMBULANCE)
                    self.ChatsIDs[chat_id][2] = '0'
                else:
                    self.sendMessage(chat_id, "Неверный пароль!")
        else:
            self.ChatsIDs[chat_id] = ['0', '0', '0']
            self.reboot(chat_id,message)

