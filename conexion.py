import cx_Oracle
from typing import Optional

def guardar_documento(nombre_archivo: str, contenido: str, resumen: str, tipo_documento: str):
    try:
        conn = conectar_oracle()
        if not conn:
            print("❌ No se pudo conectar para guardar el documento.")
            return

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO C##AGENTE.DOCUMENTOS_ANALIZADOS (
                NOMBRE_ARCHIVO, CONTENIDO, RESUMEN, TIPO_DOCUMENTO
            ) VALUES (
                :nombre, :contenido, :resumen, :tipo
            )
        """, {
            "nombre": nombre_archivo,
            "contenido": contenido,
            "resumen": resumen,
            "tipo": tipo_documento
        })
        conn.commit()
        print("✅ Documento guardado en la base de datos.")
    except Exception as e:
        print(f"❌ Error al guardar documento: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def conectar_oracle() -> Optional[cx_Oracle.Connection]:
    try:
        dsn = cx_Oracle.makedsn(
            host="localhost",
            port=1521,
            service_name="xe"
        )
        
        # Conexión normal sin SYSDBA
        conn = cx_Oracle.connect(
            user="C##AGENTE",
            password="123456",
            dsn=dsn,
            encoding="UTF-8"
        )
        
        # Verificar conexión
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM DUAL")
            if cursor.fetchone()[0] != 1:
                raise cx_Oracle.DatabaseError("Verificación de conexión fallida")
        return conn
        
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"❌ Error Oracle (Code: {error.code}):")
        print(f"Message: {error.message}")
        print(f"Context: {error.context}")
        print("Solución: Verificar privilegios con 'GRANT CREATE SESSION TO C##AGENTE'")
        return None
    
def buscar_documentos_relacionados(palabras_clave: list) -> list:
    conn = conectar_oracle()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        condiciones = []
        params = {}
        for i, palabra in enumerate(palabras_clave):
            key = f"pal{i}"
            condiciones.append(f"(LOWER(RESUMEN) LIKE '%' || :{key} || '%')")
            params[key] = palabra.lower()

        sql = f"""
            SELECT RESUMEN FROM C##AGENTE.DOCUMENTOS_ANALIZADOS
            WHERE {" OR ".join(condiciones)}
            FETCH FIRST 3 ROWS ONLY
        """

        cursor.execute(sql, params)
        resultados = cursor.fetchall()
        resumenes = [str(r[0].read()) if hasattr(r[0], 'read') else str(r[0]) for r in resultados]
        return resumenes

    except Exception as e:
        print(f"❌ Error al buscar en memoria semántica: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

