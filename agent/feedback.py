"""
Sistema de Retroalimentación del agente.

Cuando el usuario da feedback:
    LIKE    → el agente refuerza los atributos del producto
    DISLIKE → el agente penaliza los atributos del producto

Los pesos w1, w2, w3 de la función de decisión
se ajustan dinámicamente según el rendimiento acumulado del agente.

De esta forma se implementa prendizaje basado en retroalimentación (Feedback Learning)
"""

from agent.state import AgentState

# Cuánto cambia el puntaje de un atributo por cada feedback
DELTA_LIKE    = +1.0
DELTA_DISLIKE = -0.5

# Cuánto se ajustan los pesos w1, w2, w3 por sesión
DELTA_PESO = 0.02


def procesar_feedback(producto: dict, feedback: str, state: AgentState) -> dict:
    """
    Procesa el feedback del usuario y actualiza el estado del agente.

    Parámetros:
        producto → diccionario con los atributos del producto recomendado
        feedback → 'like' o 'dislike'
        state    → estado actual del agente (se modifica in-place)

    Retorna:
        dict con un resumen de los cambios realizados al estado
    """
    # Guardar valores anteriores para mostrar el cambio
    Cp_antes = dict(state.Cp)
    Tp_antes = dict(state.Tp)
    Mp_antes = dict(state.Mp)

    # Delegar al estado la actualización de Cp, Tp, Mp e historial H
    state.registrar_feedback(producto, feedback)

    # Calcular qué cambió
    cambios = {
        'feedback':  feedback,
        'producto':  producto['nombre'],
        'color':     producto.get('color'),
        'tela':      producto.get('tela'),
        'marca':     producto.get('marca'),
        'Cp_antes':  Cp_antes,
        'Cp_despues': dict(state.Cp),
        'Tp_antes':  Tp_antes,
        'Tp_despues': dict(state.Tp),
        'Mp_antes':  Mp_antes,
        'Mp_despues': dict(state.Mp),
    }

    return cambios


def ajustar_pesos(state: AgentState):
    """
    Ajusta dinámicamente los pesos w1, w2, w3 según el desempeño acumulado.

      - Si tasa de aceptación > 0.7 (agente va bien)           
        - subir w2 (más peso al historial de preferencias) 
        - bajar un poco w3 (menos exploración necesaria)   
                                                              
      - Si tasa de aceptación < 0.4 (agente va mal)          
        - subir w3 (más exploración / novedad)             
        - bajar un poco w2                                  

    Los pesos siempre deberán sumar 1.0
    """
    likes    = state.data['likes_totales']
    dislikes = state.data['dislikes_totales']
    total    = likes + dislikes

    if total == 0:
        return  # Sin interacciones aún, no ajustar

    tasa_aceptacion = likes / total

    pesos = state.pesos

    if tasa_aceptacion > 0.7:
        # El agente está acertando → explotar más el historial
        pesos['w2_preferencia'] = min(0.6, pesos['w2_preferencia'] + DELTA_PESO)
        pesos['w3_novedad']     = max(0.1, pesos['w3_novedad']     - DELTA_PESO)

    elif tasa_aceptacion < 0.4:
        # El agente está fallando → explorar más productos nuevos
        pesos['w3_novedad']     = min(0.5, pesos['w3_novedad']     + DELTA_PESO)
        pesos['w2_preferencia'] = max(0.1, pesos['w2_preferencia'] - DELTA_PESO)

    # Renormalizar para que w1 + w2 + w3 = 1.0
    total_pesos = pesos['w1_similitud'] + pesos['w2_preferencia'] + pesos['w3_novedad']
    pesos['w1_similitud']   = round(pesos['w1_similitud']   / total_pesos, 4)
    pesos['w2_preferencia'] = round(pesos['w2_preferencia'] / total_pesos, 4)
    pesos['w3_novedad']     = round(pesos['w3_novedad']     / total_pesos, 4)

    state.guardar()


def imprimir_cambios(cambios: dict):
    """Muestra de forma clara cómo el estado cambió tras el feedback."""
    emoji = " LIKE" if cambios['feedback'] == 'like' else " DISLIKE"
    print(f"\n  {emoji} → '{cambios['producto']}'")
    print(f"  Atributos: color={cambios['color']}, tela={cambios['tela']}, marca={cambios['marca']}")

    # Mostrar cambios en Cp
    color = cambios['color']
    if color:
        antes   = cambios['Cp_antes'].get(color, 0)
        despues = cambios['Cp_despues'].get(color, 0)
        if antes != despues:
            print(f"  Cp['{color}']: {antes:.1f} → {despues:.1f}")

    # Mostrar cambios en Tp
    tela = cambios['tela']
    if tela:
        antes   = cambios['Tp_antes'].get(tela, 0)
        despues = cambios['Tp_despues'].get(tela, 0)
        if antes != despues:
            print(f"  Tp['{tela}']: {antes:.1f} → {despues:.1f}")

    # Mostrar cambios en Mp
    marca = cambios['marca']
    if marca:
        antes   = cambios['Mp_antes'].get(marca, 0)
        despues = cambios['Mp_despues'].get(marca, 0)
        if antes != despues:
            print(f"  Mp['{marca}']: {antes:.1f} → {despues:.1f}")