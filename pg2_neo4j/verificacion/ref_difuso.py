"""
ref_difuso.py - Motor de Referencia de Lógica Difusa Mamdani en Python
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026

Implementación matemática independiente de control para verificar los 10 centroides
publicados en PI3 y reproducidos en Neo4j Cypher puro.
"""

import math
import sys
from typing import Dict, List, Tuple, Any

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ------------------------------------------------------------------------------
# Parámetros de Conjuntos Difusos Gaussianos
# c: centro, s: sigma, h: hombro ('izq', 'der', 'ninguno')
# ------------------------------------------------------------------------------

ETIQUETAS = {
    # M1: Interpretación
    'ConfianzaExtraccion': {
        'Baja': {'c': 0.0, 's': 0.18, 'h': 'izq'},
        'Media': {'c': 0.55, 's': 0.16, 'h': 'ninguno'},
        'Alta': {'c': 1.0, 's': 0.15, 'h': 'der'}
    },
    'CoincidenciaLexica': {
        'Debil': {'c': 0.0, 's': 0.20, 'h': 'izq'},
        'Parcial': {'c': 0.55, 's': 0.16, 'h': 'ninguno'},
        'Fuerte': {'c': 1.0, 's': 0.15, 'h': 'der'}
    },
    'DistanciaCandidatos': {
        'Pequena': {'c': 0.0, 's': 0.15, 'h': 'izq'},
        'Moderada': {'c': 0.40, 's': 0.15, 'h': 'ninguno'},
        'Grande': {'c': 1.0, 's': 0.22, 'h': 'der'}
    },
    'SuficienciaInterpretacion': {
        'Insuficiente': {'c': 10.0, 's': 15.0, 'h': 'izq'},
        'Parcial': {'c': 50.0, 's': 14.0, 'h': 'ninguno'},
        'Suficiente': {'c': 90.0, 's': 14.0, 'h': 'der'}
    },

    # M2: Diagnóstico
    'FrecuenciaCausa': {
        'Rara': {'c': 0.0, 's': 0.18, 'h': 'izq'},
        'PocoFrecuente': {'c': 0.45, 's': 0.16, 'h': 'ninguno'},
        'Frecuente': {'c': 1.0, 's': 0.20, 'h': 'der'}
    },
    'RiesgoEsfuerzoPaso': {
        'Bajo': {'c': 0.0, 's': 1.8, 'h': 'izq'},
        'Medio': {'c': 5.0, 's': 1.6, 'h': 'ninguno'},
        'Alto': {'c': 10.0, 's': 1.8, 'h': 'der'}
    },
    'EvidenciaAcumulada': {
        'Debil': {'c': 0.0, 's': 0.18, 'h': 'izq'},
        'Moderada': {'c': 0.50, 's': 0.16, 'h': 'ninguno'},
        'Fuerte': {'c': 1.0, 's': 0.18, 'h': 'der'}
    },
    'PrioridadHipotesisPaso': {
        'Baja': {'c': 10.0, 's': 15.0, 'h': 'izq'},
        'Media': {'c': 50.0, 's': 14.0, 'h': 'ninguno'},
        'Alta': {'c': 90.0, 's': 14.0, 'h': 'der'}
    },

    # M3: Severidad
    'ImpactoClimatico': {
        'Bajo': {'c': 16.0, 's': 3.5, 'h': 'izq'},
        'Medio': {'c': 24.0, 's': 3.2, 'h': 'ninguno'},
        'Alto': {'c': 33.0, 's': 3.6, 'h': 'ninguno'},
        'Extremo': {'c': 41.0, 's': 3.8, 'h': 'der'}
    },
    'TiempoRestante': {
        'Inminente': {'c': 0.0, 's': 5.0, 'h': 'izq'},
        'Intermedio': {'c': 24.0, 's': 11.0, 'h': 'ninguno'},
        'Prolongado': {'c': 56.0, 's': 13.0, 'h': 'der'}
    },
    'SensibilidadServicio': {
        'Tolerable': {'c': 0.0, 's': 1.8, 'h': 'izq'},
        'Molesto': {'c': 5.0, 's': 1.6, 'h': 'ninguno'},
        'Critico': {'c': 10.0, 's': 1.8, 'h': 'der'}
    },
    'CriticidadDifusa': {
        'Baja': {'c': 12.0, 's': 11.0, 'h': 'izq'},
        'Media': {'c': 42.0, 's': 11.0, 'h': 'ninguno'},
        'Alta': {'c': 70.0, 's': 10.0, 'h': 'ninguno'},
        'Emergencia': {'c': 93.0, 's': 7.5, 'h': 'der'}
    }
}

