import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'digitech_clave_secreta_2026'
DB_NAME = 'digitech.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            fecha_nacimiento TEXT NOT NULL,
            telefono TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            tipo_persona TEXT NOT NULL,
            rol TEXT NOT NULL,
            password TEXT NOT NULL,
            fecha_registro TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    if 'user' in session:
        u = session['user']
        return f"""
        <div style="font-family: Arial; padding: 20px;">
            <h1>Bienvenido a DIGITECH, {u['nombre']} {u['apellido']}</h1>
            <p><b>Tipo de persona:</b> {u['tipo_persona'].capitalize()}</p>
            <p><b>Rol asignado:</b> {u['rol'].capitalize()}</p>
            <p><b>Correo:</b> {u['email']}</p>
            <a href='/logout'>Cerrar Sesión</a>
        </div>
        """
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personas WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = {
                'id': user['id'],
                'nombre': user['nombre'],
                'apellido': user['apellido'],
                'email': user['email'],
                'tipo_persona': user['tipo_persona'],
                'rol': user['rol']
            }
            flash(f"¡Bienvenido/a, {user['nombre']}!", "success")
            return redirect(url_for('home'))
        else:
            flash("Correo o contraseña incorrectos.", "error")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    today_date = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        run = request.form['run'].strip()
        nombre = request.form['nombre'].strip()
        apellido = request.form['apellido'].strip()
        fecha_nacimiento = request.form['fecha_nacimiento']
        telefono = request.form['telefono'].strip()
        email = request.form['email'].strip()
        tipo_persona = request.form['tipo_persona']
        
        if tipo_persona == 'cliente':
            rol = 'comprador'
        else:
            rol = request.form.get('rol_trabajador', 'vendedor')

        password = request.form['password'].strip()
        fecha_registro = today_date

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO personas (run, nombre, apellido, fecha_nacimiento, telefono, email, tipo_persona, rol, password, fecha_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (run, nombre, apellido, fecha_nacimiento, telefono, email, tipo_persona, rol, password, fecha_registro))
            conn.commit()
            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("El RUN o el Correo ya están registrados.", "error")
        finally:
            conn.close()

    return render_template('register.html', today_date=today_date)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)