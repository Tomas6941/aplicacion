import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = "CocheraKey1234"

DATABASE = 'database.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Crear tabla si no existe
with sqlite3.connect(DATABASE) as conn:
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cochera (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_ingreso TEXT NOT NULL,
        hora_ingreso TEXT NOT NULL,
        marca TEXT NOT NULL,
        color TEXT NOT NULL,
        patente TEXT NOT NULL,
        dni TEXT NOT NULL,
        telefono TEXT NOT NULL,
        ticket TEXT UNIQUE NOT NULL,
        fecha_salida TEXT,
        hora_salida TEXT,
        monto_total REAL,
        retirado INTEGER DEFAULT 0
    )
    ''')
    conn.commit()

def generar_ticket():
    """Genera un ticket único para cada auto"""
    return f"T-{random.randint(1_000_000, 9_999_999)}"

@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/add', methods=['GET', 'POST'])
def add_auto():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        marca = request.form['marca']
        color = request.form['color']
        patente = request.form['patente']
        dni = request.form['dni']
        telefono = request.form['telefono']

        ahora = datetime.now()
        fecha_ingreso = ahora.strftime("%d/%m/%Y")
        hora_ingreso = ahora.strftime("%H:%M")

        # Generar ticket único
        while True:
            ticket = generar_ticket()
            cursor.execute("SELECT id FROM cochera WHERE ticket=?", (ticket,))
            if cursor.fetchone() is None:
                break

        cursor.execute('''
            INSERT INTO cochera (fecha_ingreso, hora_ingreso, marca, color, patente, dni, telefono, ticket)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (fecha_ingreso, hora_ingreso, marca, color, patente, dni, telefono, ticket))
        db.commit()

        flash(f"Auto registrado correctamente. Ticket: {ticket}")
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
        query += " WHERE patente LIKE ? OR dni LIKE ? OR ticket LIKE ?"
        cursor.execute(query, (f"%{search_value}%", f"%{search_value}%", f"%{search_value}%"))
    else:
        cursor.execute(query)

    # Convertir filas a diccionarios para poder modificar
    autos = [dict(auto) for auto in cursor.fetchall()]

    # Calcular tiempo en minutos
    for auto in autos:
        if auto['hora_salida']:
            fmt = "%H:%M"
            ingreso = datetime.strptime(auto['hora_ingreso'], fmt)
            salida = datetime.strptime(auto['hora_salida'], fmt)
            auto['tiempo_min'] = int((salida - ingreso).total_seconds() / 60)
        else:
            auto['tiempo_min'] = None

    return render_template('list_autos.html', autos=autos, search_value=search_value)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_auto(id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        marca = request.form['marca']
        color = request.form['color']
        patente = request.form['patente']
        dni = request.form['dni']
        telefono = request.form['telefono']

        cursor.execute('''
            UPDATE cochera
            SET marca=?, color=?, patente=?, dni=?, telefono=?
            WHERE id=?
        ''', (marca, color, patente, dni, telefono, id))
        db.commit()
        flash("Auto editado correctamente")
        return redirect(url_for('list_autos'))

    cursor.execute("SELECT * FROM cochera WHERE id=?", (id,))
    auto = cursor.fetchone()
    return render_template('edit_auto.html', auto=auto)

@app.route('/retirar', methods=['POST'])
def retirar_auto():
    db = get_db()
    cursor = db.cursor()

    ticket = request.form['ticket']
    cursor.execute("SELECT * FROM cochera WHERE ticket=? AND retirado=0", (ticket,))
    auto = cursor.fetchone()
    if not auto:
        flash("Ticket inválido o auto ya retirado")
        return redirect(url_for('list_autos'))

    ahora = datetime.now()
    fecha_salida = ahora.strftime("%d/%m/%Y")
    hora_salida = ahora.strftime("%H:%M")

    precio_por_hora = 5000
    precio_por_minuto = precio_por_hora / 60

    formato = "%H:%M"
    ingreso = datetime.strptime(auto['hora_ingreso'], formato)
    salida = datetime.strptime(hora_salida, formato)
    diferencia_minutos = (salida - ingreso).total_seconds() / 60
    if diferencia_minutos < 1:
        diferencia_minutos = 1

    monto_total = round(diferencia_minutos * precio_por_minuto, 2)

    cursor.execute('''
        UPDATE cochera
        SET fecha_salida=?, hora_salida=?, monto_total=?, retirado=1
        WHERE id=?
    ''', (fecha_salida, hora_salida, monto_total, auto['id']))
    db.commit()

    flash(f"Auto retirado. Tiempo: {int(diferencia_minutos)} min — Monto total: ${monto_total}")
    return redirect(url_for('list_autos'))

if __name__ == '__main__':
    app.run(debug=True)
