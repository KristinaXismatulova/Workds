import requests
import setting
import vk_api.vk_api, json, requests
import random
from datetime import datetime 
import pdfminer
import pdf2docx
from PIL import Image
import pytesseract
from pathlib import Path
from pdf2image import *
from vk_api.longpoll import VkLongPoll
from vk_api.longpoll import VkEventType
from vk_api.upload import VkUpload


class Bot():
    def __init__(self,token,group):
        """
        Создание конструктора для нашего бота. 
        param:: token - наш токент бота, для управления группой
                group - ид нашей группы
        """
        self.token = token
        self.group = group 
        self.url = ""
        self.vk = vk_api.vk_api.VkApi(token=self.token)

        self.longpol = VkLongPoll(self.vk,group_id=self.group) 
        self.upload = VkUpload(self.vk)
        self.vk_api = self.vk.get_api()

    def bot(self):
        """
        Главная функция, тут мы проверяем
        
        """
        for event in self.longpol.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.text in ['старт','/старт']:
                    now = datetime.now() 
                    current_time = now.strftime("%H") 
                    current_time = int(current_time)
                    if current_time > 5 and current_time < 9:
                        message = "Доброе утро, я Робикс, бот, преобразующий pdf в word. Хотите узнать список команд?\nЕсли да,то введите '.команды' где . обязательна!"
                    elif current_time >=9 and current_time < 18:
                        message = "Добрый день, я Робикс, бот, преобразующий pdf в word. Хотите узнать список команд?\nЕсли да,то введите '.команды' где . обязательна!"
                    elif current_time >=18 and current_time < 23:
                        message = "Добрый вечер, я Робикс, бот, преобразующий pdf в word. Хотите узнать список команд?\nЕсли да,то введите '.команды' где . обязательна!"
                    else: message = "Доброй ночи, я Робикс, бот, преобразующий pdf в word. Хотите узнать список команд?\nЕсли да,то введите '.команды' где . обязательна!"
                    self.send_message(event,message)
                elif event.text == ".команды":
                    self.send_message(event,"Данный раздел пока что не работает")
                elif event.text == ".переделать":
                    self.send_message(event,"Хорошо, отправьте пожалуйста файл формата pdf сюда:")
                    for event in self.longpol.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.attachments is not None:
                            if len(event.attachments) != 0:
                                self.cheker_attachments(event)
                                for event in self.longpol.listen():
                                    if event.type == VkEventType.MESSAGE_NEW:
                                        answer = event.text
                                        answer = answer.lower()
                                        if answer == "да":
                                            self.convert(event)
                                                                
    def cheker_attachments(self,event):
        """
        Тут мы выципляем url документы для того, 
        чтобы можно было его скачать и обработать

        """
        message = self.vk_api.messages.getHistoryAttachments(peer_id = event.user_id, media_type='doc')
        title = message['items'][0]['attachment']['doc']['title']
        size = str(message['items'][0]['attachment']['doc']['size']/1024) + " КБ"
        messages = f"Вы действительно хотите переделать файл:\nНазвание: {title}\nРазмер: {size}\n ---------------------\n Если вы согласны, то отправьте 'да'"
        self.send_message(event,messages)
        self.url = message['items'][0]['attachment']['doc']['url']
    
    def send_message(self,event,message):
        """
        Отправка сообщений
        """
        self.vk_api.messages.send(user_id = event.user_id,random_id=random.randint(0,10000),message=message)

    def convert(self,event):
        """
        Преобразование нашего файла из PDF в DOCX

        """
        file = requests.get(self.url)
        with open('phile.pdf','wb') as code:
            code.write(file.content)
        pdf2docx.parse('phile.pdf','out.docx')
        self.send_answer(event)
    
    def send_answer(self,event):
        """
        Загрузка файла во временное хранилище ВК,
        после чего, отправка сообщения
        """
        result = json.loads(requests.post(self.vk_api.docs.getMessagesUploadServer(type='doc', peer_id=event.user_id)['upload_url'],
                                                  files={'file': open('out.docx', 'rb')}).text)
        jsonAnswer = self.vk_api.docs.save(file=result['file'], title='title', tags=[])

        self.vk_api.messages.send(
                    peer_id=event.user_id,
                    random_id=0,
                    attachment=f"doc{jsonAnswer['doc']['owner_id']}_{jsonAnswer['doc']['id']}"
                )
        
bot = Bot(setting.token,setting.group)
bot.bot()
