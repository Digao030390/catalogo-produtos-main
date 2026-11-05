import sqlite3
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
conn = sqlite3.connect('database.db')
conn.execute('''CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)''')
hash_ = bcrypt.generate_password_hash("senha123").decode('utf-8')
try:
    conn.execute('INSERT INTO usuario (username, password_hash) VALUES (?, ?)', ("admin", hash_))
    conn.commit()
    print("Usuário criado.")
except sqlite3.IntegrityError:
    print("Usuário já existe.")
conn.close()