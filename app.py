from flask import Flask, flash, render_template, request, redirect , url_for
from flask_mysqldb import MySQL
import secrets
import string


app = Flask(__name__, static_url_path='/static')
app=Flask(__name__)

#coneccion de Mysql
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]="motorojava14"
app.config["MYSQL_DB"]="contrasenas"
mysql1=MySQL(app)

# config
app.secret_key="mysecretkey"


@app.route('/')
def Casa():
    return render_template("Casa.html")

@app.route("/Almacen", methods=["GET"])
def Almacen():
    nombre = request.args.get("nombre")
    apellido = request.args.get("apellido")
    cur = mysql1.connect.cursor()
    cur.execute("""
    SELECT datos.ID, datos.nombre, datos.apellido, datos.red_social, datos.correo, pasword.contrasena, historial.fecha_hora, historial.contrasena_anterior
    FROM datos
    JOIN pasword ON datos.ID = pasword.ID
    LEFT JOIN historial ON datos.ID = historial.ID
    WHERE datos.nombre = %s AND datos.apellido = %s
""", (nombre, apellido))
    datos = cur.fetchall()
    
    if datos:
        flash("Persona econtrada")
    else:
        flash("Busque una nueva persona")

    return render_template("ALMACEN.html", datas=datos)
    


@app.route("/Casa")
def Casa1():
    return render_template("Casa.html")

@app.route("/Ingreso")
def Index():
    cur= mysql1.connect.cursor()
    cur.execute("SELECT * FROM datos ")
    datos = cur.fetchall()
    return render_template("index.html", datas = datos)

@app.route("/add_persona", methods=["POST"])
def add_persona():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        red_social=request.form["red_social"]
        correo=request.form["correo"]
        cur = mysql1.connection.cursor()
        cur.execute("INSERT INTO datos (nombre,apellido,correo,red_social) VALUES (%s,%s,%s,%s)", (nombre,apellido,correo,red_social))
        mysql1.connection.commit()
        flash("Persona agregada correctamente")
        return redirect (url_for("Index"))

@app.route("/Eliminar/<string:ID>")
def del_persona(ID):
    cur= mysql1.connection.cursor()
    cur.execute("DELETE FROM datos WHERE id= {0}".format(ID))
    mysql1.connection.commit()
    flash("Persona eliminada correctamente")
    return redirect(url_for("Index"))

@app.route("/Editar/<ID>")
def edit_persona(ID):
    cur=mysql1.connection.cursor()
    cur.execute("SELECT * FROM datos WHERE id= %s", (ID))
    data = cur.fetchall()
    return render_template("edit-personas.html", personas = data[0])

@app.route("/update/<ID>", methods = ["POST"])
def update_persona(ID):
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        red_social = request.form["red_social"]
        correo = request.form["correo"]
        cur= mysql1.connection.cursor()
        cur.execute(""" 
        UPDATE datos
        SET nombre = %s,
            apellido = %s,
            red_social = %s,
            correo = %s                                
        WHERE ID = %s
    """, (nombre,apellido,red_social,correo,ID))
        mysql1.connection.commit()
        flash("la persona se ha actualizado")
        return redirect(url_for("Almacen"))


    
@app.route("/guardar_contrasena/<string:ID>", methods=["POST"])
def guardar_contrasena(ID):
    longitud = int(request.form.get("longitud"))  # Obtén la longitud desde el formulario
    contrasena_nueva = generar_contrasena_aleatoria(longitud)
    # Verifica si el ID_persona existe antes de insertar la contraseña
    cursor = mysql1.connection.cursor()
    cursor.execute("SELECT ID, contrasena FROM pasword WHERE ID = %s", (ID,))
    resultado = cursor.fetchone()
    if resultado:
        contrasena_anterior = resultado[1]
        cursor.execute("UPDATE pasword SET contrasena = %s WHERE ID = %s", (contrasena_nueva, ID))
        cursor.execute("UPDATE historial SET fecha_hora = NOW(), contrasena_anterior = %s WHERE ID = %s", (contrasena_anterior, ID))
        mysql1.connection.commit()
        flash("Contraseña actualizada correctamente")
        return redirect(url_for("Almacen"))
    else:
        flash("ID no encontrado. No se actualizó la contraseña.")
        return redirect(url_for("Almacen"))

def generar_contrasena_aleatoria(longitud):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    contrasena = ''.join(secrets.choice(caracteres) for _ in range(longitud))
    return contrasena

if __name__ =="__main__":
    app.run (port= 3000,debug = True)

