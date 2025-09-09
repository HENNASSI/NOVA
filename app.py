from flask import Flask, request, jsonify
import sqlite3
import openai
import os

app = Flask(__name__)

# Configure OpenAI (set in Render Environment Variables)
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Database ---
def init_db():
    conn = sqlite3.connect("nova.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_msg TEXT,
                    ai_reply TEXT
                )""")
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return "NOVA AI is alive 🚀"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")

    if not message:
        return jsonify({"reply": "Please say something 🙃"})

    # Call OpenAI
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"You are NOVA, a friendly AI assistant. User said: {message}\nReply:",
        max_tokens=100
    )
    reply = response.choices[0].text.strip()

    # Save memory
    conn = sqlite3.connect("nova.db")
    c = conn.cursor()
    c.execute("INSERT INTO memories (user_msg, ai_reply) VALUES (?, ?)", (message, reply))
    conn.commit()
    conn.close()

    return jsonify({"reply": reply})

@app.route("/add_note", methods=["POST"])
def add_note():
    data = request.get_json()
    note = data.get("note", "")

    if not note:
        return jsonify({"status": "empty note"})

    conn = sqlite3.connect("nova.db")
    c = conn.cursor()
    c.execute("INSERT INTO notes (text) VALUES (?)", (note,))
    conn.commit()
    conn.close()

    return jsonify({"status": "note saved"})

@app.route("/notes", methods=["GET"])
def get_notes():
    conn = sqlite3.connect("nova.db")
    c = conn.cursor()
    c.execute("SELECT * FROM notes")
    notes = [{"id": row[0], "text": row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(notes)

@app.route("/memories", methods=["GET"])
def get_memories():
    conn = sqlite3.connect("nova.db")
    c = conn.cursor()
    c.execute("SELECT * FROM memories")
    memories = [{"id": row[0], "user": row[1], "nova": row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify(memories)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
