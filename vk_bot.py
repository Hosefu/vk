import random
import sqlite3

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

import config
import keyboard

vk_session = vk_api.VkApi(token=config.token)
longPoll = VkLongPoll(vk_session)
vk = vk_session.get_api()
conn = sqlite3.connect(config.sqlite_path)
c = conn.cursor()
t = False

print("Подключение к серверу...\n< Успешно >\n")
print("Запуск бота...\n< Успешно >\n\nЛоги:\n")


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
            score=result[3],
            exist=True
        )

    return result_arr


def send_message_VK(event, message, keyboard=keyboard.default):
    vk.messages.send(  # Отправляем сообщение
        user_id=event.user_id,
        message=message,
        keyboard=keyboard,
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
    cmd = "INSERT INTO users(user_id, state, last_exercise_id, score) VALUES (%d, 'none', 1, 0)" % user_id
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


def send_exercise(event):
    set_user_state(event.user_id, "biotop_exercise")
    exercise = generate_exercise()
    msg = "Вопрос: {}".format(exercise["question"])

    questions = [exercise["answer_one"], exercise["answer_two"], exercise["answer_three"], exercise["answer_true"]]
    random.shuffle(questions)
    keyboard_exercise = keyboard.exercise % (questions[0], questions[1], questions[2], questions[3])
    send_message_VK(event, msg, keyboard=keyboard_exercise)

    set_user_last_exercise_id(event.user_id, exercise["exercise_id"])


def score_controller(user_id, score):
    score_old = get_user(user_id)["score"]
    score_new = score_old + score

    cmd = "UPDATE users SET score = '{}' WHERE user_id = {}".format(score_new, user_id)
    c.execute(cmd)
    conn.commit()

    return score_new


while True:
    for event in longPoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            name = get_user_VK(event)["name"]
            print_str = "> {} [{}, id{}]".format(event.message, name, event.user_id)
            print(print_str)

            if not get_user(user_id=event.user_id)["exist"]:
                register_new_user(user_id=event.user_id)

            if event.text.lower() == "биотоп" and get_user(event.user_id)["state"] == "none":
                send_message_VK(event, "Хочешь участвовать в БИОТОПЕ? Жора пидр", keyboard=keyboard.biotop)
                set_user_state(event.user_id, "biotop_wait")

            if get_user(event.user_id)["state"] == "biotop_wait":
                msg = event.text.lower()

                if msg == "да, начать биотоп!":
                    send_message_VK(event, "Окей, тогда начинаем. За правильные ответы на вопросы ты получаешь очки и "
                                           "можешь участвовать в топе. Удачи!")
                    send_exercise(event)
                elif msg == "отмена":
                    send_message_VK(event, "Вы вышли из БИОТОПА")
                    set_user_state(event.user_id, "none")
                elif msg != "биотоп":
                    send_message_VK(event,
                                    """⛔ Выбери один из перечисленных вариантов: "Да, начать БИОТОП!" или "Отмена" """,
                                    keyboard=keyboard.biotop)

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
                    score_new = score_controller(event.user_id, 5)
                    send_message_VK(event, "Отлично! Ты заработал 5 баллов\nТвой счет: {}".format(score_new))
                    set_user_state(event.user_id, "biotop_exercise_new")
                elif msg == exercise["ans_1"] or msg == exercise["ans_2"] or msg == exercise["ans_3"]:
                    score_new = score_controller(event.user_id, -2)
                    send_message_VK(event, "Упс! Неправильно. Ты потерял 2 балла\nТвой счет: {}".format(score_new))
                    set_user_state(event.user_id, "biotop_exercise_new")
                elif msg != "да, начать биотоп!":
                    send_message_VK(event, "выбери вариант ало")

            if get_user(event.user_id)["state"] == "biotop_exercise_new":
                msg = event.text.lower()

                if msg == "продолжить":
                    send_exercise(event)

                elif msg == "отмена":
                    score_usr = get_user(event.user_id)["score"]
                    send_message_VK(event, "Твой БИОТОП завершен!\nТвой счет: {}".format(score_usr))
                    set_user_state(event.user_id, "none")

                else:
                    send_message_VK(event, "Пиши ок чтобы продолжить или отмена", keyboard.next)
