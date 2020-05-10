from flask import Flask, render_template, session, request
import music_api

app = Flask(__name__)
app.config['SECRET_KEY'] = "123131"

@app.route('/')
@app.route("/index")
def main():
    return render_template("mainpage.html")
@app.route("/cpanel")
def cpanel():
    reqtype = request.args.get("page")
    if reqtype == "news":
        return render_template("cpanelpage.html", ses=session)
    else:
        return "В разработке"

if __name__ == '__main__':
    app.register_blueprint(music_api.blueprint)
    app.run(port=80, host='127.0.0.1', debug=True)