# ------------------------------------------------------------------------------
# Función de pertenencia gaussiana con saturación de hombro
# ------------------------------------------------------------------------------

def mu_gauss(x: float, c: float, sigma: float, hombro: str = 'ninguno') -> float:
    if hombro == 'izq' and x <= c:
        return 1.0
    if hombro == 'der' and x >= c:
        return 1.0
    return math.exp(-((x - c) ** 2) / (2.0 * (sigma ** 2)))

def fuzzify(var_name: str, x: float) -> Dict[str, float]:
    res = {}
    for et_name, params in ETIQUETAS[var_name].items():
        res[et_name] = mu_gauss(x, params['c'], params['s'], params['h'])
    return res

# ------------------------------------------------------------------------------
# Reglas Difusas por Módulo
# Estructura: (regla_id, consecuente, activa, [grupos_de_antecedentes])
# Cada grupo es una lista de (variable, etiqueta, negada) combinados por OR (MAX).
# Los grupos se combinan por AND (MIN).
# ------------------------------------------------------------------------------

REGLAS_M1 = [
    ('IF1', 'Suficiente', True, [[('ConfianzaExtraccion', 'Alta', False)], [('CoincidenciaLexica', 'Fuerte', False)], [('DistanciaCandidatos', 'Grande', False)]]),
    ('IF2', 'Suficiente', True, [[('ConfianzaExtraccion', 'Alta', False)], [('CoincidenciaLexica', 'Parcial', False)], [('DistanciaCandidatos', 'Grande', False)]]),
    ('IF3', 'Parcial', True, [[('ConfianzaExtraccion', 'Media', False), ('CoincidenciaLexica', 'Parcial', False)], [('DistanciaCandidatos', 'Moderada', False)]]),
    ('IF4', 'Parcial', True, [[('DistanciaCandidatos', 'Pequena', False)], [('ConfianzaExtraccion', 'Baja', True)]]),
    ('IF5', 'Insuficiente', True, [[('ConfianzaExtraccion', 'Baja', False), ('CoincidenciaLexica', 'Debil', False)]]),
    ('IF6', 'Parcial', True, [[('ConfianzaExtraccion', 'Alta', False)], [('CoincidenciaLexica', 'Fuerte', False)], [('DistanciaCandidatos', 'Moderada', False)]]),
    ('IF7', 'Parcial', False, [[('ConfianzaExtraccion', 'Media', False)], [('DistanciaCandidatos', 'Grande', False)]])
]

REGLAS_M2 = [
    ('RF1', 'Alta', True, [[('FrecuenciaCausa', 'Frecuente', False), ('EvidenciaAcumulada', 'Fuerte', False)], [('RiesgoEsfuerzoPaso', 'Bajo', False)]]),
    ('RF2', 'Alta', True, [[('FrecuenciaCausa', 'Frecuente', False)], [('EvidenciaAcumulada', 'Fuerte', False)], [('RiesgoEsfuerzoPaso', 'Medio', False)]]),
    ('RF3', 'Media', True, [[('FrecuenciaCausa', 'PocoFrecuente', False)], [('EvidenciaAcumulada', 'Moderada', False)], [('RiesgoEsfuerzoPaso', 'Alto', True)]]),
    ('RF4', 'Media', True, [[('FrecuenciaCausa', 'Frecuente', False)], [('EvidenciaAcumulada', 'Moderada', False)], [('RiesgoEsfuerzoPaso', 'Medio', False)]]),
    ('RF5', 'Baja', True, [[('RiesgoEsfuerzoPaso', 'Alto', False), ('EvidenciaAcumulada', 'Debil', False)]]),
    ('RF6', 'Baja', True, [[('FrecuenciaCausa', 'Rara', False)], [('EvidenciaAcumulada', 'Fuerte', True)]]),
    ('RF7', 'Media', False, [[('EvidenciaAcumulada', 'Fuerte', False)], [('RiesgoEsfuerzoPaso', 'Medio', False)]])
]

