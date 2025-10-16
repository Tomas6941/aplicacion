import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g
from datetime import datetime

app = Flask(__name__)
app.secret_key = "CocheraKey1234"

DATABASE = 'database.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

with sqlite3.connect(DATABASE) as conn:
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cochera (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        hora TEXT NOT NULL,
        marca TEXT NOT NULL,
        modelo TEXT,
        patente TEXT NOT NULL,
        dni TEXT NOT NULL,
        telefono TEXT,
        horas_a_estar TEXT,
        precio_cobrado TEXT,
        retirado TEXT DEFAULT 'No'
    )
    ''')
    conn.commit()

@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/add', methods=['GET', 'POST'])
def add_auto():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        patente = request.form['patente']
        dni = request.form['dni']
        telefono = request.form['telefono']
        horas_a_estar = request.form['horas_a_estar']
        precio_cobrado = request.form['precio_cobrado']
        retirado = request.form.get('retirado', 'No')

        ahora = datetime.now()
        fecha = ahora.strftime("%d/%m/%Y")
        hora = ahora.strftime("%H:%M")

        cursor.execute('''
            INSERT INTO cochera 
            (fecha, hora, marca, modelo, patente, dni, telefono, horas_a_estar, precio_cobrado, retirado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (fecha, hora, marca, modelo, patente, dni, telefono, horas_a_estar, precio_cobrado, retirado))
        db.commit()

        flash("Auto registrado correctamente")
        return redirect(url_for('list_autos'))

    return render_template('add_auto.html')

@app.route('/list', methods=['GET', 'POST'])
def list_autos():
    db = get_db()
    cursor = db.cursor()
    
    query = "SELECT * FROM cochera"
    search_value = None

    if request.method == 'POST':
        search_value = request.form['buscar']
        query += " WHERE patente LIKE ? OR dni LIKE ?"
        cursor.execute(query, (f"%{search_value}%", f"%{search_value}%"))
    else:
        cursor.execute(query)
    
    autos = cursor.fetchall()
    return render_template('list_autos.html', autos=autos, search_value=search_value)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_auto(id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        patente = request.form['patente']
        dni = request.form['dni']
        telefono = request.form['telefono']
        horas_a_estar = request.form['horas_a_estar']
        precio_cobrado = request.form['precio_cobrado']
        retirado = request.form.get('retirado', 'No')

        cursor.execute('''
            UPDATE cochera
            SET marca=?, modelo=?, patente=?, dni=?, telefono=?, horas_a_estar=?, precio_cobrado=?, retirado=?
            WHERE id=?
        ''', (marca, modelo, patente, dni, telefono, horas_a_estar, precio_cobrado, retirado, id))
        db.commit()
        flash("Auto editado correctamente")
        return redirect(url_for('list_autos'))

    cursor.execute("SELECT * FROM cochera WHERE id=?", (id,))
    auto = cursor.fetchone()
    return render_template('edit_auto.html', auto=auto)

@app.route('/delete/<int:id>')
def delete_auto(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM cochera WHERE id=?", (id,))
    db.commit()
    flash("Auto eliminado correctamente")
    return redirect(url_for('list_autos'))

if __name__ == '__main__':
    app.run(debug=True)

