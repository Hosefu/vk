import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
import sqlite3
import random
import config

vk_session = vk_api.VkApi(token=config.token)

longpoll = VkLongPoll(vk_session)

vk = vk_session.get_api()

conn = sqlite3.connect(config.sqlite_path)
c = conn.cursor()

def register_new_user(user_id):
    cmd = "INSERT INTO users(user_id, state) VALUES (%d, '')" % user_id



while True:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:

