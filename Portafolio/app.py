# app.py
from flask import Flask, render_template, request, redirect, session, flash, url_for, abort, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
import time

from connect import get_db

app = Flask(__name__)
app.secret_key = "parangutirimicuaro"

# -------------------
# CONFIG
# -------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "svg", "pdf", "mp3", "mp4", "ogg"}

TABLAS_CONFIG = {
    "contenido": {"label": "Contenido simple", "editable": ["titulo", "texto", "seccion"]},
    "datos_personales": {"label": "Datos personales", "editable": ["nombre", "descripcion", "avatar_url", "fondo_url", "edad", "pais", "ocupacion"]},
    "habilidades": {"label": "Habilidades", "editable": ["nombre", "tipo", "nivel", "icono_url"]},
    "gustos_categorias": {"label": "Gustos (categorías)", "editable": ["nombre", "descripcion"]},
    "gustos_items": {"label": "Gustos (items)", "editable": ["categoria_id", "nombre", "descripcion", "imagen_url", "ranking"]},
    "galeria": {"label": "Galería", "editable": ["titulo", "descripcion", "imagen_url"]},
    "trayecto": {"label": "Trayecto", "editable": ["titulo", "descripcion", "fecha_inicio", "fecha_fin", "icono_url"]},
    "proyectos": {"label": "Proyectos", "editable": ["nombre", "descripcion", "link", "imagen_url", "fecha"]},
    "proyectos_tecnologias": {"label": "Proyectos - Tecnologías", "editable": ["proyecto_id", "tecnologia"]},
    "posts": {"label": "Blog - Posts", "editable": ["titulo", "contenido", "fecha", "portada_url"]},
    "posts_multimedia": {"label": "Blog - Multimedia", "editable": ["post_id", "tipo", "url", "descripcion"]},
    "contacto": {"label": "Contacto", "editable": ["tipo", "valor", "icono_url"]}
}

# -------------------
# UTIL
# -------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    filename = secure_filename(file_storage.filename)
    if filename == "":
        return None
    if not allowed_file(filename):
        return None
    ts = str(int(time.time()))
    dest = f"{ts}_{filename}"
    path = os.path.join(app.config["UPLOAD_FOLDER"], dest)
    file_storage.save(path)
    return f"/static/uploads/{dest}"

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

# -------------------
# OBTENER CONTENIDO
# -------------------
def obtener_contenido(seccion):
    db = get_db()
    with db.cursor(dictionary=True) as c:
        c.execute("SELECT titulo, texto, seccion FROM contenido WHERE seccion=%s", (seccion,))
        return c.fetchone()

# -------------------
# RUTAS PÚBLICAS
# -------------------
@app.route("/")
def manos():
    page = obtener_contenido("manos") or {}
    return render_template("manos.html", datos=page)

@app.route("/inicio")
def inicio():
    db = get_db()
    page = obtener_contenido("index") or {}

    with db.cursor(dictionary=True) as c:
        c.execute("SELECT * FROM datos_personales LIMIT 1")
        persona = c.fetchone()

    return render_template("index.html", datos=page, persona=persona)

@app.route("/sobre-mi")
def sobre_mi():
    db = get_db()
    page = obtener_contenido("sobre_mi") or {}

    with db.cursor(dictionary=True) as c:
        c.execute("SELECT * FROM datos_personales LIMIT 1")
        persona = c.fetchone()

    return render_template("sobre_mi.html", datos=page, persona=persona)

@app.route("/blog")
def blog():
    db = get_db()
    page = obtener_contenido("blog") or {}

    with db.cursor(dictionary=True) as c:
        c.execute("SELECT * FROM posts ORDER BY fecha DESC")
        posts = c.fetchall()

    return render_template("blog.html", datos=page, posts=posts)

@app.route("/personal")
def personal():
    page = obtener_contenido("personal") or {}
    return render_template("personal.html", datos=page)

@app.route("/trayecto")
def trayecto():
    db = get_db()
    page = obtener_contenido("trayecto") or {}
    with db.cursor(dictionary=True) as c:
        c.execute("SELECT * FROM trayecto ORDER BY fecha_inicio DESC")
        lista = c.fetchall()
    return render_template("trayecto.html", datos=page, trayecto=lista)

@app.route("/proyectos")
def proyectos():
    db = get_db()
    page = obtener_contenido("proyectos") or {}
    with db.cursor(dictionary=True) as c:
        c.execute("SELECT * FROM proyectos")
        lista = c.fetchall()
    return render_template("proyectos.html", datos=page, proyectos=lista)

