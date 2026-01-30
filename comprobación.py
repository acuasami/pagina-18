import psycopg2
import sys

# TUS DATOS DE CONEXIÓN DIRECTOS
# He quitado 'channel_binding' porque suele dar errores en Windows/Mac si no tienes configuraciones avanzadas
DB_URI = "postgresql://neondb_owner:npg_LOQTwP86bvYc@ep-floral-meadow-ahobjrmx-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

print("--- INICIANDO PRUEBA DE CONEXIÓN ---")
print(f"Intentando conectar a: {DB_URI.split('@')[1]}") # Imprime solo el host por seguridad

try:
    conn = psycopg2.connect(DB_URI)
    print("✅ ¡CONEXIÓN EXITOSA!")
    
    cur = conn.cursor()
    
    # 1. Verificar si existe la tabla tickets
    print("\n🔍 Buscando tabla 'tickets'...")
    cur.execute("SELECT to_regclass('public.tickets');")
    existe = cur.fetchone()[0]
    
    if existe:
        print("✅ La tabla 'tickets' EXISTE.")
        
        # 2. Verificar datos
        cur.execute("SELECT COUNT(*) FROM tickets;")
        total = cur.fetchone()[0]
        print(f"📊 Tienes {total} tickets registrados.")
        
        # 3. Verificar columnas
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'tickets';")
        cols = cur.fetchall()
        print("📝 Columnas encontradas:", [c[0] for c in cols])
        
    else:
        print("❌ ERROR: Te conectaste a la BD, pero la tabla 'tickets' NO EXISTE.")
        print("   Las tablas que sí existen son:")
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tablas = cur.fetchall()
        for t in tablas:
            print(f"   - {t[0]}")

    conn.close()

except psycopg2.OperationalError as e:
    print("\n❌ FALLÓ LA CONEXIÓN (Error Operacional):")
    print(e)
    print("\nSOLUCIÓN POSIBLE:")
    if "password authentication failed" in str(e):
        print("-> Tu contraseña es incorrecta.")
    elif "could not translate host name" in str(e):
        print("-> El 'host' está mal escrito o no tienes internet.")
    elif "ssl" in str(e):
        print("-> Problema de SSL. Neon requiere SSL activado.")

except Exception as e:
    print(f"\n❌ ERROR DESCONOCIDO: {e}")

print("\n--- FIN DE LA PRUEBA ---")