REGLAS_M3 = [
    ('F1', 'Emergencia', True, [[('SensibilidadServicio', 'Critico', False)], [('ImpactoClimatico', 'Extremo', False)]]),
    ('F2', 'Alta', True, [[('SensibilidadServicio', 'Critico', False)], [('ImpactoClimatico', 'Alto', False)]]),
    ('F3', 'Alta', True, [[('SensibilidadServicio', 'Molesto', False)], [('ImpactoClimatico', 'Alto', False)], [('TiempoRestante', 'Inminente', True)]]),
    ('F4a', 'Baja', True, [[('SensibilidadServicio', 'Tolerable', False)]]),
    ('F4b', 'Baja', True, [[('ImpactoClimatico', 'Bajo', False)], [('SensibilidadServicio', 'Critico', True)]]),
    ('F5', 'Media', True, [[('TiempoRestante', 'Inminente', False)], [('SensibilidadServicio', 'Critico', True)]]),
    ('F6', 'Alta', True, [[('TiempoRestante', 'Prolongado', False)], [('SensibilidadServicio', 'Critico', False)]]),
    ('F7', 'Alta', False, [[('SensibilidadServicio', 'Critico', False)]])
]

# ------------------------------------------------------------------------------
# Motor de Inferencia Mamdani
# ------------------------------------------------------------------------------

def inferencia_mamdani(modulo: str, inputs: Dict[str, float], incluir_cobertura: bool = False) -> Tuple[float, float, str, List[Dict[str, Any]]]:
    """
    Ejecuta el ciclo completo de inferencia difusa:
    Fuzzificación -> Evaluación de reglas -> Agregación -> Defuzzificación Centroide.
    Retorna: (centroide, alfa_max, estado, lista_reglas_activadas)
    """
    if modulo == 'M1':
        reglas = REGLAS_M1
        var_salida = 'SuficienciaInterpretacion'
    elif modulo == 'M2':
        reglas = REGLAS_M2
        var_salida = 'PrioridadHipotesisPaso'
    elif modulo == 'M3':
        reglas = REGLAS_M3
        var_salida = 'CriticidadDifusa'
    else:
        raise ValueError(f"Módulo desconocido: {modulo}")

    # 1. Fuzzificar entradas
    mu_dict = {}
    for var, val in inputs.items():
        mu_dict[var] = fuzzify(var, val)

    # 2. Evaluar reglas
    alfa_por_consecuente = {et: 0.0 for et in ETIQUETAS[var_salida]}
    reglas_activadas = []

    for r_id, cons, activa, grupos in reglas:
        if not activa and not incluir_cobertura:
            continue

        valores_grupos = []
        for grp in grupos:
            val_or = 0.0
            for var, et, negada in grp:
                val = mu_dict[var][et]
                if negada:
                    val = 1.0 - val
                if val > val_or:
                    val_or = val
            valores_grupos.append(val_or)

        alfa = min(valores_grupos) if valores_grupos else 0.0

        if alfa > 0.0:
            reglas_activadas.append({
                'regla': r_id,
                'alfa': round(alfa, 3),
                'consecuente': cons,
                'activa': activa
            })
            if alfa > alfa_por_consecuente[cons]:
                alfa_por_consecuente[cons] = alfa

    alfa_max = max(alfa_por_consecuente.values()) if alfa_por_consecuente else 0.0

    # 3. Defuzzificación: Centroide sobre 4001 puntos (y = i / 40.0)
    num = 0.0
    den = 0.0
    params_salida = ETIQUETAS[var_salida]

    for i in range(4001):
        y = i / 40.0
        # Agregación por MAX de consecuentes recortados
        agg = 0.0
        for et, alfa in alfa_por_consecuente.items():
            if alfa > 0.0:
                p = params_salida[et]
                m = mu_gauss(y, p['c'], p['s'], p['h'])
                recortado = min(m, alfa)
                if recortado > agg:
                    agg = recortado
        num += y * agg
        den += agg

    centroide = round(num / den, 1) if den > 0 else 0.0
    estado = 'interpretable' if alfa_max >= 0.2 else 'sin_cobertura (usar respaldo nitido)'

    return centroide, round(alfa_max, 3), estado, reglas_activadas

# ------------------------------------------------------------------------------
# Verificación de los 10 Casos Difusos Oficiales
# ------------------------------------------------------------------------------

