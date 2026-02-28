from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS scores(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            time REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/save_score", methods=["POST"])
def save_score():
    data = request.json
    username = data.get("username")
    time = float(data.get("time"))

    if not username:
        return jsonify({"status":"error"})

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # если игрок уже есть — обновляем только если время лучше
    c.execute("SELECT time FROM scores WHERE username=?", (username,))
    existing = c.fetchone()

    if existing:
        if time < existing[0]:
            c.execute("UPDATE scores SET time=? WHERE username=?", (time, username))
    else:
        c.execute("INSERT INTO scores (username,time) VALUES (?,?)", (username,time))

    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})

@app.route("/leaderboard")
def leaderboard():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT username,time FROM scores WHERE time IS NOT NULL ORDER BY time ASC LIMIT 10")
    data = c.fetchall()
    conn.close()
    return jsonify(data)

if __name__ == "__main__":
    app.run()