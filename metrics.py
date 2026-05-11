"""
Calculo y registro de las métricas del agente.

Métricas implementadas:
    1. Tasa de aceptación        → likes / total de recomendaciones
    2. Precisión de coincidencia → qué tan bien coincide la recomendación con Cp, Tp, Mp
    3. Evolución de pesos        → cómo cambian w1, w2, w3 con el tiempo
    4. Evolución del estado      → cómo crecen los puntajes en Cp, Tp, Mp
"""

import json
import os

def tasa_aceptacion(likes: int, total: int) -> float:
    """
    Métrica 1: Tasa de aceptación.
    
    Mediante esta se mide qué fracción de las recomendaciones fueron aceptadas (like).
    Rango: [0.0, 1.0]
    
    Si sube con el tiempo significa que el agente está aprendiendo correctamente.
    """
    if total == 0:
        return 0.0
    return round(likes / total, 4)


def precision_coincidencia(producto: dict, state_Cp: dict, state_Tp: dict, state_Mp: dict) -> float:
    """
    Métrica 2: Precisión de coincidencia.
    
    Meidante esta se mide qué tan bien coincide el producto recomendado con las
    preferencias actuales del agente (Cp, Tp, Mp).
    
    Valor entre 0 y 1:
        1 → coincide en color, tela y marca
        0 → no coincide en ningún atributo
    """
    coincidencias = 0
    total_atributos = 0

    # Verificar color
    if state_Cp:
        total_atributos += 1
        if producto.get('color') in state_Cp and state_Cp[producto['color']] > 0:
            coincidencias += 1

    # Verificar tela
    if state_Tp:
        total_atributos += 1
        if producto.get('tela') in state_Tp and state_Tp[producto['tela']] > 0:
            coincidencias += 1

    # Verificar marca
    if state_Mp:
        total_atributos += 1
        if producto.get('marca') in state_Mp and state_Mp[producto['marca']] > 0:
            coincidencias += 1

    if total_atributos == 0:
        return 0.0
    return round(coincidencias / total_atributos, 4)


def calcular_score_promedio_aceptados(historial: list, scores_por_ronda: list) -> float:
    """
    Métrica 3: Score promedio de las recomendaciones aceptadas.
    
    Si el agente mejora, el score de los productos que le gustan al usuario
    debería ser más alto con el tiempo.
    """
    if not scores_por_ronda:
        return 0.0

    scores_likes = [
        entry['score']
        for entry in scores_por_ronda
        if entry['feedback'] == 'like'
    ]

    if not scores_likes:
        return 0.0
    return round(sum(scores_likes) / len(scores_likes), 4)


def registrar_snapshot(ronda: int, feedback: str, producto: dict,
                        score: float, state_Cp: dict, state_Tp: dict,
                        state_Mp: dict, pesos: dict) -> dict:
    """
    Creación de un snapshot del estado del agente en una ronda dada para graficar 
    la evolución a lo largo del tiempo.
    
    Retorna un diccionario con todos los valores relevantes de esa ronda.
    """
    return {
        'ronda':        ronda,
        'feedback':     feedback,
        'producto':     producto['nombre'],
        'color':        producto.get('color', ''),
        'tela':         producto.get('tela', ''),
        'marca':        producto.get('marca', ''),
        'score':        score,
        'precision':    precision_coincidencia(producto, state_Cp, state_Tp, state_Mp),
        'w1':           pesos['w1_similitud'],
        'w2':           pesos['w2_preferencia'],
        'w3':           pesos['w3_novedad'],
        'Cp_snapshot':  dict(state_Cp),
        'Tp_snapshot':  dict(state_Tp),
        'Mp_snapshot':  dict(state_Mp),
    }