CASOS_OFICIALES = [
    {'caso': 'M1-A', 'caso_id': 'M1-A', 'modulo': 'M1', 'esperado': 50.1, 'esperado_pi3': 50.1, 'inputs': {'ConfianzaExtraccion': 0.72, 'CoincidenciaLexica': 0.68, 'DistanciaCandidatos': 0.35}},
    {'caso': 'M1-B', 'caso_id': 'M1-B', 'modulo': 'M1', 'esperado': 82.7, 'esperado_pi3': 82.7, 'inputs': {'ConfianzaExtraccion': 0.90, 'CoincidenciaLexica': 0.92, 'DistanciaCandidatos': 0.85}},
    {'caso': 'M1-hueco', 'caso_id': 'M1-hueco', 'modulo': 'M1', 'esperado': 29.7, 'esperado_pi3': 29.7, 'inputs': {'ConfianzaExtraccion': 0.50, 'CoincidenciaLexica': 0.50, 'DistanciaCandidatos': 0.90}},
    {'caso': 'M2-hip1-e1', 'caso_id': 'M2-hip1-e1', 'modulo': 'M2', 'esperado': 51.1, 'esperado_pi3': 51.1, 'inputs': {'FrecuenciaCausa': 0.82, 'RiesgoEsfuerzoPaso': 4.2, 'EvidenciaAcumulada': 0.55}},
    {'caso': 'M2-hip1-e2', 'caso_id': 'M2-hip1-e2', 'modulo': 'M2', 'esperado': 75.9, 'esperado_pi3': 75.9, 'inputs': {'FrecuenciaCausa': 0.82, 'RiesgoEsfuerzoPaso': 4.2, 'EvidenciaAcumulada': 0.85}},
    {'caso': 'M2-hip2-e1', 'caso_id': 'M2-hip2-e1', 'modulo': 'M2', 'esperado': 68.4, 'esperado_pi3': 68.4, 'inputs': {'FrecuenciaCausa': 0.75, 'RiesgoEsfuerzoPaso': 1.2, 'EvidenciaAcumulada': 0.55}},
    {'caso': 'M2-hueco', 'caso_id': 'M2-hueco', 'modulo': 'M2', 'esperado': 50.0, 'esperado_pi3': 50.0, 'inputs': {'FrecuenciaCausa': 0.10, 'RiesgoEsfuerzoPaso': 5.0, 'EvidenciaAcumulada': 1.00}},
    {'caso': 'M3-caso1', 'caso_id': 'M3-caso1', 'modulo': 'M3', 'esperado': 76.5, 'esperado_pi3': 76.5, 'inputs': {'ImpactoClimatico': 38.0, 'TiempoRestante': 48.0, 'SensibilidadServicio': 8.3}},
    {'caso': 'M3-hueco', 'caso_id': 'M3-hueco', 'modulo': 'M3', 'esperado': 66.7, 'esperado_pi3': 66.7, 'inputs': {'ImpactoClimatico': 12.0, 'TiempoRestante': 12.0, 'SensibilidadServicio': 10.0}},
    {'caso': 'M3-limite', 'caso_id': 'M3-limite', 'modulo': 'M3', 'esperado': 48.7, 'esperado_pi3': 48.7, 'inputs': {'ImpactoClimatico': 31.0, 'TiempoRestante': 3.5, 'SensibilidadServicio': 5.5}}
]

CASOS_CALIBRACION = CASOS_OFICIALES

def run_verification():
    print("=" * 80)
    print("VERIFICACIÓN DE LOS 10 CENTROIDES MAMDANI (PI3 / PG2)")
    print("=" * 80)
    print(f"{'Caso':<12} | {'Mód':<4} | {'Esperado':<8} | {'Obtenido':<8} | {'α máx':<6} | {'Estado':<25} | {'OK?'}")
    print("-" * 80)
    all_ok = True
    for c in CASOS_OFICIALES:
        centroide, alfa_max, estado, _ = inferencia_mamdani(c['modulo'], c['inputs'], incluir_cobertura=False)
        match = abs(centroide - c['esperado']) < 0.15
        if not match:
            all_ok = False
        status = "OK" if match else "DIFF"
        print(f"{c['caso']:<12} | {c['modulo']:<4} | {c['esperado']:<8.1f} | {centroide:<8.1f} | {alfa_max:<6.3f} | {estado:<25} | {status}")
    print("=" * 80)
    if all_ok:
        print(">>> TODOS LOS 10 CENTROIDES COINCIDEN CON LA PUBLICACIÓN OFICIAL DE PG2/PI3 <<<")
    else:
        print(">>> SE DETECTARON DISCREPANCIAS <<<")
    return all_ok

if __name__ == '__main__':
    run_verification()
