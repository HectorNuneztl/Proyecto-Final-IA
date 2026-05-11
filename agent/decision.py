"""
Implementa la Función de Desicón del agente inteligente.

Fórmula:
    a* = argmax f(s, a)

Donde:
    f(s, a) = w1 * similitud(s, a) + w2 * preferencia(s, a) + w3 * novedad(s, a)

Componentes:
    similitud(s, a)   → qué tan parecido es el producto a las preferencias actuales
    preferencia(s, a) → qué tan bien coincide con el historial positivo del usuario
    novedad(s, a)     → si el producto NO ha sido visto antes (evita repeticiones)

El agente evalúa todos los productos del catálogo y selecciona
el que maximiza f(s, a). Esto es la toma de decisión real del agente.
"""

import pandas as pd
import numpy as np
from agent.state import AgentState


def calcular_similitud(producto: dict, state: AgentState) -> float:
    """
    Componente 1: similitud(s, a)
    
    Mide qué tan parecido es el producto a las preferencias declaradas
    por el usuario (Cp, Tp, Mp).
    
    Lógica:
        - Si el color del producto está en Cp → suma su puntaje normalizado
        - Si la tela del producto está en Tp  → suma su puntaje normalizado
        - Si la marca del producto está en Mp → suma su puntaje normalizado
    
    El resultado está en el rango [0, 1].
    """
    score = 0.0
    coincidencias = 0

    # Evaluar coincidencia de color
    Cp = state.Cp
    if Cp:
        max_cp = max(Cp.values()) if max(Cp.values()) > 0 else 1
        color_producto = producto.get('color', '')
        if color_producto in Cp:
            score += Cp[color_producto] / max_cp
        coincidencias += 1

    # Evaluar coincidencia de tela
    Tp = state.Tp
    if Tp:
        max_tp = max(Tp.values()) if max(Tp.values()) > 0 else 1
        tela_producto = producto.get('tela', '')
        if tela_producto in Tp:
            score += Tp[tela_producto] / max_tp
        coincidencias += 1

    # Evaluar coincidencia de marca
    Mp = state.Mp
    if Mp:
        max_mp = max(Mp.values()) if max(Mp.values()) > 0 else 1
        marca_producto = producto.get('marca', '')
        if marca_producto in Mp:
            score += Mp[marca_producto] / max_mp
        coincidencias += 1

    # Normalizar entre 0 y 1
    if coincidencias == 0:
        return 0.0
    return score / coincidencias


def calcular_preferencia(producto: dict, state: AgentState) -> float:
    """
    Componente 2: preferencia(s, a)
    
    Evalúa el historial H del usuario para medir si productos con
    atributos similares recibieron feedback positivo antes.
    
    Lógica:
        - Buscar en H todos los items con mismo color/tela/marca
        - Contar likes (+1) y dislikes (-1)
        - Normalizar entre -1 y 1
    
    Si el valor es positivo → el usuario tiende a gustar productos así.
    Si es negativo → el usuario los rechaza.
    """
    historial = state.H
    if not historial:
        return 0.5  # Sin historial: puntaje neutral

    color  = producto.get('color', '')
    tela   = producto.get('tela', '')
    marca  = producto.get('marca', '')

    puntaje_acumulado = 0.0
    total_interacciones = 0

    for item in historial:
        coincide = (
            item.get('color') == color or
            item.get('tela')  == tela  or
            item.get('marca') == marca
        )
        if coincide:
            total_interacciones += 1
            puntaje_acumulado += 1.0 if item['feedback'] == 'like' else -1.0

    if total_interacciones == 0:
        return 0.5  # Sin interacciones similares: neutral

    # Normalizar de [-1, 1] a [0, 1]
    normalizado = (puntaje_acumulado / total_interacciones + 1) / 2
    return normalizado


def calcular_novedad(producto: dict, state: AgentState) -> float:
    """
    Componente 3: novedad(s, a)
    
    Penaliza los productos que ya fueron mostrados al usuario.
    El agente prefiere recomendar productos nuevos para explorar el catálogo.
    
    Retorna:
        1.0 → producto nuevo (no visto antes)
        0.0 → producto ya recomendado
    """
    productos_vistos = state.productos_vistos()
    producto_id = producto.get('id')
    return 0.0 if producto_id in productos_vistos else 1.0


def calcular_score(producto: dict, state: AgentState) -> dict:
    """
    Función completa f(s, a):
    
        f(s, a) = w1 * similitud + w2 * preferencia + w3 * novedad
    
    Retorna un diccionario con el score total y los componentes individuales
    para poder inspeccionar cómo el agente tomó la decisión.
    """
    w1 = state.pesos['w1_similitud']
    w2 = state.pesos['w2_preferencia']
    w3 = state.pesos['w3_novedad']

    similitud   = calcular_similitud(producto, state)
    preferencia = calcular_preferencia(producto, state)
    novedad     = calcular_novedad(producto, state)

    score_total = (w1 * similitud) + (w2 * preferencia) + (w3 * novedad)

    return {
        'producto_id':  producto['id'],
        'nombre':       producto['nombre'],
        'score_total':  round(score_total, 4),
        'similitud':    round(similitud, 4),
        'preferencia':  round(preferencia, 4),
        'novedad':      round(novedad, 4),
        'w1':           w1,
        'w2':           w2,
        'w3':           w3,
    }


def decidir(catalogo: pd.DataFrame, state: AgentState, top_n: int = 1) -> list:
    """
    Implementa: a* = argmax f(s, a)
    
    Evalúa TODOS los productos del catálogo y devuelve los top_n
    productos con mayor score.
    
    Parámetros:
        catalogo → DataFrame con todos los productos disponibles
        state    → Estado actual del agente S = (Cp, Tp, Mp, H, R)
        top_n    → cuántas recomendaciones devolver (default: 1)
    
    Retorna:
        Lista de dicts con el producto recomendado y el desglose del score.
    """
    scores = []

    for _, producto in catalogo.iterrows():
        resultado = calcular_score(producto.to_dict(), state)
        scores.append(resultado)

    # Ordenar de mayor a menor score → argmax
    scores_ordenados = sorted(scores, key=lambda x: x['score_total'], reverse=True)

    return scores_ordenados[:top_n]


def imprimir_decision(decision: dict):
    """
    Muestra de forma clara cómo el agente tomó la decisión.
    Esto cumple el requisito: 'mostrar claramente cómo decide el agente'.
    """
    print("\n" + "─" * 45)
    print("  DECISIÓN DEL AGENTE")
    print("─" * 45)
    print(f"  Producto:    {decision['nombre']}")
    print(f"  Score total: {decision['score_total']:.4f}")
    print()
    print("  Desglose f(s,a):")
    print(f"    w1={decision['w1']:.2f} × similitud={decision['similitud']:.4f}   → {decision['w1']*decision['similitud']:.4f}")
    print(f"    w2={decision['w2']:.2f} × preferencia={decision['preferencia']:.4f} → {decision['w2']*decision['preferencia']:.4f}")
    print(f"    w3={decision['w3']:.2f} × novedad={decision['novedad']:.4f}      → {decision['w3']*decision['novedad']:.4f}")
    print(f"    {'─'*35}")
    print(f"    TOTAL f(s,a) = {decision['score_total']:.4f}")
    print("─" * 45)