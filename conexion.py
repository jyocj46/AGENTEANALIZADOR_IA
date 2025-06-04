import cx_Oracle
from typing import Optional

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
