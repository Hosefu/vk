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
            last_exercise_id=result[2],
            exist=True
        )

    return result_arr


def send_message_VK(event, message):
    vk.messages.send(  # Отправляем сообщение
        user_id=event.user_id,
        message=message,
        random_id=random.randint(-1000000000, 1000000000)
    )
    print_str = "— {}".format(message)
    print(print_str)

def get_user_VK(event):
    request_arr = vk.users.get(
        user_ids=event.user_id
    )
    result_arr = dict(
        id=request_arr[0]["id"],
        first_name=request_arr[0]["first_name"],
        last_name=request_arr[0]["last_name"],
        name="{} {}".format(request_arr[0]["first_name"], request_arr[0]["last_name"]),
        is_closed=request_arr[0]["is_closed"]
    )
    return result_arr


def register_new_user(user_id):
    cmd = "INSERT INTO users(user_id, state) VALUES (%d, 'none')" % user_id
    c.execute(cmd)
    conn.commit()


def set_user_state(user_id, state):
    cmd = "UPDATE users SET state = '%s' WHERE user_id = %d" % (state, user_id)
    c.execute(cmd)
    conn.commit()


def set_user_last_exercise_id(user_id, exercise_id):
    cmd = "UPDATE users SET last_exercise_id = '{}' WHERE user_id = {}".format(exercise_id, user_id)
    c.execute(cmd)
    conn.commit()


def get_exercise(exercise_id):
    cmd = "SELECT * FROM exercises WHERE exercise_id={}".format(exercise_id)
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
            name = get_user_VK(event)["name"]
            print_str = "> {} [{}, id{}]".format(event.message, name, event.user_id)
            print(print_str)

            if not get_user(user_id=event.user_id)["exist"]:
                register_new_user(user_id=event.user_id)

            if event.text.lower() == "биотоп" and get_user(event.user_id)["state"] == "none":
                send_message_VK(event, "Хочешь БИОТОП?")
                set_user_state(event.user_id, "biotop_wait")

            if get_user(event.user_id)["state"] == "biotop_wait":
                msg = event.text.lower()
                used = False

                if msg == "да" and not used:
                    send_message_VK(event, "Кайф! Лови")
                    set_user_state(event.user_id, "biotop_exercise")
                    exercise = generate_exercise()
                    msg = "Вот вопрось: {}. варианты: {}, {}, {}, {}".format(exercise["question"],
                                                                             exercise["answer_one"],
                                                                             exercise["answer_two"],
                                                                             exercise["answer_three"],
                                                                             exercise["answer_true"])
                    send_message_VK(event, msg)
                    set_user_last_exercise_id(event.user_id, exercise["exercise_id"])
                    used = True
                elif msg == "нет" and not used:
                    send_message_VK(event, "Окей. Ты возвращен обратно")
                    set_user_state(event.user_id, "none")
                    used = True
                elif msg != "да" and not used:
                    send_message_VK(event, "Напиши ДА для продолжения или НЕТ для отмены.")
                    used = True

            if get_user(event.user_id)["state"] == "biotop_exercise":
                msg = event.text.lower()
                used = False

                exercise_id = get_user(event.user_id)["last_exercise_id"]
                exercise = dict(
                    ans_1=get_exercise(exercise_id)["answer_one"],
                    ans_2=get_exercise(exercise_id)["answer_two"],
                    ans_3=get_exercise(exercise_id)["answer_three"],
                    ans_true=get_exercise(exercise_id)["answer_true"]
                )

                if msg == exercise["ans_true"]:
                    send_message_VK(event, "кайф получи 10 баллов")
                    set_user_state(event.user_id, "biotop_exercise_new")
                elif msg == exercise["ans_1"] or msg == exercise["ans_2"] or msg == exercise["ans_3"]:
                    send_message_VK(event, "сорян, неправильно")
                    set_user_state(event.user_id, "biotop_exercise_new")
                else:
                    send_message_VK(event, "выбери вариант ало")

            if get_user(event.user_id)["state"] == "biotop_exercise_new":
                msg = event.text.lower()

                send_message_VK(event, "Пиши ок чтобы продолжить или отмена")

                if msg == "ок":
                    set_user_state(event.user_id, "biotop_exercise")
                    exercise = generate_exercise()
                    msg = "Вот вопрось: {}. варианты: {}, {}, {}, {}".format(exercise["question"],
                                                                             exercise["answer_one"],
                                                                             exercise["answer_two"],
                                                                             exercise["answer_three"],
                                                                             exercise["answer_true"])
                    send_message_VK(event, msg)
                    set_user_last_exercise_id(event.user_id, exercise["exercise_id"])