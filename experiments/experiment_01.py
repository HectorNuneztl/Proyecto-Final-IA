"""
EXPERIMENTO 1: ¿El agente mejora con el tiempo?

A medida que el usuario da feedback, la tasa de aceptación
de las recomendaciones debe aumentar.

Para ello se usa: 
    - Usuario simulado con preferencia real: azul, algodón, Nike
    - 20 rondas de interacción
    - Feedback automático: LIKE si el producto tiene algún atributo preferido,
      DISLIKE en caso contrario
    - Registrar métricas ronda a ronda

Resultado esperado:
    - Tasa de aceptación sube con el tiempo
    - Cp['azul'] crece consistentemente
    - Pesos se adaptan al patrón de feedback
    - Gráficas muestran tendencia positiva
"""

import sys
import os
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.state    import AgentState
from agent.decision import decidir
from agent.feedback import procesar_feedback, ajustar_pesos
from metrics        import tasa_aceptacion, registrar_snapshot

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
CATALOG_PATH  = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.csv')
PROFILE_PATH  = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_profile.json')
RESULTS_DIR   = os.path.join(os.path.dirname(__file__), 'results')
N_RONDAS      = 20

# Preferencias reales del usuario simulado
PREFERENCIAS_USUARIO = {
    'colores': ['azul'],
    'telas':   ['algodón'],
    'marcas':  ['Nike']
}

# ─── FUNCIÓN DE FEEDBACK SIMULADO ─────────────────────────────────────────────

def feedback_simulado(producto: dict) -> str:
    """
    Simula el comportamiento del usuario.
    
    Like si el producto coincide con al menos una preferencia real.
    Dislike en caso contrario.
    """
    if producto['color'] in PREFERENCIAS_USUARIO['colores']:
        return 'like'
    if producto['tela'] in PREFERENCIAS_USUARIO['telas']:
        return 'like'
    if producto['marca'] in PREFERENCIAS_USUARIO['marcas']:
        return 'like'
    return 'dislike'

# ─── RESET DEL PERFIL ─────────────────────────────────────────────────────────

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

# ─── EXPERIMENTO ──────────────────────────────────────────────────────────────

