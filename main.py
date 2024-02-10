from flask import Flask, render_template, redirect, url_for, session, request
import sqlite3
import secrets

app = Flask(__name__)
app.config["SECRET_KEY"] = "123456"

@app.route("/")
def home_page():
    req = request.args.get("stat")
    if req == "login":
        return render_template("index.html", login=True)
    elif req == "signin":
        return render_template("index.html", signin=True)
    return render_template("index.html", signin=False, login=False)

@app.route("/signin", methods=["POST"])
def signin():
    username = request.form.get("username")
    password = request.form.get("password")
    try:
        connect = sqlite3.connect("data.db")
        cursor = connect.cursor()
        res = cursor.execute("SELECT * FROM users WHERE name = ?", (username,)).fetchone()
        if res:
            return render_template("index.html", signin=True, alreadyExist=True)
        else:
            token = secrets.token_hex(8)
            req = cursor.execute("INSERT INTO users (token, name, password) VALUES (?,?,?)", (token, username, password))
            session["Token"] = token
        connect.commit()
        user = cursor.execute("SELECT * FROM users WHERE token = ?", (token, )).fetchone()
        session["user"] = user
    except Exception as e:
        connect.rollback()
        print(e)
    
    finally:
        connect.close()
    
    return render_template("forum.html")

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
    
    return render_template("forum.html")


@app.route("/clear")
def clear():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")