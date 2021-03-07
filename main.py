import vk_api
import random
import time
import sqlite3
import os
from googletrans import Translator
from kinopoisk.movie import Movie

def set_state(state, id):
    sql = f'''UPDATE Users SET state='{state}' WHERE id={id} '''
    cursor.execute(sql)
    conn.commit()


def set_property(name, value, id):
    sql = f'''UPDATE Users SET {name}='{value}' WHERE id={id} '''
    cursor.execute(sql)
    conn.commit()


def get_property(name, id):
    sql = f"SELECT {name} FROM Users WHERE id={from_id} "
    cursor.execute(sql)
    return cursor.fetchone()[0]



conn = sqlite3.connect("database.db")
cursor = conn.cursor()

token = "81c628d6d793e632266d636c88767092e8686c8adbdfd8bad76ea56b16054ed38abebe57f163b7e895c4f"

vk = vk_api.VkApi(token=token)
vk._auth_token()
uploader = vk_api.upload.VkUpload(vk)

value = {"count": 20, "offset": 0, "filter": "unanswered"}


kbrd = open("keyboards/empty.json", "r", encoding="UTF-8").read()

translator = Translator()

while True:
    messages = vk.method("messages.getConversations", value)

    if messages["count"] > 0:
        from_id = messages["items"][0]["last_message"]["from_id"]
        in_text = messages["items"][0]["last_message"]["text"]

        sql = f"SELECT * FROM Users WHERE id={from_id}"
        cursor.execute(sql)
        if len(cursor.fetchall()) == 0:
            sql = f'''
            INSERT INTO Users (id, state)
            VALUES ({from_id}, 'start')
            '''
            cursor.execute(sql)
            conn.commit()


        sql = f"SELECT state FROM Users WHERE id={from_id} "
        cursor.execute(sql)
        state = cursor.fetchone()[0]
        print(state)

        if state == "start":
            out_text = "Привет!"
            set_state("menu", from_id)
            kbrd = open("keyboards/menu.json", "r", encoding="UTF-8").read()

        elif state == "menu":
            if in_text == "Переводчик":
                set_state("translation",from_id)
                out_text = "Пиши слово и я дам тебе перевод"
                kbrd = open("keyboards/empty.json", "r", encoding="UTF-8").read()


            elif in_text == "Правило Английского":
                set_state("ruleANGL",from_id)
                files = os.listdir(path='./data/text')
                out_text = "Выберите файл:\n"
                for i in range(len(files)):
                    out_text += f"{i+1}) {files[i].split('.')[0]}\n"
                kbrd = open("keyboards/empty.json", "r", encoding="UTF-8").read()
            else:
                out_text = "неправильный пункт меню"
                set_state("menu", from_id)
                kbrd = open("keyboards/menu.json", "r", encoding="UTF-8").read()
        elif state == "translation":
            out_text = translator.translate(in_text, dest = 'en').text
            set_state("menu", from_id)
            kbrd = open("keyboards/menu.json", "r", encoding="UTF-8").read()

        elif state == "ruleANGL":
            try: 
                n = int(in_text)
                f = open(f"data/text/{os.listdir(path='./data/text')[n-1]}", "r", encoding="UTF-8")
                out_text = f.read()
                f.close()
            except Exception:
                out_text = "Нет такого файла :("
  


            set_state("menu", from_id)
            kbrd = open("keyboards/menu.json", "r", encoding="UTF-8").read()
            
      
        
            

            
      
        else:
            out_text = "Неизвестная команда"
            set_state("menu", from_id)
            kbrd = open("keyboards/menu.json", "r", encoding="UTF-8").read() 
        vk.method("messages.send", {"peer_id": from_id, "message": out_text, "random_id": random.randint(1, 1000),
                                 "keyboard": kbrd})
    time.sleep(1)
