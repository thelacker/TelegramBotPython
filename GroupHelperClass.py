# -*- coding: utf-8 -*-
import telegram
import Commands
import random
import pickle
import time
import frases as frz


class GroupHelper:

    def __init__(self, token, last_update_id=None):
        self.last_update_id = last_update_id
        self.Reply_Markup = telegram.ReplyKeyboardHide()
        self.Bot = telegram.Bot(token)
        self.ChatsIDs = {}
        self.chat_id = 0 # None

#   def listener(self, interruption=1):
#   #Вернуть поток, который бы делал check_update с промежутком interruption
#   #А check_update удалить
#        pass

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

    # Проверка на новые сообщения
    def check_update(self):
        try:
            for update in self.Bot.getUpdates(offset=self.last_update_id+1 if self.last_update_id else None):\

                # Обработка символов
                update.message.text = unicode(update.message.text).encode('utf-8').lower()

                # Ищем и запоминаем пользователя
                self.chat_id = update.message.chat_id
                if self.chat_id in self.ChatsIDs.keys():
                    self.conversation_status(update)
                else:
                    self.ChatsIDs[self.chat_id] = [None, 'g']
                    self.conversation_status(update)

                # Ставим отметку об обработке
                self.last_update_id = update.update_id

                # Записываем информацию о юзере в файл
                chatData = open('chatdata.txt', 'w')
                pickle.dump(self.ChatsIDs, chatData)
                chatData.close()
                

        except Exception as e:

            # Убираем клавиатуры
            self.Reply_Markup = telegram.ReplyKeyboardHide()
            
            print(e)
            
            # Отсылаем уведомление админу и пользователю об ошибке
            self.Bot.sendMessage(text = str(e), chat_id=25556417)
            self.Bot.sendMessage(text="К сожалению, произошла ошибка. Бот работает в режими БЭТА. Это значит, что мы ловим все ошибки, в том числе и эту. Мы ее исправим. А пока - простите :(",
                                             chat_id=self.chat_id)
            
            # Сбрасываем стадию разговора
            self.ChatsIDs[self.chat_id][1] = None
            try:
                self.last_update_id = update.update_id
            except Exception as e:
                print (e)

    # Проверка текущего состояния разговора
    def conversation_status(self, update):
        self.Bot.sendChatAction(chat_id=self.chat_id, action=telegram.ChatAction.TYPING)

        # Сброс стадии разговора
        if update.message.text == "\\":
            self.Reply_Markup = telegram.ReplyKeyboardHide()
            self.send_message("Данные о разговоре сброшены")
            self.ChatsIDs[self.chat_id][1] = None

        # Обработка команд
        elif self.ChatsIDs[self.chat_id][1] != None or update.message.text[0] == "/":          
            
            # Разговор не ведется
            if self.ChatsIDs[self.chat_id][1] == None:
                for (command, args) in self.parse_message(update.message.text):
                        self.last_update_id = update.update_id
                        Commands.commands[command](self, *args)
            
            # Разговор ведется
            else:
                Commands.commands[Commands.statuses[self.ChatsIDs[self.chat_id][1][0]]](self, update.message.text)
        
        # Не команда
        else:
            self.not_a_command(update)

    def send_message(self, message, to_all=False):
        if to_all:
            pass
        else:
            self.Bot.sendMessage(text=message, chat_id=self.chat_id, reply_markup=self.Reply_Markup)
    
    def not_a_command(self, update):
        message = update.message.text
        if message == 'как дела?' or message == 'как ты?' or message == 'как делишки?':
            self.send_message(random.choice(frz.HowAreYouFrases))
        elif 'почему' in message:
            self.send_message(random.choice(frz.WhyFrases))
            time.sleep(5)
            self.send_message('Шутить я не умею :(')
        elif "?" in message:
            self.send_message('Я чувствую вопрос. Но, к сожалению, не могу его распознать ' + telegram.Emoji.FACE_SCREAMING_IN_FEAR)

    
    #def send_document
    #def send_photo
    #def send_video
    #def send_audio


# -------------------------------------------------------------------------------------------------------------------- #
    # Вывод помощи
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

    # Вывод приветствия
    @Commands.define_command(help_text="Приветствие бота")
    def start(self):
        result = self.ChatsIDs[self.chat_id][0]+ ', '+ random.choice(frz.HelloFrase) + frz.IntroFrase + telegram.Emoji.SMIRKING_FACE
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

    # Сообщение пусто
    @Commands.define_command(special_name="", help_text=" ")
    def _empty(self, *args):
        result = ' '.join(args) + "\n\nК сожалению, этого я не понимаю :("
        self.send_message(result)
        return result

    # Вывод списка группы
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
            elif message == 'pdf':
                self.Bot.sendChatAction(chat_id=self.chat_id, action=telegram.ChatAction.UPLOAD_DOCUMENT)
                self.Bot.sendDocument(self.chat_id, document=open('GroupList.pdf', 'rb').encoding('utf-8'), reply_markup=self.Reply_Markup)
                self.ChatsIDs[self.chat_id][1] = None
            else:
                result = "Прошу прощения, я Вас не понял.\nВ каком виде прислать список группы?"
        self.send_message(result)
        return result

    # Удаления пользователя из базы
    @Commands.define_command(help_text="Удаляет Вас из базы данных бота")
    def clear(self):
        if chat_id in self.ChatsIDs.keys():
            self.ChatsIDs.__delitem__(self.chat_id)
            self.Reply_Markup = telegram.ReplyKeyboardHide()
            result = 'Ваша история общения удалена'
        else:
            result = 'Вас и так не было в базе :)'
        self.send_message(result)
        return result

    # Рассылка всем сообщения
    @Commands.define_command(help_text="""Просто отправляет "Ты тут?" всем пользователям""")
    def spam(self):
        for chatid in self.ChatsIDs:
            try:
                result = 'Ты тут, ' + str(self.ChatsIDs[chatid][0]) + '?'
            except Exception as e:
                print (e)
                result = "Ты тут?"
            self.Bot.sendMessage(text=result, chat_id=chatid, reply_markup=self.Reply_Markup)
        return result

    # Стандартное приветствие
    @Commands.define_command(help_text="""Вызывает подсказку""")
    def greeting(self, message):
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
                    self.send_message("Ваше право!")
                    self.ChatsIDs[self.chat_id][0] = 'Аноним'
                    self.ChatsIDs[self.chat_id][1] = None
                else:
                    self.send_message("Прошу прощения, я Вас не понял.\nХотите познакомиться?")

            elif self.ChatsIDs[self.chat_id][1] == 'g_1':
                self.ChatsIDs[self.chat_id][0] = message
                self.send_message("Очень приятно, " + message + "! А меня можете называть Бот")
                self.ChatsIDs[self.chat_id][1] = None

