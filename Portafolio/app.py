from flask import Flask, render_template
from connect import get_db

app = Flask(__name__)

def obtener_contenido(seccion):
    db = get_db()
    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT titulo, texto FROM contenido WHERE seccion=%s", (seccion,))
        return cursor.fetchone()

@app.route("/")
def index():
    page = obtener_contenido("manos")
    return render_template("manos.html", page=page)

@app.route("/inicio")
def inicio():
    page = obtener_contenido("index")
    return render_template("index.html", page=page)

@app.route("/sobre-mi")  # ruta limpia
def sobre_mi():
    db = get_db()
    page = obtener_contenido("sobre_mi")

    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM datos_personales LIMIT 1")
        datos = cursor.fetchone()

    return render_template("sobre_mi.html", page=page, datos=datos)

@app.route("/personal")
def personal():
    page = obtener_contenido("personal")
    return render_template("personal.html", page=page)

@app.route("/trayecto")
def trayecto():
    db = get_db()
    page = obtener_contenido("trayecto")

    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM trayecto ORDER BY fecha_inicio DESC")
        lista_trayecto = cursor.fetchall()

    return render_template("trayecto.html", page=page, trayecto=lista_trayecto)

@app.route("/proyectos")
def proyectos():
    db = get_db()
    page = obtener_contenido("proyectos")

    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM proyectos")
        lista_proyectos = cursor.fetchall()

    return render_template("proyectos.html", page=page, proyectos=lista_proyectos)

@app.route("/login")
def login():
    page = obtener_contenido("personal")  # O si querés crear la sección 'login' en contenido
    return render_template("login.html", page=page)

if __name__ == "__main__":
    app.run(debug=True)
