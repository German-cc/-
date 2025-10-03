import json
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__, template_folder='HTML')
app.secret_key = 'mi_secreto'  # Cambia por una clave secreta más segura

# Ruta a nuestro archivo JSON donde almacenamos los usuarios
USERS_FILE = 'users.json'

# Función para cargar los usuarios desde el archivo JSON
def load_users():
    try:
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Función para guardar los usuarios en el archivo JSON
def save_user(username, email, password):
    users = load_users()
    username_lower = username.lower()
    if username_lower in users:
        return False  # Usuario ya existe
    users[username_lower] = {"email": email, "password": password}
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file)
    return True

# Ruta para la página principal (login)
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username'].strip()
        password = request.form['password']
        users = load_users()
        username_lower = username.lower()

        # Verificar si el usuario existe y la contraseña es correcta
        if username_lower in users and users[username_lower]["password"] == password:
            flash('¡Bienvenido!', 'success')
            return redirect(url_for('home', username=username))
        else:
            flash('Credenciales incorrectas. Intenta de nuevo.', 'error')

    return render_template('index.html', active_tab='login')

# Ruta para la página de registro
@app.route("/register", methods=["POST"])
def register():
    username = request.form['username'].strip()
    email = request.form['email'].strip()
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    users = load_users()
    username_lower = username.lower()

    # Verificar si el usuario ya existe
    if username_lower in users:
        flash('El nombre de usuario ya existe.', 'error')
        return redirect(url_for('login'))
    elif password != confirm_password:
        flash('Las contraseñas no coinciden.', 'error')
        return redirect(url_for('login'))
    else:
        if not save_user(username, email, password):
            flash('El nombre de usuario ya existe.', 'error')
            return redirect(url_for('login'))
        flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

# Ruta para cambiar la contraseña
@app.route("/change-password", methods=["POST"])
def change_password():
    username = request.form['username'].strip()
    current_password = request.form['currentPassword']
    new_password = request.form['newPassword']
    confirm_new_password = request.form['confirmNewPassword']

    users = load_users()
    username_lower = username.lower()

    # Verificar si el usuario existe
    if username_lower not in users:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('home', username=username))
    
    # Verificar si la contraseña actual es correcta
    if users[username_lower]["password"] != current_password:
        flash('Contraseña actual incorrecta.', 'error')
        return redirect(url_for('home', username=username))
    
    # Verificar si las nuevas contraseñas coinciden
    if new_password != confirm_new_password:
        flash('Las nuevas contraseñas no coinciden.', 'error')
        return redirect(url_for('home', username=username))
    
    # Actualizar la contraseña
    users[username_lower]["password"] = new_password
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file)
    
    flash('Contraseña cambiada con éxito.', 'success')
    return redirect(url_for('home', username=username))

# Página de inicio después de un login exitoso
@app.route("/home", methods=["GET", "POST"])
def home():
    username = request.args.get('username', '')

    if request.method == "POST":
        # Aquí podrías agregar lógica adicional si es necesario
        flash('Acción realizada correctamente', 'success')
        return redirect(url_for('home', username=username))

    return render_template('index.html', active_tab='home', username=username)

if __name__ == "__main__":
    app.run(debug=True)