def ejecutar_experimento():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    reset_perfil()

    catalogo = pd.read_csv(CATALOG_PATH)
    state    = AgentState()

    # Registrar preferencias iniciales del usuario
    state.registrar_preferencias_iniciales(
        colores=PREFERENCIAS_USUARIO['colores'],
        telas=PREFERENCIAS_USUARIO['telas'],
        marcas=PREFERENCIAS_USUARIO['marcas']
    )

    snapshots        = []
    likes_acum       = 0
    total_acum       = 0
    tasas_acum       = []
    scores_ronda     = []
    pesos_historia   = {'w1': [], 'w2': [], 'w3': []}
    cp_azul_historia = []

    print("=" * 60)
    print("  EXPERIMENTO 1: Evolución del aprendizaje del agente")
    print(f"  {N_RONDAS} rondas | Usuario prefiere: azul, algodón, Nike")
    print("=" * 60)
    print(f"\n  {'Ronda':<7} {'Producto':<30} {'Score':<8} {'FB':<8} {'Tasa%':<8} Cp[azul]")
    print(f"  {'─'*5:<7} {'─'*28:<30} {'─'*6:<8} {'─'*6:<8} {'─'*6:<8} {'─'*8}")

    for ronda in range(1, N_RONDAS + 1):

        # Si todos los productos ya fueron vistos, limpiar novedad
        if len(state.productos_vistos()) >= len(catalogo):
            state.data['historial'] = []
            state.guardar()

        # ── Decisión ──────────────────────────────────────────────
        top1     = decidir(catalogo, state, top_n=1)
        decision = top1[0]
        fila     = catalogo[catalogo['id'] == decision['producto_id']].iloc[0]
        producto = fila.to_dict()

        # ── Feedback simulado ─────────────────────────────────────
        fb = feedback_simulado(producto)
        if fb == 'like':
            likes_acum += 1
        total_acum += 1

        # ── Actualizar estado ─────────────────────────────────────
        procesar_feedback(producto, fb, state)
        ajustar_pesos(state)

        # ── Registrar métricas ────────────────────────────────────
        tasa      = tasa_aceptacion(likes_acum, total_acum)
        cp_azul   = state.Cp.get('azul', 0)
        snap      = registrar_snapshot(
                        ronda, fb, producto, decision['score_total'],
                        state.Cp, state.Tp, state.Mp, state.pesos)

        snapshots.append(snap)
        tasas_acum.append(tasa * 100)
        scores_ronda.append({'ronda': ronda, 'score': decision['score_total'], 'feedback': fb})
        pesos_historia['w1'].append(state.pesos['w1_similitud'])
        pesos_historia['w2'].append(state.pesos['w2_preferencia'])
        pesos_historia['w3'].append(state.pesos['w3_novedad'])
        cp_azul_historia.append(cp_azul)

        print(f"  {ronda:<7} {producto['nombre'][:28]:<30} {decision['score_total']:<8.4f} "
              f"{'LIKE' if fb=='like' else 'DISLIKE':<8} {tasa*100:<8.1f} {cp_azul:.1f}")

    print(f"\n  Tasa de aceptación final: {tasas_acum[-1]:.1f}%")
    print(f"  Cp[azul] final:           {cp_azul_historia[-1]:.1f}")

    # ── Guardar CSV de resultados ─────────────────────────────────
    df_resultados = pd.DataFrame(snapshots)
    csv_path = os.path.join(RESULTS_DIR, 'exp01_resultados.csv')
    df_resultados.to_csv(csv_path, index=False)
    print(f"\n  CSV guardado: {csv_path}")

    # ── Generar gráficas ──────────────────────────────────────────
    generar_graficas(snapshots, tasas_acum, pesos_historia, cp_azul_historia, scores_ronda)

    return snapshots, tasas_acum


# ─── GRÁFICAS ─────────────────────────────────────────────────────────────────

