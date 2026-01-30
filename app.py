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
        cur.execute("SELECT COUNT(*) as t FROM tickets")
        kpis['total'] = cur.fetchone()['t']
        
        # Filtros basados en tu columna 'estado'
        cur.execute("SELECT COUNT(*) as c FROM tickets WHERE estado = 'PENDIENTE'")
        kpis['abiertos'] = cur.fetchone()['c']
        
        cur.execute("SELECT COUNT(*) as c FROM tickets WHERE estado = 'EN_ATENCION'")
        kpis['atencion'] = cur.fetchone()['c']
        
        cur.execute("SELECT COUNT(*) as c FROM tickets WHERE estado = 'ESPERA_REFACCION'")
        kpis['refaccion'] = cur.fetchone()['c']
        
        cur.execute("SELECT COUNT(*) as c FROM tickets WHERE estado = 'RESUELTO'")
        kpis['resueltos'] = cur.fetchone()['c']
    except Exception as e:
        print(f"Error KPIs: {e}")
    finally:
        conn.close()
    return jsonify(kpis)

@app.route('/api/dashboard/tickets')
def get_tickets():
    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    cur = conn.cursor()
    try:
        # Unimos tickets con clientes, empresas y fallas para ver nombres, no IDs
        query = """
            SELECT 
                t.id, 
                e.empresa, 
                f.falla as tipo_falla,
                'Sin asignar' as tecnico, 
                TO_CHAR(t.fecha_creacion, 'DD/MM/YYYY') as fecha_fmt, 
                t.estado 
            FROM tickets t
            JOIN cliente c ON t.id_clientes = c.id
            JOIN empresas e ON c.id_empresa = e.id
            JOIN falla_reportada f ON t.id_falla_reportada = f.id
            ORDER BY t.fecha_creacion DESC LIMIT 10
        """
        cur.execute(query)
        return jsonify(cur.fetchall())
    except Exception as e:
        print(f"Error Tabla: {e}")
        return jsonify([]), 500
    finally:
        conn.close()
        
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
