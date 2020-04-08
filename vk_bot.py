import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

import sqlite3
import random
import config

vk_session = vk_api.VkApi(token=config.token)
longPoll = VkLongPoll(vk_session)
vk = vk_session.get_api()
conn = sqlite3.connect(config.sqlite_path)
c = conn.cursor()
t = False


def get_user(user_id):
    cmd = "SELECT * FROM users WHERE user_id=%d" % user_id
    c.execute(cmd)
    result = c.fetchone()
    result_arr = dict()

    if result is None:
        result_arr["exist"] = False
    else:
        result_arr = dict(
            user_id=result[0],
            state=result[1],
            exist=True
        )

    return result_arr


def send_message_VK(event, message):
    vk.messages.send(  # Отправляем сообщение
        user_id=event.user_id,
        message=message,
        random_id=random.randint(-1000000000, 1000000000)
    )

def register_new_user(user_id):
    cmd = "INSERT INTO users(user_id, state) VALUES (%d, 'none')" % user_id
    c.execute(cmd)
    conn.commit()

def set_user_state(user_id, state):
    cmd = "UPDATE users SET state = '%s' WHERE user_id = %d" % (state, user_id)
    c.execute(cmd)
    conn.commit()

def generate_exercise():
    cmd = "SELECT COUNT(*) FROM exercises"
    c.execute(cmd)
    count = c.fetchone()[0]

    id = random.randint(1, count)
    cmd = "SELECT * FROM exercises WHERE exercise_id=%d" % id
    c.execute(cmd)
    result = c.fetchone()
    result_arr = dict(
        exercise_id=result[0],
        question=result[1],
        answer_one=result[2],
        answer_two=result[3],
        answer_three=result[4],
        answer_true=result[5],
    )

    return result_arr


while True:
    for event in longPoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if not get_user(user_id=event.user_id)["exist"]:
                register_new_user(user_id=event.user_id)

            if event.text.lower() == "биотоп" and get_user(event.user_id)["state"] == "none":
                send_message_VK(event, "Хочешь БИОТОП? Введи ДА!")
                set_user_state(event.user_id, "biotop_wait")

            if event.text.lower() == "да" and get_user(event.user_id)["state"] == "biotop_wait":
                send_message_VK(event, "Кайф! Лови")
                set_user_state(event.user_id, "biotop_exercise")
                exercise = generate_exercise()
                send_message_VK(event, "Вот вопрось: %s. варианты: %s, %s, %s. %s") % exercise["question"], exercise["answer_one"], exercise["answer_two"], exercise["answer_three"], exercise["answer_true"]

