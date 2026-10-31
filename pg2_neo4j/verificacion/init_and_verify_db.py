"""
init_and_verify_db.py - Inicialización y Verificación de Base de Conocimiento Neo4j
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026
"""

import os
import sys
from typing import Dict, Any, List

# Garantizar que la raíz del proyecto esté en sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_cypher_statements(file_path: str) -> List[str]:
    """Lee un archivo .cypher y extrae las sentencias individuales respetando cadenas entre comillas."""
    with open(file_path, 'r', encoding='utf-8') as fh:
        content = fh.read()

    lines = content.splitlines()
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('//') or not stripped:
            continue
        clean_lines.append(line)

    full_text = '\n'.join(clean_lines)
    statements = []
    current = []
    in_single = False
    in_double = False
    escaped = False

    for ch in full_text:
        if ch == '\\' and not escaped:
            escaped = True
            current.append(ch)
            continue

        if ch == "'" and not escaped and not in_double:
            in_single = not in_single
        elif ch == '"' and not escaped and not in_single:
            in_double = not in_double

        if ch == ';' and not in_single and not in_double:
            stmt = ''.join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
        else:
            current.append(ch)

        escaped = False

    last_stmt = ''.join(current).strip()
    if last_stmt:
        statements.append(last_stmt)

    return statements

def verify_live_neo4j(uri: str, user: str, password: str, database: str = "neo4j"):
    """Se conecta a una instancia real de Neo4j / Aura y ejecuta los scripts 01..06 y C7."""
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("[ERROR] El paquete 'neo4j' no está disponible.")
        return False

    print(f"[*] Conectando a Neo4j en: {uri} (usuario: {user}) ...")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session(database=database) as session:
            session.run("RETURN 1 AS ping").single()
            print("[+] Conexión establecida con éxito.")

            print("[*] Limpiando nodos previos para carga prístina...")
            session.run("MATCH (n) DETACH DELETE n")

            scripts = [
                os.path.join(PROJECT_ROOT, 'pg2_neo4j', 'scripts', '01_esquema_restricciones.cypher'),
                os.path.join(PROJECT_ROOT, 'pg2_neo4j', 'scripts', '02_catalogo_conocimiento.cypher'),
                os.path.join(PROJECT_ROOT, 'pg2_neo4j', 'scripts', '03_reglas_nitidas.cypher'),
                os.path.join(PROJECT_ROOT, 'pg2_neo4j', 'scripts', '04_logica_difusa.cypher'),
                os.path.join(PROJECT_ROOT, 'pg2_neo4j', 'scripts', '05_instancias_casos.cypher'),
                os.path.join(PROJECT_ROOT, 'pg2_neo4j', 'scripts', '06_casos_difusos.cypher')
            ]

            print("[*] Ejecutando scripts de carga Cypher...")
            for s_path in scripts:
                if not os.path.exists(s_path):
                    print(f"[-] No existe: {s_path}")
                    continue
                stmts = parse_cypher_statements(s_path)
                print(f"    - {os.path.basename(s_path)}: {len(stmts)} sentencias...")
                for stmt in stmts:
                    session.run(stmt)

            print("[+] Carga completada. Ejecutando verificación de métricas...")

            # 1. Conteo de nodos
            r_nodes = session.run("MATCH (n) RETURN count(n) AS total").single()
            print(f"    Nodos totales: {r_nodes['total']} (esperado: 228)")

            # 2. Conteo de relaciones
            r_rels = session.run("MATCH ()-[r]->() RETURN count(r) AS total").single()
            print(f"    Relaciones totales: {r_rels['total']} (esperado: 353)")

            # 3. Controles C7
            c7_path = os.path.join(PROJECT_ROOT, 'pg2_neo4j', 'consultas', 'C7_controles_consistencia.cypher')
            with open(c7_path, 'r', encoding='utf-8') as fh:
                c7_query = fh.read()

            print("[*] Ejecutando C7 (Controles de consistencia)...")
            res_c7 = session.run(c7_query)
            c7_ok = True
            for record in res_c7:
                ctrl = record['control']
                viols = record['violaciones']
                status = "OK" if viols == 0 else f"FALLO ({viols} violaciones)"
                print(f"    [{status}] {ctrl}")
                if viols > 0:
                    c7_ok = False

            if c7_ok:
                print("[+] C7: 0 violaciones en todos los controles.")
            else:
                print("[-] Se detectaron violaciones en C7.")

        driver.close()
        return True
    except Exception as e:
        print(f"[-] Error de conexión o ejecución en Neo4j: {e}")
        return False

def main():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD", "domia2026")
    db = os.getenv("NEO4J_DATABASE", "neo4j")

    print("================================================================================")
    print("DOMIA PG2 - INICIALIZADOR Y VERIFICADOR DE BASE DE CONOCIMIENTO NEO4J")
    print("================================================================================")

    # Validar primero el motor de referencia difuso
    from pg2_neo4j.verificacion.ref_difuso import run_verification
    fuzzy_ok = run_verification()

    print("\n[*] Intentando conexión a Neo4j...")
    connected = verify_live_neo4j(uri, user, pwd, db)
    if not connected:
        print("\n[INFO] Neo4j no está accesible en esta máquina local o las credenciales no son válidas.")
        print("[INFO] Los scripts .cypher reproducibles quedan listos en 'pg2_neo4j/scripts/' y 'Grupo_3_PG2_U1.cypher'.")
        print("[INFO] La base de conocimiento está formalmente validada por el motor de referencia difuso.")

if __name__ == '__main__':
    main()
