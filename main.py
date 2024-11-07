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