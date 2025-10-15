import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g
from datetime import datetime

app = Flask(__name__)
app.secret_key = "CocheraKey1234" #     La clave    #

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
#   Crea la tabla cochera si no existe   #
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
#   Ruta para mostrar la pagina #
@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'POST':
        #   Se ponen los datos del formulario   #
        marca = request.form['marca']
        modelo = request.form['modelo']
        patente = request.form['patente']
        dni = request.form['dni']
        telefono = request.form['telefono']
        horas_a_estar = request.form['horas_a_estar']
        precio_cobrado = request.form['precio_cobrado']
        retirado = request.form.get('retirado', 'No')
        #   Se pone la fecha y hora actual automaticamente  #
        ahora = datetime.now()
        fecha = ahora.strftime("%d/%m/%Y")
        hora = ahora.strftime("%H:%M")
        #   Se agrega el nuevo auto a la base de datos  #
        cursor.execute('''
            INSERT INTO cochera 
            (fecha, hora, marca, modelo, patente, dni, telefono, horas_a_estar, precio_cobrado, retirado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (fecha, hora, marca, modelo, patente, dni, telefono, horas_a_estar, precio_cobrado, retirado))
        
        db.commit()
        flash("Auto registrado correctamente")
        return redirect(url_for('index'))
    #   Se muestran todos los autos de la base de datos #
    cursor.execute("SELECT * FROM cochera")
    autos = cursor.fetchall()
    return render_template('index.html', autos=autos)

if __name__ == '__main__':
    app.run(debug=True)