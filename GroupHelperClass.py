# -*- coding: utf-8 -*-
import telegram
import Commands
import random
import pickle
import threading
import frases as frz


class GroupHelper:

    def __init__(self, token, last_update_id=None):
        self.last_update_id = last_update_id
        self.Reply_Markup = telegram.ReplyKeyboardHide()
        self.Bot = telegram.Bot(token)
        self.ChatsIDs = {}
        self.chat_id = 0 # None

    def listener(self, interruption=1):
    #    Вернуть поток, который бы делал check_update с промежутком interruption
    #    А check_update удалить
        thread_to_return = threading.Timer(interruption, self.check_update())
        return thread_to_return

    @staticmethod
    def parse_message(message):
        # добавить корректную обработку kwargs
        result = []
        command = ""
        args = []

        for word in message.split():
            if word.startswith('/'):
                if command:
                    result.append((command, args[:]))
                    command = word
                    args = []
                else:
                    command = word
            else:
                args.append(word)
        else:
            result.append((command, args[:]))

        return result


    def check_update(self):
        try:
            for update in self.Bot.getUpdates(offset=self.last_update_id+1 if self.last_update_id else None):
                update.message.text = update.message.text
                self.chat_id = update.message.chat_id
                if self.chat_id in self.ChatsIDs.keys():
                    self.conversation_status(update)
                else:
                    self.ChatsIDs[self.chat_id] = [update.message['chat']['first_name'], None]
                    self.conversation_status(update)
                self.last_update_id = update.update_id
                chatData = open('chatdata.txt', 'wb')
                pickle.dump(self.ChatsIDs, chatData)
                chatData.close()
        except Exception as e:
            self.Reply_Markup = telegram.ReplyKeyboardHide()
            print(e)
            self.Bot.sendMessage(text="К сожалению, произошла ошибка.Мы ее исправим.",
                                             chat_id=self.chat_id)
            self.ChatsIDs[self.chat_id][1] = None
            self.last_update_id = update.update_id
            #   TODO:
            # Отслыать ошибки только мне в сообщении с 
            # указанием айди и самой ошибкой

    def conversation_status(self, update):
        self.Bot.sendChatAction(chat_id=self.chat_id, action=telegram.ChatAction.TYPING)
        if self.ChatsIDs[self.chat_id][1] == None:
            for (command, args) in self.parse_message(update.message.text):
                    self.last_update_id = update.update_id
                    debug = Commands.commands
                    Commands.commands[command](self, *args)
        else:
            Commands.commands[Commands.statuses[self.ChatsIDs[self.chat_id][1][0]]](self, update.message.text)

    def send_message(self, message, to_all=False):
        if to_all:
            pass
        else:
            self.Bot.sendMessage(text=message, chat_id=self.chat_id, reply_markup=self.Reply_Markup)
    
    #def send_document
    #def send_photo
    #def send_video
    #def send_audio


# -------------------------------------------------------------------------------------------------------------------- #

    @Commands.define_command(help_text="""Вызывает подсказку""")
    def help(self, *args):
        result = ""
        help_text_template = "{command} - {description}\n"

        for arg in args:
            command = '/' + arg
            result += help_text_template.format(command=command, description=Commands.commands[command].help_text)

        if not result:
            for command in Commands.commands:
                result += help_text_template.format(command=command, description=Commands.commands[command].help_text)

        self.send_message(result)

        return result


    @Commands.define_command(help_text="Приветствие бота")
    def start(self):
        result = self.ChatsIDs[self.chat_id][0]+ ', '+ str(random.choice(frz.HelloFrase)) + str(frz.IntroFrase)
        self.send_message(result)
        return result

    
    """
            TODO:
            Придумать/допилить нормальный метод test
            
             
    @Commands.define_command(help_text="TEST METHOD HELP")
    def test(self, attr_1, attr_2):
        result = "TEST METHOD RETURN(" + attr_1 + attr_2 + ")"
        self.send_message(result)
        return result
    """

    @Commands.define_command(special_name="")
    def _empty(self, *args):
        result = ' '.join(args) + "\n\nК сожалению, этого я не понимаю :("
        self.send_message(result)
        return result

    @Commands.define_command(help_text="Присылает список группы")
    def grouplist(self, message=''):
        if self.ChatsIDs[self.chat_id][1] == None:
            custom_keyboard = [[ "Текст"],["PDF"]]
            self.Reply_Markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            result = 'В каком виде прислать список группы?'
            self.ChatsIDs[self.chat_id][1] = 'l_0'

        elif self.ChatsIDs[self.chat_id][1] == 'l_0':
            self.Reply_Markup = telegram.ReplyKeyboardHide()
            if message == 'Текст':
                result = frz.GroupList
                self.ChatsIDs[self.chat_id][1] = None
            elif message == 'PDF':
                self.Bot.sendChatAction(chat_id=self.chat_id, action=telegram.ChatAction.UPLOAD_DOCUMENT)
                self.Bot.sendDocument(self.chat_id, document=open('GroupList.pdf', 'rb').encoding('utf-8'), reply_markup=self.Reply_Markup)
                self.ChatsIDs[self.chat_id][1] = None
            else:
                result = "Прошу прощения, я Вас не понял"
        self.send_message(result)
        return result

    @Commands.define_command(help_text="Удаляет Вас из базы данных бота")
    def clear(self):
        if self.chat_id in self.ChatsIDs.keys():
            self.ChatsIDs.__delitem__(self.chat_id)
            self.Reply_Markup = telegram.ReplyKeyboardHide()
            result = 'Ваша история общения удалена'
        else:
            result = 'Вас и так не было в базе :)'
        self.send_message(result)
        return result

    @Commands.define_command(help_text="""Просто отправляет "Ты тут?" всем пользователям""")
    def spam(self):
        for chatid in self.ChatsIDs:
            result = 'Ты тут, ' + self.ChatsIDs[self.chat_id][0] + '?'
            self.send_message(result)
        return result

    @Commands.define_command(help_text="""Вызывает подсказку""")
    def greeting(self, message):
        self.send_message("HUITA")
        if self.ChatsIDs[self.chat_id][1] == 'g':
            custom_keyboard = [[ "Да", "Нет" ]]
            self.Reply_Markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            self.send_message("Хотите познакомиться?")
            self.Reply_Markup = telegram.ReplyKeyboardHide()
            self.ChatsIDs[self.chat_id][1] = 'g_0'

        elif self.ChatsIDs[self.chat_id][1] == 'g_0':
            self.Reply_Markup = telegram.ReplyKeyboardHide()
            if message == 'Да':
                self.send_message("Как Вас зовут?")
                self.ChatsIDs[self.chat_id][1] = 'g_1'
            elif message == 'Нет':
                self.send_message("Ваше право! " + self.ChatsIDs[self.chat_id][0])
                self.ChatsIDs[self.chat_id][1] = None
            else:
                self.send_message("Прошу прощения, я Вас не понял")

        elif self.ChatsIDs[self.chat_id][1] == 'g_1':
            self.ChatsIDs[self.chat_id][0] = message
            self.send_message("Очень приятно, " + message + "! А меня можете называть Бот")
            self.ChatsIDs[self.chat_id][1] = None