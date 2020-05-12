from flask import Flask, render_template, session, request
import music_api

app = Flask(__name__)
app.config['SECRET_KEY'] = "123131"

@app.route('/')
@app.route("/index")
def main():
    music_list = []
    try:
        music_list = music_api.os.listdir(f"static/music/other")
        music_list = [i.split("_") for i in music_list]
    except:
        pass
    return render_template("mainpage.html", ses=session, music=music_list, music_len=len(music_list))


@app.route("/cpanel")
def cpanel():
    music_list = []
    try:
        music_list = music_api.os.listdir(f"static/music/{session.get('user')}")
        music_list = [i for i in music_list]
    except:
        pass
    return render_template("cpanelpage.html", ses=session, music=music_list, music_len=len(music_list), req=request)


@app.route("/result")
def result():
    return 0


if __name__ == '__main__':
    app.register_blueprint(music_api.blueprint)
    app.run(port=80, host='127.0.0.1', debug=True)
