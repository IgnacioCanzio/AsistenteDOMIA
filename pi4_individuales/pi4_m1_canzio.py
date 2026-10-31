"""
pi4_individuales/pi4_m1_canzio.py - Script Individual de Evaluación PI4
Responsable: Ignacio Canzio (Submódulo M1: Interpretación Semántica y Diálogo)
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026
"""

import sys
import os
import json

# Forzar salida en UTF-8 en Windows PowerShell y agregar raíz al path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.m1_interpretacion import modulo_m1

CASOS_M1 = [
    {
        'id': 'M1_CASO_1',
        'nombre': 'Extracción unívoca y clara (Caso estándar Depto 101)',
        'inmueble_id': 'inm101',
        'relato': 'Hola, no tengo agua caliente en la ducha desde que llegué.',
        'esperado': 'reporte_emitido'
    },
    {
        'id': 'M1_CASO_2',
        'nombre': 'Extracción cerradura digital (Depto 102)',
        'inmueble_id': 'inm102',
        'relato': 'El teclado de la cerradura no reacciona al poner la clave y no puedo entrar.',
        'esperado': 'reporte_emitido'
    },
    {
        'id': 'M1_CASO_3',
        'nombre': 'Ambigüedad de artefacto en Depto 104 (Gas vs Eléctrico)',
        'inmueble_id': 'inm104',
        'relato': 'No anda el agua caliente en el departamento.',
        'esperado': 'pregunta_aclaratoria'
    },
    {
        'id': 'M1_CASO_4',
        'nombre': 'Climatización en Depto 103',
        'inmueble_id': 'inm103',
        'relato': 'El split tira aire caliente en vez de frío.',
        'esperado': 'reporte_emitido'
    },
    {
        'id': 'M1_CASO_5',
        'nombre': 'Detección crítica de seguridad (Olor a gas Depto 105)',
        'inmueble_id': 'inm105',
        'relato': 'Siento un fuerte olor a gas en la cocina.',
        'esperado': 'emergencia'
    },
    {
        'id': 'M1_CASO_ABSURDO',
        'nombre': 'Consulta fuera de dominio (Regla I13)',
        'inmueble_id': 'inm101',
        'relato': 'Hola, me podés recomendar los mejores restaurantes de Mendoza para ir a cenar esta noche?',
        'esperado': 'fuera_de_dominio'
    }
]

def run_pi4_m1_tests():
    print("=" * 80)
    print("EJECUCIÓN DE PRUEBAS PI4 - SUBMÓDULO M1 (Ignacio Canzio)")
    print("Interpretación Semántica, Suficiencia Difusa Mamdani y Barrera de Seguridad")
    print("=" * 80)

    total = len(CASOS_M1)
    passed = 0

    for i, c in enumerate(CASOS_M1, 1):
        print(f"\n[{i}/{total}] Test {c['id']}: {c['nombre']}")
        print(f"  Inmueble: {c['inmueble_id']}")
        print(f"  Relato Huésped: \"{c['relato']}\"")

        tipo_ev, reporte, eval_m1, extra = modulo_m1.procesar_relato(
            relato=c['relato'],
            inmueble_id=c['inmueble_id']
        )

        print(f"  -> Resultado: {tipo_ev}")
        if reporte:
            print(f"     Artefacto detectado: {reporte.artefacto_id}")
            print(f"     Síntoma detectado:   {reporte.sintoma_id}")
            print(f"     Señal seguridad:     {reporte.senal_seguridad}")
            print(f"     Puntaje suficiencia: {reporte.suficiencia_puntaje:.1f}")
        if eval_m1:
            print(f"     Centroide Difuso M1: {eval_m1.suficiencia_centroide:.1f}")
            print(f"     Decisión M1:         {eval_m1.decision}")
        if extra.get('mensaje'):
            print(f"     Mensaje devuelto:    {extra.get('mensaje')[:100]}...")

        if tipo_ev == c['esperado']:
            print("  [OK] PASÓ")
            passed += 1
        else:
            print(f"  [FALLÓ] Esperado {c['esperado']} pero se obtuvo {tipo_ev}")

    print("\n" + "=" * 80)
    print(f"RESUMEN PI4 M1: {passed}/{total} pruebas superadas.")
    print("=" * 80)
    return passed == total

if __name__ == "__main__":
    success = run_pi4_m1_tests()
    sys.exit(0 if success else 1)