@app.route("/gustos")
def gustos():
    page = obtener_contenido("gustos") or {}
    return render_template("gustos.html", datos=page)

# -------------------
# LOGIN
# -------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    page = obtener_contenido("login") or {}
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        db = get_db()
        with db.cursor(dictionary=True) as c:
            c.execute("SELECT * FROM usuarios WHERE username=%s", (username,))
            user = c.fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/admin")
        flash("Usuario o contraseña incorrectos", "danger")
    return render_template("login.html", datos=page)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# -------------------
# ADMIN INDEX
# -------------------
@app.route("/admin")
@login_required
def admin_index():
    tablas = [{"name": t, "label": cfg["label"]} for t, cfg in TABLAS_CONFIG.items()]
    return render_template("admin_index.html", tablas=tablas)

# -------------------
# LISTAR / NUEVO / ELIMINAR (GENÉRICO)
# -------------------
SECCION_RUTAS = {
    "index": "inicio",
    "sobre_mi": "sobre_mi",
    "personal": "personal",
    "contacto": "contacto",
    "blog": "blog"
}

@app.route("/admin/<tabla>")
@login_required
def admin_listado(tabla):
    if tabla not in TABLAS_CONFIG:
        abort(404)
    db = get_db()
    with db.cursor(dictionary=True) as c:
        c.execute(f"SELECT * FROM {tabla}")
        filas = c.fetchall()
    return render_template("admin_listado.html", tabla=tabla, filas=filas, config=TABLAS_CONFIG[tabla])

@app.route("/admin/<tabla>/nuevo", methods=["GET", "POST"])
@login_required
def admin_nuevo(tabla):
    if tabla not in TABLAS_CONFIG:
        abort(404)
    cfg = TABLAS_CONFIG[tabla]
    campos = cfg["editable"]

    if request.method == "POST":
        datos = {}
        for campo in campos:
            if campo in request.files and request.files[campo].filename:
                datos[campo] = save_file(request.files[campo])
            else:
                datos[campo] = request.form.get(campo) or None

        keys = [k for k in datos if datos[k] is not None]
        vals = [datos[k] for k in keys]
        if keys:
            campos_sql = ", ".join(keys)
            holders = ", ".join(["%s"] * len(keys))
            db = get_db()
            with db.cursor() as c:
                c.execute(f"INSERT INTO {tabla} ({campos_sql}) VALUES ({holders})", vals)
            db.commit()
        return redirect(url_for("admin_listado", tabla=tabla))

    return render_template("admin_nuevo.html", tabla=tabla, campos=campos, config=cfg)

@app.route("/admin/<tabla>/eliminar/<int:row_id>")
@login_required
def admin_eliminar(tabla, row_id):
    if tabla not in TABLAS_CONFIG:
        abort(404)
    db = get_db()
    with db.cursor() as c:
        c.execute(f"DELETE FROM {tabla} WHERE id=%s", (row_id,))
    db.commit()
    flash("Elemento eliminado", "info")
    return redirect(url_for("admin_listado", tabla=tabla))

# -------------------
# EDITAR CONTENIDO POR SECCION (CORREGIDO)
# -------------------
@app.route("/admin/contenido/editar/<seccion>", methods=["GET", "POST"])
@login_required
def admin_contenido_editar(seccion):
    db = get_db()
    with db.cursor(dictionary=True) as c:
        c.execute("SELECT * FROM contenido WHERE seccion=%s", (seccion,))
        fila = c.fetchone()

    if request.method == "POST":
        titulo = request.form.get("titulo")
        texto = request.form.get("texto")

        if fila:
            with db.cursor() as c:
                c.execute(
                    "UPDATE contenido SET titulo=%s, texto=%s WHERE id=%s",
                    (titulo, texto, fila["id"])
                )
        else:
            with db.cursor() as c:
                c.execute(
                    "INSERT INTO contenido (seccion, titulo, texto) VALUES (%s, %s, %s)",
                    (seccion, titulo, texto)
                )

        db.commit()
        flash("Sección actualizada", "success")
        ruta = SECCION_RUTAS.get(seccion)
        if ruta:
            return redirect(url_for(ruta))
        else:
            return redirect(url_for("inicio"))



    return render_template("admin_contenido_editar.html", seccion=seccion, fila=fila)

# -------------------
# INJECT SESSION
# -------------------
@app.context_processor
def inject_user():
    return dict(session=session)

# -------------------
# RUN
# -------------------
if __name__ == "__main__":
    app.run(debug=True)
