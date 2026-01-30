from flask import Flask, render_template, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

app = Flask(__name__)

# --- CONEXIÓN A LA BASE DE DATOS ---
# Usamos tu link directo para asegurar que no haya errores de lectura
DB_URL = "postgresql://neondb_owner:npg_LOQTwP86bvYc@ep-floral-meadow-ahobjrmx-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

def get_db_connection():
    try:
        conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"\n❌ ERROR REAL DE CONEXIÓN: {e}\n")
        return None

# --- RUTAS DE LAS PÁGINAS ---
@app.route('/')
def login(): return render_template('Login.html')

@app.route('/recuperacion')
def recuperacion(): return render_template('Recuperación.html')

@app.route('/index')
def dashboard(): return render_template('Index.html')

# --- APIS DEL DASHBOARD (CORREGIDAS) ---

@app.route('/api/dashboard/kpis')
def get_kpis():
    conn = get_db_connection()
    if not conn: return jsonify({"total":0}), 500
    cur = conn.cursor()
    
    kpis = {'total':0, 'abiertos':0, 'atencion':0, 'refaccion':0, 'resueltos':0}
    try:
        # 1. Total General
        cur.execute("SELECT COUNT(*) as t FROM tickets")
        kpis['total'] = cur.fetchone()['t']
        
        # 2. Conteo por Estado
        # NOTA: En tu BD el default es 'PENDIENTE', así que lo sumaremos a 'abiertos'
        cur.execute("SELECT COUNT(*) as c FROM tickets WHERE estado = 'PENDIENTE' OR estado = 'ABIERTO'")
        kpis['abiertos'] = cur.fetchone()['c']
        
        cur.execute("SELECT COUNT(*) as c FROM tickets WHERE estado = 'EN_ATENCION'")
        kpis['atencion'] = cur.fetchone()['c']
        
        cur.execute("SELECT COUNT(*) as c FROM tickets WHERE estado = 'ESPERA_REFACCION'")
        kpis['refaccion'] = cur.fetchone()['c']
        
        cur.execute("SELECT COUNT(*) as c FROM tickets WHERE estado = 'RESUELTO'")
        kpis['resueltos'] = cur.fetchone()['c']
        
    except Exception as e:
        print(f"⚠️ Error SQL en KPIs: {e}")
        
    conn.close()
    return jsonify(kpis)

@app.route('/api/dashboard/tickets')
def get_tickets():
    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    cur = conn.cursor()
    data = []
    
    try:
        # --- AQUÍ ESTABA EL ERROR ---
        # Ahora seleccionamos tus columnas reales: id_clientes, num_autobus, fecha_creacion
        # Y las renombramos (alias) para que el HTML las entienda.
        
        query = """
            SELECT 
                id, 
                CAST(id_clientes AS VARCHAR) as empresa,  -- Mostramos el ID del cliente temporalmente
                num_autobus as tipo_falla,                -- Usamos num_autobus en lugar de tipo falla por ahora
                'Por Asignar' as tecnico,                 -- Tu tabla tickets NO tiene columna técnico
                TO_CHAR(fecha_creacion, 'DD/MM/YYYY') as fecha_fmt, 
                estado 
            FROM tickets 
            ORDER BY fecha_creacion DESC 
            LIMIT 10
        """
        cur.execute(query)
        data = cur.fetchall()
        
    except Exception as e:
        print(f"⚠️ Error SQL en Tabla Tickets: {e}")
        # Si falla, devolvemos lista vacía para no romper la página
        data = []
        
    conn.close()
    return jsonify(data)

# --- APIS VACÍAS (Para que no marquen error las otras pestañas) ---
@app.route('/api/incidencias')
def api_1(): return jsonify([])
@app.route('/api/catalogo/<tipo>')
def api_2(tipo): return jsonify([])
@app.route('/api/tecnicos')
def api_3(): return jsonify([])
@app.route('/api/clientes')
def api_4(): return jsonify([])

if __name__ == '__main__':
    # El puerto 5000 es el estándar
    app.run(debug=True, port=5000)