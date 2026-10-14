import sqlite3
from flask import Flask, request, jsonify, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DB_NAME = "database.db"

# ---------------------------------------------------------
# Función para inicializar la base de datos SQLite
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Creamos la tabla de usuarios si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Inicializamos la base de datos al arrancar
init_db()

# ---------------------------------------------------------
# 1. Registro de Usuarios (POST /registro)
# ---------------------------------------------------------
@app.route('/registro', methods=['POST'])
def registro():
    datos = request.get_json()
    
    if not datos:
        return jsonify({"error": "Se requieren datos en formato JSON"}), 400
    
    usuario = datos.get('usuario')
    # Permite leer 'contraseña' o 'contrasena'
    password = datos.get('contraseña') or datos.get('contrasena')

    if not usuario or not password:
        return jsonify({"error": "Debe proporcionar usuario y contraseña"}), 400

    # Hasheamos la contraseña antes de guardarla en la base de datos
    password_hashed = generate_password_hash(password)

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)", (usuario, password_hashed))
        conn.commit()
        conn.close()
        return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "El nombre de usuario ya existe"}), 400
    except Exception as e:
        return jsonify({"error": f"Error en el servidor: {str(e)}"}), 500

# ---------------------------------------------------------
# 2. Inicio de Sesión (POST /login)
# ---------------------------------------------------------
@app.route('/login', methods=['POST'])
def login():
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "Se requieren datos en formato JSON"}), 400

    usuario = datos.get('usuario')
    password = datos.get('contraseña') or datos.get('contrasena')

    if not usuario or not password:
        return jsonify({"error": "Debe proporcionar usuario y contraseña"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT contrasena FROM usuarios WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()
    conn.close()

    # Si el usuario no existe o la contraseña no coincide
    if resultado is None or not check_password_hash(resultado[0], password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    return jsonify({
        "mensaje": f"¡Bienvenido {usuario}! Inicio de sesión exitoso.",
        "acceso_tareas": "/tareas"
    }), 200

# ---------------------------------------------------------
# 3. Gestión de Tareas (GET /tareas)
# ---------------------------------------------------------
@app.route('/tareas', methods=['GET'])
def tareas():
    html_bienvenida = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Bienvenido a las Tareas</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f6f9;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                box-sizing: border-box;
            }
            .img-logo {
                max-width: 130px;
                height: auto;
                border-radius: 8px;
                margin-bottom: 25px;
            }
            .card {
                background: white;
                padding: 28px 45px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.06);
                text-align: center;
                max-width: 520px;
                width: 100%;
                margin-bottom: 25px;
                box-sizing: border-box;
            }
            h1 {
                color: #2c3e50;
                font-size: 24px;
                margin: 0 0 10px 0;
            }
            p {
                color: #7f8c8d;
                font-size: 14px;
                margin: 0;
            }
            .img-gato {
                max-width: 210px;
                height: auto;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <img src="/static/logo.png" alt="Logo IFTS 29" class="img-logo">
        <div class="card">
            <h1>¡Bienvenido al Panel de Tareas!</h1>
            <p>Has accedido correctamente al sistema de gestión de tareas.</p>
        </div>
        <img src="/static/gato.png" alt="Gato" class="img-gato">
    </body>
    </html>
    """
    return render_template_string(html_bienvenida)

# ---------------------------------------------------------
# Punto de entrada principal
# ---------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
