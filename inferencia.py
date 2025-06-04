from conexion import conectar_oracle
import cx_Oracle
from typing import Tuple, Optional

def buscar_solucion(palabras_clave, tipo_equipo):
    conn = None
    cursor = None
    try:
        conn = conectar_oracle()
        cursor = conn.cursor()

        # Construimos condiciones dinámicas para palabras clave
        condiciones = []
        params = {}
        for i, palabra in enumerate(palabras_clave):
            key = f"palabra{i}"
            condiciones.append(f"(LOWER(PALABRAS_CLAVE) LIKE '%' || :{key} || '%')")
            params[key] = palabra.lower()

        condiciones_sql = " OR ".join(condiciones)

        query = f"""
            SELECT 
                SINTOMA, 
                CAUSA_PROBABLE, 
                SOLUCION,
                SUM(
                    CASE
                        {"".join([
                            f"WHEN LOWER(PALABRAS_CLAVE) LIKE '%' || :palabra{i} || '%' THEN 3 "
                            f"WHEN LOWER(SINTOMA) LIKE '%' || :palabra{i} || '%' THEN 2 "
                            f"WHEN LOWER(CAUSA_PROBABLE) LIKE '%' || :palabra{i} || '%' THEN 1 "
                            for i in range(len(palabras_clave))
                        ])}
                        ELSE 0
                    END
                ) AS RELEVANCIA
            FROM C##AGENTE.FALLAS_INFORMATICAS
            WHERE ({condiciones_sql})
              AND (TIPO_EQUIPO = :tipo_equipo OR TIPO_EQUIPO = 'ambos')
            GROUP BY SINTOMA, CAUSA_PROBABLE, SOLUCION
            ORDER BY RELEVANCIA DESC
        """

        # Añadir tipo de equipo al diccionario de parámetros
        params["tipo_equipo"] = tipo_equipo.lower()

        cursor.execute(query, params)
        resultado = cursor.fetchone()
        return resultado[:3] if resultado else (None, None, None)

    except cx_Oracle.DatabaseError as e:
        print(f"Error de base de datos: {e}")
        return None, None, None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def buscar_solucion_generica(palabras_clave: list, conn: cx_Oracle.Connection) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Búsqueda secundaria con términos más generales cuando no hay coincidencia exacta.
    """
    try:
        cursor = conn.cursor()
        
        # Consulta genérica para problemas relacionados
        query = """
            SELECT SINTOMA, CAUSA_PROBABLE, SOLUCION
            FROM C##AGENTE.FALLAS_INFORMATICAS
            WHERE CATEGORIA = (
                SELECT CATEGORIA 
                FROM C##AGENTE.FALLAS_INFORMATICAS
                WHERE """
        
        condiciones = []
        params = {}
        for i, palabra in enumerate(palabras_clave):
            condiciones.append(f"LOWER(PALABRAS_CLAVE) LIKE '%' || :gp{i} || '%'")
            params[f"gp{i}"] = palabra.lower()

        query += " OR ".join(condiciones)
        query += " FETCH FIRST 1 ROWS ONLY) ORDER BY PRIORIDAD DESC FETCH FIRST 1 ROWS ONLY"

        cursor.execute(query, params)
        resultado = cursor.fetchone()
        
        return resultado if resultado else (None, None, None)
        
    except Exception as e:
        print(f" Error en búsqueda genérica: {e}")
        return None, None, None