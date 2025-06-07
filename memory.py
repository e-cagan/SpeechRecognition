import sqlite3
import os

DB_FILE = "memory.db"

# Initialize DB table and connection
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Save memory a new conversation
def save_to_memory(prompt, response):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO memory (prompt, response) VALUES (?, ?)", (prompt, response))
    conn.commit()
    conn.close()

# Return the last X conversations (default = 5)
def load_recent_history(limit=5):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT prompt, response FROM memory ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows[::-1]

# Convert to chat format
def get_chat_history_as_messages(user_input):
    history = load_recent_history()
    messages = []
    for prompt, response in history:
        messages.append({"role": "user", "content": prompt})
        messages.append({"role": "assistant", "content": response})
    messages.append({"role": "user", "content": user_input})
    return messages
