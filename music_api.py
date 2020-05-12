import flask
import sqlite3
import shutil
import hashlib
import os
from random import randrange


blueprint = flask.Blueprint("music_api", __name__, template_folder="templates")

# Подключение базы
base = sqlite3.connect("database.db", check_same_thread=False)
cur = base.cursor()


# Генерация айди для аккаунта
def generateId():
    # Получаем айди всех пользователей
    response = cur.execute(f"""SELECT id FROM users""").fetchall()
    ids = [i[0][1:] for i in response]
    randomId = randrange(100000, 999999)
    # Генерирум рандом айди пока он не станет уникальным
    while randomId in ids:
        randomId = randrange(100000, 999999)
    return str(randomId)


# Функция проверки юзера
def funcReturn(lst):
    if len(lst) > 0:
        return "success"
    else:
        return "fail"


# Api авторизации и регистрацим
@blueprint.route('/api/users/<request_type>')
def UsersApi(request_type):
    # Авторизация 
    if request_type == "get":
        # получение параметров с GET-запроса
        login = flask.request.args.get("login")
        passwd = flask.request.args.get("pass")
        # получение аккаунта в базе и в дальнейшем преобразования данных в JSON
        getUser = cur.execute(f"""SELECT login, pass FROM users WHERE login = '{login}' AND pass = '{hashlib.sha384(passwd.encode()).hexdigest()}'""").fetchall()
        data = {
            "data": {
                "login": login,
                "status": funcReturn(getUser)
            }
        }
        return data
    # Регистрация
    elif request_type == "add":
        # Все так же как и с авторизацией
        login = flask.request.args.get("login")
        passwd = flask.request.args.get("pass")
        data = {
            "data": {
                "login": login,
                "password": passwd,
                "status": "success",
            }
        }
        # Проверка нет ли еще такого ще аккаунта
        if len(cur.execute(f"""SELECT login FROM users WHERE login = '{login}'""").fetchall()) < 1:
            addUser = cur.execute(f"""INSERT INTO users VALUES('{str(login[0]).lower() + generateId()}', '{login}', '{hashlib.sha384(passwd.encode()).hexdigest()}')""")
            base.commit()
        else:
            # Добавление параметров в JSON об ошибки и ее описания
            data["data"]["status"] = "fail"
            data["data"]["status_description"] = "Login already in use"
        return data


# Авторизация аккаунта с помощью API
@blueprint.route('/users/log')
def login():
    data = UsersApi("get")["data"]
    if "success" in data["status"]:
        flask.session["user"] = data["login"]
        return flask.redirect(flask.url_for("cpanel"))
    else:
        return "Аккаунта не существует!"


# Загрузка файла на сервер
@blueprint.route("/api/users/load_music", methods=["POST", "GET"])
def load_music():
    # Проверка на запрос
    if flask.request.method == "GET":
        return {"data": {"status": "fail", "description": "Метод 'GET' не поддерживается!"}}
    if flask.request.method == "POST":
        username = flask.session.get("user")
        # Проверка на валидность аккаунта
        if len(cur.execute(f"""SELECT login FROM users WHERE login = '{username}'""").fetchall()) > 0:
            try:
                # Создание папки и загрузки туда mp3 файла
                file_music = flask.request.files.get("file")
                files = flask.request.files.get("file")
                filename = flask.request.form.get("track")
                try:
                    os.makedirs(f"static/music/{username}")
                except:
                    pass
                with open(f"static/music/{username}/{filename}.mp3", "wb") as file:
                    file.write(file_music.read())
                    file.close()
                shutil.copy(f"static/music/{username}/{filename}.mp3", f"static/music/other/{username}_{filename}.mp3")
                return {"data": {"status": "success"}}
            except:
                return {"data": {"status": "fail"}}


# Загрузка файлов с помощью API
@blueprint.route("/music/uploads", methods=["POST", "GET"])
def uploads_music():
    data = load_music()["data"]
    if "success" in data["status"]:
        return flask.redirect(flask.url_for("cpanel", status="success"))
    else:
        return flask.redirect(flask.url_for("cpanel", status="error_upload"))


# Удаление файлов без API
@blueprint.route("/users/del/<username>/<filename>")
def delMusic(username, filename):
    try:
        os.remove(f"static/music/{username}/{filename}")
        os.remove(f"static/music/other/{flask.session.get('user')}_{filename}")
    except:
        pass
    return flask.redirect(flask.url_for("cpanel", status="success"))


# Регистрация аккаунта с помощью API
@blueprint.route('/users/reg')
def register():
    data = UsersApi("add")["data"]
    if "success" in data["status"]:
        flask.session["user"] = data["login"]
        return flask.redirect(flask.url_for("cpanel"))
    else:
        return flask.redirect(flask.url_for("main", status="error", description=data["status_description"]))


@blueprint.route('/users/exit')
def exit():
    flask.session["user"] = None
    return flask.redirect(flask.url_for("main"))
