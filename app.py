import sqlite3 
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

DATABASE = 'database.db'
conn = sqlite3.connect(DATABASE, check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS items
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   description TEXT)''')
conn.commit()

@app.route('/')
def index():
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    return render_template('index.html', items=items)

if __name__ == '__main__':
    app.run(debug=True)