def generar_graficas(snapshots, tasas_acum, pesos_historia, cp_azul_historia, scores_ronda):
    rondas = list(range(1, len(snapshots) + 1))

    fig = plt.figure(figsize=(16, 10))
    fig.suptitle(
        'Experimento 1: Evolución del Aprendizaje del Agente\n'
        'Clothes Recommender — Agente Inteligente',
        fontsize=14, fontweight='bold', y=0.98
    )

    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.35)

    # ── Gráfica 1: Tasa de aceptación acumulada ───────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(rondas, tasas_acum, color='#2ecc71', linewidth=2.5, marker='o', markersize=4)
    ax1.axhline(y=50, color='gray', linestyle='--', linewidth=1, alpha=0.6, label='50% base')
    ax1.fill_between(rondas, tasas_acum, alpha=0.15, color='#2ecc71')
    ax1.set_title('Tasa de Aceptación Acumulada', fontweight='bold')
    ax1.set_xlabel('Ronda')
    ax1.set_ylabel('Tasa (%)')
    ax1.set_ylim(0, 105)
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    # ── Gráfica 2: Evolución de Cp[azul] ─────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(rondas, cp_azul_historia, color='#3498db', linewidth=2.5, marker='s', markersize=4)
    ax2.fill_between(rondas, cp_azul_historia, alpha=0.15, color='#3498db')
    ax2.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax2.set_title("Evolución de Cp['azul']", fontweight='bold')
    ax2.set_xlabel('Ronda')
    ax2.set_ylabel('Puntaje acumulado')
    ax2.grid(True, alpha=0.3)

    # ── Gráfica 3: Evolución de pesos w1, w2, w3 ─────────────────
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(rondas, pesos_historia['w1'], label='w1 (similitud)',   color='#e74c3c', linewidth=2)
    ax3.plot(rondas, pesos_historia['w2'], label='w2 (preferencia)', color='#9b59b6', linewidth=2)
    ax3.plot(rondas, pesos_historia['w3'], label='w3 (novedad)',     color='#f39c12', linewidth=2)
    ax3.set_title('Evolución de Pesos w1, w2, w3', fontweight='bold')
    ax3.set_xlabel('Ronda')
    ax3.set_ylabel('Valor del peso')
    ax3.set_ylim(0, 0.75)
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    # ── Gráfica 4: Score por ronda (like vs dislike) ──────────────
    ax4 = fig.add_subplot(gs[1, 0])
    likes_r    = [s for s in scores_ronda if s['feedback'] == 'like']
    dislikes_r = [s for s in scores_ronda if s['feedback'] == 'dislike']
    if likes_r:
        ax4.scatter([s['ronda'] for s in likes_r],
                    [s['score'] for s in likes_r],
                    color='#2ecc71', label='Like', s=60, zorder=3)
    if dislikes_r:
        ax4.scatter([s['ronda'] for s in dislikes_r],
                    [s['score'] for s in dislikes_r],
                    color='#e74c3c', label='Dislike', s=60, marker='x', zorder=3)
    ax4.plot(rondas, [s['score'] for s in scores_ronda],
             color='gray', linewidth=1, alpha=0.4, linestyle='--')
    ax4.set_title('Score f(s,a) por Ronda', fontweight='bold')
    ax4.set_xlabel('Ronda')
    ax4.set_ylabel('Score f(s,a)')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)

    # ── Gráfica 5: Distribución final de Cp ──────────────────────
    ax5 = fig.add_subplot(gs[1, 1])
    ultimo = snapshots[-1]
    cp_final = ultimo['Cp_snapshot']
    if cp_final:
        colores_nombres = list(cp_final.keys())
        valores         = list(cp_final.values())
        colores_barras  = ['#2ecc71' if v > 0 else '#e74c3c' for v in valores]
        bars = ax5.bar(colores_nombres, valores, color=colores_barras, edgecolor='white', linewidth=0.8)
        ax5.axhline(y=0, color='black', linewidth=0.8)
        for bar, val in zip(bars, valores):
            ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                     f'{val:.1f}', ha='center', va='bottom', fontsize=8)
    ax5.set_title('Estado Final Cp (Preferencias Color)', fontweight='bold')
    ax5.set_xlabel('Color')
    ax5.set_ylabel('Puntaje acumulado')
    ax5.grid(True, alpha=0.3, axis='y')
    plt.setp(ax5.xaxis.get_majorticklabels(), rotation=30, ha='right', fontsize=8)

    # ── Gráfica 6: Likes vs Dislikes acumulados ───────────────────
    ax6 = fig.add_subplot(gs[1, 2])
    likes_acum_hist    = []
    dislikes_acum_hist = []
    l_count = d_count = 0
    for s in snapshots:
        if s['feedback'] == 'like':
            l_count += 1
        else:
            d_count += 1
        likes_acum_hist.append(l_count)
        dislikes_acum_hist.append(d_count)
    ax6.stackplot(rondas, likes_acum_hist, dislikes_acum_hist,
                  labels=['Likes', 'Dislikes'],
                  colors=['#2ecc71', '#e74c3c'], alpha=0.75)
    ax6.set_title('Likes vs Dislikes Acumulados', fontweight='bold')
    ax6.set_xlabel('Ronda')
    ax6.set_ylabel('Cantidad acumulada')
    ax6.legend(fontsize=8, loc='upper left')
    ax6.grid(True, alpha=0.3)

    # ── Guardar ───────────────────────────────────────────────────
    path_png = os.path.join(RESULTS_DIR, 'exp01_graficas.png')
    plt.savefig(path_png, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Gráficas guardadas: {path_png}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    ejecutar_experimento()