from flask import Flask, render_template, request, redirect, session
from connect import get_connection
from werkzeug.security import check_password_hash
from flask import url_for

app = Flask(__name__)
app.secret_key = "clave-re-privada"  # Cambiar después

# Función para obtener texto de sección
def get_section(section):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contenido WHERE seccion=%s", (section,))
    data = cursor.fetchone()
    conn.close()
    return data

# Página principal
@app.route("/")
def index():
    data = get_section("index")
    return render_template("index.html", data=data)

@app.route("/sobre_mi")
def sobre_mi():
    data = get_section("sobre_mi")
    return render_template("sobre_mi.html", data=data)

@app.route("/personal")
def personal():
    data = get_section("personal")
    return render_template("personal.html", data=data)

@app.route("/trayecto")
def trayecto():
    data = get_section("trayecto")
    return render_template("trayecto.html", data=data)

@app.route("/proyectos")
def proyectos():
    data = get_section("proyectos")
    return render_template("proyectos.html", data=data)

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuario WHERE username=%s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user"] = username
            return redirect("/")
        else:
            return "Login incorrecto"

    return render_template("login.html")

# Editar secciones
@app.route("/editar/<seccion>", methods=["GET", "POST"])
def editar(seccion):
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        nuevo_texto = request.form["texto"]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE contenido SET texto=%s WHERE seccion=%s", (nuevo_texto, seccion))
        conn.commit()
        conn.close()
        return redirect(url_for(seccion))

    data = get_section(seccion)
    return render_template("editar.html", data=data)
    
# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
