from fastapi import FastAPI, HTTPException
from psycopg2.extras import RealDictCursor
import psycopg2
from pydantic import BaseModel

app = FastAPI()

DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "creta3"

class Tarea(BaseModel):
    nombre_tarea: str
    completado: bool

class TareaEliminar(BaseModel):
    id: int
class TareaCompletar(BaseModel):
    id: int
    completado: bool


class UsuarioVerificar(BaseModel):
    correo_elecronico: str

class UsuarioRegistrar(BaseModel):
    nombre: str
    apellido: str
    correo_electronico: str
    contraseña: str  # La contraseña ya llegará en hash desde el servidor intermedio

@app.post("/verificarUsuario")
async def verificar_usuario(usuario: UsuarioVerificar):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Verificar si el email ya existen en la base de datos
        cur.execute("SELECT correo_electronico FROM usuarios WHERE correo_electronico = %s", (usuario.correo_electronico))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Determinar si el email ya están en uso
        email_exists = any(row['correo_electronico'] == usuario.correo_electronico for row in rows)

        return {"emailExists": email_exists}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/registrarUsuario")
async def registrar_usuario(usuario: UsuarioRegistrar):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()

        # Insertar el nuevo usuario en la base de datos
        cur.execute(
            "INSERT INTO usuarios (nombre, apellido, correo_electronico, contraseña) VALUES (%s, %s, %s, %s)",
            (usuario.nombre, usuario.apellido, usuario.correo_electronico, usuario.contraseña)
        )

        conn.commit()
        cur.close()
        conn.close()

        return {"message": "Usuario registrado exitosamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/obtenerDatos")
async def obtenerDatos():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM tareas;")

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return rows

@app.post("/agregarTarea")
async def agregarTarea(tarea: Tarea):
        conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

        cur = conn.cursor()
        cur.execute(
              "INSERT INTO tareas(nombre_tarea, completado) VALUES (%s, %s)",
              (tarea.nombre_tarea, tarea.completado)
        )

        conn.commit()
        cur.close()
        conn.close()

        return {"message": "Tarea agregada exitosamente"}

@app.delete("/eliminarTarea")
async def eliminarTarea(tarea: TareaEliminar):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        cur = conn.cursor()

        # Ejecutar el DELETE con el ID proporcionado
        cur.execute("DELETE FROM tareas WHERE id = %s", (tarea.id,))

        # Verificar si alguna fila fue afectada
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")

        conn.commit()
        cur.close()
        conn.close()

        return {"message": "Tarea eliminada exitosamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/completarTarea")
async def completarTarea(tarea: TareaCompletar):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        cur = conn.cursor()

        # Ejecutar la consulta UPDATE para cambiar el estado de 'completado'
        cur.execute("UPDATE tareas SET completado = %s WHERE id = %s",
                    (tarea.completado, tarea.id))

        # Verificar si alguna fila fue afectada
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")

        conn.commit()
        conn.commit()
        cur.close()
        cur.close()
        conn.close()

        return {"message": "Tarea actualizada exitosamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))