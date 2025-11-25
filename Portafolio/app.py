from flask import Flask, render_template, request, redirect, session, flash, url_for
import os
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from connect import get_db

app = Flask(__name__)
app.secret_key = "parangutirimicuaro"


def obtener_contenido(seccion):
    db = get_db()
    with db.cursor(dictionary=True) as cursor:
        cursor.execute(
            "SELECT titulo, texto FROM contenido WHERE seccion=%s",
            (seccion,)
        )
        return cursor.fetchone()

@app.route("/")
def index():
    page = obtener_contenido("manos")
    return render_template("manos.html", page=page)

@app.route("/inicio")
def inicio():
    db = get_db()

    page = obtener_contenido("index")

    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM datos_personales LIMIT 1")
        datos = cursor.fetchone()

    return render_template("index.html", page=page, datos=datos)

@app.route("/sobre-mi")
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
        cursor.execute(
            "SELECT * FROM trayecto ORDER BY fecha_inicio DESC"
        )
        lista_trayecto = cursor.fetchall()

    return render_template(
        "trayecto.html",
        page=page,
        trayecto=lista_trayecto
    )

@app.route("/proyectos")
def proyectos():
    db = get_db()
    page = obtener_contenido("proyectos")

    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM proyectos")
        lista_proyectos = cursor.fetchall()

    return render_template(
        "proyectos.html",
        page=page,
        proyectos=lista_proyectos
    )

@app.route("/gustos")
def gustos():
    page = obtener_contenido("gustos")
    return render_template("gustos.html", page=page)

@app.route("/blog")
def blog():
    page = obtener_contenido("blog")
    return render_template("blog.html", page=page)

@app.route("/login", methods=["GET", "POST"])
def login():
    page = obtener_contenido("login")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        with db.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE username=%s", (username,))
            user = cursor.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Bienvenido, ¡login exitoso!", "success")
            return redirect("/inicio")

        flash("Usuario o contraseña incorrectos", "danger")

    return render_template("login.html", page=page)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

class IndexForm(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired()])
    texto = TextAreaField("Texto")
    submit = SubmitField("Guardar")



@app.route("/admin/<tabla>")
@login_required
def admin_listado(tabla):
    db = get_db()

    with db.cursor(dictionary=True) as cur:
        cur.execute(f"SELECT * FROM {tabla}")
        filas = cur.fetchall()

    return render_template("admin_listado.html", tabla=tabla, filas=filas)

@app.route("/admin/<tabla>/editar/<int:id>", methods=["GET", "POST"])
@login_required
def admin_editar(tabla, id):
    db = get_db()

    with db.cursor(dictionary=True) as cur:
        cur.execute(f"SELECT * FROM {tabla} WHERE id = %s", (id,))
        fila = cur.fetchone()

    if request.method == "POST":
        datos = request.form.to_dict()
        
        campos = ", ".join([f"{k}=%s" for k in datos.keys()])
        valores = list(datos.values())
        valores.append(id)

        with db.cursor() as cur:
            cur.execute(
                f"UPDATE {tabla} SET {campos} WHERE id = %s", valores
            )
        db.commit()

        return redirect(url_for("admin_listado", tabla=tabla))

    return render_template("admin_editar.html", tabla=tabla, fila=fila)

@app.route("/admin/<tabla>/nuevo", methods=["GET", "POST"])
@login_required
def admin_nuevo(tabla):
    if request.method == "POST":
        datos = request.form.to_dict()

        campos = ", ".join(datos.keys())
        placeholders = ", ".join(["%s"] * len(datos))
        valores = list(datos.values())

        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                f"INSERT INTO {tabla} ({campos}) VALUES ({placeholders})",
                valores
            )
        db.commit()

        return redirect(url_for("admin_listado", tabla=tabla))

    return render_template("admin_nuevo.html", tabla=tabla)

@app.route("/admin/<tabla>/eliminar/<int:id>")
@login_required
def admin_eliminar(tabla, id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(f"DELETE FROM {tabla} WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for("admin_listado", tabla=tabla))




@app.context_processor
def inject_user():
    return dict(session=session)

if __name__ == "__main__":
    app.run(debug=True)
