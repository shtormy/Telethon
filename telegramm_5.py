# Книжный IT сборник
# Архив разработчика

from telethon import TelegramClient
import time
from datetime import datetime
import configparser
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import json

config = configparser.ConfigParser()
config.read("config.ini")

api_id: str = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

client = TelegramClient(username, api_id, api_hash)
client.start()

start = time.time()


async def selection():
    dialogs = []  # список чатов
    last_date = None
    size_dialogs = 200  # максимальное количество получаемых групп
    groups = []  # список чатов после проверки

    result = await client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=size_dialogs,
        hash=0
    ))

    dialogs.extend(result.chats)

    for dialog in dialogs:
        try:
            if dialog.megagroup == False:
                groups.append(dialog)
        except:
            continue

    print('Выберите номер группы из перечня:')
    i = 0
    for g in groups:
        print(str(i) + '- ' + g.title)
        i += 1

    g_index = input("Введите нужную цифру: ")

    target_group = groups[int(g_index)] #выбор нужного канала

    all_books = [] # создаем список для записи данных

    link_path = 'https://t.me/c/'

    # перебираем все сообщения канала
    async for msg in client.iter_messages(target_group):
        try:
            if msg.media and msg.file.ext == '.pdf' and msg not in all_books:
                # all_books.append(await msg.download_media(file="./Books")) # если нужно сразу скачать все книги
                all_books.append(({"date": msg.date,
                                   "name": msg.file.name,
                                   "link": f'{link_path}{msg.peer_id.channel_id}/{msg.id}'
                                   }))
            time.sleep(1)

        except Exception as exc:
            print(f'Внимание! Ошибка: {exc}') # если будет ошибка, все равно продолжить

        else:
            continue

    class DateTimeEncoder(json.JSONEncoder):
        '''Класс для сериализации записи дат в JSON'''

        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, bytes):
                return list(obj)
            return json.JSONEncoder.default(self, obj)

    # записываем в json
    with open('parse_books.json', 'w', encoding='utf-8') as outfile:
        json.dump(all_books, outfile, ensure_ascii=False, cls=DateTimeEncoder, indent=4)


async def main():
    await selection()
    end = time.time()
    print('Загрузка успешно завершена.')
    print(f"Время выполнения программы: {round((end - start)/60), 2} минут.")


with client:
    client.loop.run_until_complete(main())
