"""
EXPERIMENTO 2: Agente con aprendizaje vs Agente sin aprendizaje

Hipótesis:
    Un agente que actualiza su estado con feedback debe superar
    consistentemente a un agente que recomienda al azar (sin aprendizaje).

Metodología:
    - Se simulan 2 agentes en paralelo durante 20 rondas
    - Agente A: aprende (actualiza Cp, Tp, Mp con feedback)
    - Agente B: no aprende (pesos y preferencias fijos, elige al azar)
    - Mismo usuario simulado para ambos
    - Comparar tasa de aceptación y precisión de coincidencia

Resultado esperado:
    - Agente A supera a Agente B en tasa de aceptación
    - La diferencia se amplía con el tiempo (el aprendizaje acumula ventaja)

Cómo ejecutar:
    python experiments/experiment_02.py
"""

import sys
import os
import json
import random
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.state    import AgentState
from agent.decision import decidir
from agent.feedback import procesar_feedback, ajustar_pesos
from metrics        import tasa_aceptacion, precision_coincidencia

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
CATALOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.csv')
PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_profile.json')
RESULTS_DIR  = os.path.join(os.path.dirname(__file__), 'results')
N_RONDAS     = 20
RANDOM_SEED  = 42

PREFERENCIAS_USUARIO = {
    'colores': ['azul', 'negro'],
    'telas':   ['algodón', 'poliéster'],
    'marcas':  ['Nike', 'Adidas']
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def reset_perfil():
    perfil = {
        "preferencias": {"colores": {}, "telas": {}, "marcas": {}},
        "pesos": {"w1_similitud": 0.5, "w2_preferencia": 0.3, "w3_novedad": 0.2},
        "historial": [],
        "ultima_recomendacion": None,
        "sesiones": 0,
        "likes_totales": 0,
        "dislikes_totales": 0
    }
    with open(PROFILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(perfil, f, ensure_ascii=False, indent=2)


def feedback_simulado(producto: dict) -> str:
    """Like si coincide con preferencias reales del usuario."""
    if producto['color'] in PREFERENCIAS_USUARIO['colores']:
        return 'like'
    if producto['tela'] in PREFERENCIAS_USUARIO['telas']:
        return 'like'
    if producto['marca'] in PREFERENCIAS_USUARIO['marcas']:
        return 'like'
    return 'dislike'


# ─── AGENTE A: Con aprendizaje ─────────────────────────────────────────────────

def simular_agente_con_aprendizaje(catalogo: pd.DataFrame) -> dict:
    """
    Agente A: actualiza estado con cada feedback.
    Implementa el ciclo completo del agente inteligente.
    """
    reset_perfil()
    state = AgentState()
    state.registrar_preferencias_iniciales(
        colores=PREFERENCIAS_USUARIO['colores'],
        telas=PREFERENCIAS_USUARIO['telas'],
        marcas=PREFERENCIAS_USUARIO['marcas']
    )

    tasas       = []
    precisiones = []
    likes = total = 0

    for ronda in range(1, N_RONDAS + 1):
        if len(state.productos_vistos()) >= len(catalogo):
            state.data['historial'] = []
            state.guardar()

        top1     = decidir(catalogo, state, top_n=1)
        decision = top1[0]
        fila     = catalogo[catalogo['id'] == decision['producto_id']].iloc[0]
        producto = fila.to_dict()

        fb = feedback_simulado(producto)
        if fb == 'like':
            likes += 1
        total += 1

        procesar_feedback(producto, fb, state)
        ajustar_pesos(state)

        tasas.append(tasa_aceptacion(likes, total) * 100)
        precisiones.append(precision_coincidencia(producto, state.Cp, state.Tp, state.Mp) * 100)

    return {'tasas': tasas, 'precisiones': precisiones, 'likes': likes, 'total': total}


# ─── AGENTE B: Sin aprendizaje (baseline) ─────────────────────────────────────

def simular_agente_sin_aprendizaje(catalogo: pd.DataFrame) -> dict:
    """
    Agente B: recomendación aleatoria sin aprendizaje.
    Representa la línea base (baseline) para comparación.
    """
    random.seed(RANDOM_SEED)
    vistos = set()

    # Preferencias fijas vacías (sin aprendizaje)
    Cp_fijo = {}
    Tp_fijo = {}
    Mp_fijo = {}

    tasas       = []
    precisiones = []
    likes = total = 0

    for ronda in range(1, N_RONDAS + 1):
        # Escoger producto aleatorio no visto
        disponibles = [i for i in catalogo['id'].tolist() if i not in vistos]
        if not disponibles:
            vistos = set()
            disponibles = catalogo['id'].tolist()

        prod_id  = random.choice(disponibles)
        vistos.add(prod_id)
        fila     = catalogo[catalogo['id'] == prod_id].iloc[0]
        producto = fila.to_dict()

        fb = feedback_simulado(producto)
        if fb == 'like':
            likes += 1
        total += 1

        tasas.append(tasa_aceptacion(likes, total) * 100)
        precisiones.append(precision_coincidencia(producto, Cp_fijo, Tp_fijo, Mp_fijo) * 100)

    return {'tasas': tasas, 'precisiones': precisiones, 'likes': likes, 'total': total}


# ─── GRÁFICAS ─────────────────────────────────────────────────────────────────

def generar_graficas(res_A: dict, res_B: dict):
    rondas = list(range(1, N_RONDAS + 1))

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        'Experimento 2: Agente con Aprendizaje vs Sin Aprendizaje\n'
        'Clothes Recommender — Agente Inteligente',
        fontsize=13, fontweight='bold'
    )

    # ── Panel izquierdo: Tasa de aceptación ──────────────────────
    ax1 = axes[0]
    ax1.plot(rondas, res_A['tasas'], color='#2ecc71', linewidth=2.5,
             marker='o', markersize=4, label='Agente A (con aprendizaje)')
    ax1.plot(rondas, res_B['tasas'], color='#e74c3c', linewidth=2.5,
             marker='x', markersize=5, linestyle='--', label='Agente B (sin aprendizaje)')
    ax1.fill_between(rondas, res_A['tasas'], res_B['tasas'],
                     where=[a > b for a, b in zip(res_A['tasas'], res_B['tasas'])],
                     alpha=0.15, color='#2ecc71', label='Ventaja Agente A')
    ax1.axhline(y=50, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    ax1.set_title('Tasa de Aceptación Acumulada (%)', fontweight='bold')
    ax1.set_xlabel('Ronda')
    ax1.set_ylabel('Tasa de aceptación (%)')
    ax1.set_ylim(0, 105)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Anotación de resultado final
    ax1.annotate(f"Final A: {res_A['tasas'][-1]:.1f}%",
                 xy=(N_RONDAS, res_A['tasas'][-1]),
                 xytext=(N_RONDAS - 5, res_A['tasas'][-1] + 6),
                 fontsize=8, color='#27ae60',
                 arrowprops=dict(arrowstyle='->', color='#27ae60', lw=1.2))
    ax1.annotate(f"Final B: {res_B['tasas'][-1]:.1f}%",
                 xy=(N_RONDAS, res_B['tasas'][-1]),
                 xytext=(N_RONDAS - 5, res_B['tasas'][-1] - 10),
                 fontsize=8, color='#c0392b',
                 arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.2))

    # ── Panel derecho: Comparación de likes totales ───────────────
    ax2 = axes[1]
    categorias = ['Agente A\n(con aprendizaje)', 'Agente B\n(sin aprendizaje)']
    likes_vals  = [res_A['likes'], res_B['likes']]
    colores_bar = ['#2ecc71', '#e74c3c']
    bars = ax2.bar(categorias, likes_vals, color=colores_bar,
                   width=0.45, edgecolor='white', linewidth=1.2)

    for bar, val in zip(bars, likes_vals):
        ax2.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.3,
                 f'{val} likes\n({val/N_RONDAS*100:.0f}%)',
                 ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax2.set_title(f'Likes Totales en {N_RONDAS} Rondas', fontweight='bold')
    ax2.set_ylabel('Número de likes')
    ax2.set_ylim(0, N_RONDAS + 3)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.axhline(y=N_RONDAS / 2, color='gray', linestyle='--',
                linewidth=1, alpha=0.5, label='50% base')
    ax2.legend(fontsize=8)

    plt.tight_layout()
    path_png = os.path.join(RESULTS_DIR, 'exp02_graficas.png')
    plt.savefig(path_png, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Gráficas guardadas: {path_png}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def ejecutar_experimento():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    catalogo = pd.read_csv(CATALOG_PATH)

    print("=" * 60)
    print("  EXPERIMENTO 2: Con aprendizaje vs Sin aprendizaje")
    print(f"  {N_RONDAS} rondas | Usuario: azul/negro, algodón/poliéster, Nike/Adidas")
    print("=" * 60)

    print("\n  Simulando Agente A (con aprendizaje)...")
    res_A = simular_agente_con_aprendizaje(catalogo)

    print("  Simulando Agente B (sin aprendizaje)...")
    res_B = simular_agente_sin_aprendizaje(catalogo)

    print(f"\n  {'─'*40}")
    print(f"  {'':>25} {'Agente A':>10} {'Agente B':>10}")
    print(f"  {'─'*40}")
    print(f"  {'Likes totales:':<25} {res_A['likes']:>10} {res_B['likes']:>10}")
    print(f"  {'Tasa final (%):':<25} {res_A['tasas'][-1]:>10.1f} {res_B['tasas'][-1]:>10.1f}")
    print(f"  {'Diferencia (pp):':<25} {res_A['tasas'][-1]-res_B['tasas'][-1]:>+10.1f}")
    print(f"  {'─'*40}")

    mejora = res_A['tasas'][-1] - res_B['tasas'][-1]
    if mejora > 0:
        print(f"\n   El agente con aprendizaje superó al baseline por {mejora:.1f} puntos porcentuales.")
    else:
        print(f"\n    Resultado inesperado. Revisar parámetros del experimento.")

    generar_graficas(res_A, res_B)

    # Guardar CSV comparativo
    df = pd.DataFrame({
        'ronda':       list(range(1, N_RONDAS + 1)),
        'tasa_A':      res_A['tasas'],
        'tasa_B':      res_B['tasas'],
        'diferencia':  [a - b for a, b in zip(res_A['tasas'], res_B['tasas'])]
    })
    csv_path = os.path.join(RESULTS_DIR, 'exp02_comparacion.csv')
    df.to_csv(csv_path, index=False)
    print(f"  CSV guardado: {csv_path}")

    return res_A, res_B


if __name__ == '__main__':
    ejecutar_experimento()