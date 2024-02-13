from flask import Flask, render_template, redirect, url_for, session, request
import sqlite3
import secrets
import datetime


app = Flask(__name__)
app.config["SECRET_KEY"] = "123456"

@app.route("/", methods=["GET"])
def home_page():
    req = request.args.get("stat")
    post = request.args.get("post")
    if req == "login":
        return render_template("index.html", login=True)
    elif req == "signin":
        return render_template("index.html", signin=True)
    if session:
        try:
            connect = sqlite3.connect("data.db")
            cursor = connect.cursor()
            if post:
                req = cursor.execute("SELECT * FROM messages WHERE token = ?", (post,))
                messages_res = req.fetchone()
                messages_response = cursor.execute("SELECT * FROM messages WHERE response = ?", (post, ))
                res = messages_response.fetchall()
                return render_template("forum.html",messages = messages_res, messages_resp = res, postit=True)
            else:
                req = cursor.execute("SELECT * FROM messages WHERE response IS NULL")
                messages_res = req.fetchall()
        except Exception as e:
            connect.rollback()
            print(e)
        finally:
            connect.close()
            
        return render_template("forum.html",messages = reversed(messages_res))
    else:
        return render_template("index.html", signin=False, login=False)

@app.route("/signin", methods=["POST"])
def signin():
    username = request.form.get("username")
    password = request.form.get("password")
    avatar = "https://api.dicebear.com/7.x/notionists-neutral/svg?seed="+username
    try:
        connect = sqlite3.connect("data.db")
        cursor = connect.cursor()
        res = cursor.execute("SELECT * FROM users WHERE name = ?", (username,)).fetchone()
        if res:
            return render_template("index.html", signin=True, alreadyExist=True)
        else:
            token = secrets.token_hex(8)
            req = cursor.execute("INSERT INTO users (token, name, password, avatar) VALUES (?,?,?,?)", (token, username, password, avatar))
            session["Token"] = token
        connect.commit()
        user = cursor.execute("SELECT * FROM users WHERE token = ?", (token, )).fetchone()
        session["user"] = user
    except Exception as e:
        connect.rollback()
        print(e)
    
    finally:
        connect.close()
    
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    try:
        connect = sqlite3.connect("data.db")
        cursor = connect.cursor()
        res = cursor.execute("SELECT * FROM users WHERE name = ? AND password = ?", (username, password)).fetchone()
        if not res:
            return render_template("index.html", login=True, dontExist=True)
        else:
            session["Token"] = res[0]
            session["user"] = res
        connect.commit()
        
    except Exception as e:
        connect.rollback()
        print(e)
    
    finally:
        connect.close()
    
    return redirect("/")


@app.route("/clear")
def clear():
    session.clear()
    return redirect("/")

@app.route("/send", methods=["POST"])
def send():
    content = request.form.get("messagecontent")
    resp = request.form.get("resp")
    author = session["user"][1]
    time = "Le "+ datetime.datetime.now().strftime("%d %m %y")
    token = secrets.token_hex(6)
    if resp:
        data = (token, author, time, content, session['user'][3], resp)
    else:
        data = (token, author, time, content, session['user'][3], resp)
    try:
        connect = sqlite3.connect("data.db")
        cursor = connect.cursor()
        req = cursor.execute("INSERT INTO messages (token, author, datetime, content, useravatar, response) VALUES (?,?,?,?,?,?)", data)
        connect.commit()
    except Exception as e:
        connect.rollback()
        print(e)
    finally:
        connect.close()
    
    if resp:
        return redirect(url_for("home_page")+"?post="+resp)
    else:
        return redirect(url_for("home_page"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")