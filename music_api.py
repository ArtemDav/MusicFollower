import flask
import sqlite3
import hashlib


blueprint = flask.Blueprint("music_api", __name__, template_folder="templates")

# Подключение базы
base = sqlite3.connect("database.db", check_same_thread=False)
cur = base.cursor()


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
            addUser = cur.execute(f"""INSERT INTO users VALUES('{login}', '{hashlib.sha384(passwd.encode()).hexdigest()}')""")
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
        return """Аккаунта не существует!"""

# Регистрация аккаунта с помощью API
@blueprint.route('/users/reg')
def register():
    data = UsersApi("add")["data"]
    if "success" in data["status"]:
        flask.session["user"] = data["login"]
        return flask.redirect(flask.url_for("cpanel"))
    else:
        return "Аккаунт не создан! Возможные ошибки: " + data["status_description"]

@blueprint.route('/users/exit')
def exit():
    flask.session["user"] = None
    return flask.redirect(flask.url_for("main"))
