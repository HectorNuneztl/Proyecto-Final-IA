# Clothes Recommender — Agente Inteligente

Sistema de recomendación de ropa basado en un agente inteligente que aprende
de las preferencias del usuario mediante retroalimentación iterativa.

---

## ¿Qué hace el agente?

El agente recibe un **estado** `S = (Cp, Tp, Mp, H, R)`, evalúa todos los
productos del catálogo con la función `f(s,a) = w1·similitud + w2·preferencia + w3·novedad`,
selecciona el producto óptimo (`a* = argmax f(s,a)`) y actualiza su estado
según el feedback del usuario. Con cada interacción, las recomendaciones
se vuelven más precisas.

---

## Estructura del proyecto

```
clothes-recommender/
├── data/
│   ├── products.csv          # Catálogo: 30 productos (color, tela, marca)
│   └── user_profile.json     # Estado del agente S = (Cp, Tp, Mp, H, R)
├── agent/
│   ├── state.py              # Clase AgentState — gestión del estado
│   ├── decision.py           # Función f(s,a) y argmax
│   ├── feedback.py           # Aprendizaje por retroalimentación
│   └── recommender.py        # Agente principal — ciclo completo
├── experiments/
│   ├── experiment_01.py      # Evolución del aprendizaje (20 rondas)
│   ├── experiment_02.py      # Agente con vs sin aprendizaje
│   └── results/              # CSVs y gráficas generadas
|        ├── exp01_graficas.png # Gráficas generadas para experimento 1
|        ├── exp02_graficas.png # Gráficas generadas para experimento 2
|        ├── exp01_resultados.csv # CSV para experimento 1
|        ├── exp02_resultados.csv # CSV para experimento 2
|
├── app.py                    # Interfaz de consola
├── metrics.py                # Cálculo de métricas
└── README.md
```

---

## Requisitos

```
Python 3.10+
pandas
numpy
matplotlib
```

Instalar dependencias:

```bash
pip install pandas numpy matplotlib
```

---

## Cómo ejecutar

### Sesión interactiva

```bash
python app.py
```

Opciones del menú:
- `[1]` Iniciar sesión normal
- `[2]` Iniciar sesión con desglose de `f(s,a)` visible (ideal para demo)
- `[3]` Reiniciar perfil del usuario
- `[4]` Salir

## Ejemplo de ejecución
Modo 2 (desglose de decisión visible):

```
==================================================
     CLOTHES RECOMMENDER — Agente IA
==================================================

CONFIGURACIÓN INICIAL DE PREFERENCIAS
─────────────────────────────────────────────
  Colores disponibles: azul, rojo, verde, negro, blanco, gris
  ¿Qué colores prefieres? → azul

  Telas disponibles: algodón, poliéster, lino, mezclilla, franela, piqué, lana, cuero
  ¿Qué telas prefieres? → algodón

  Marcas disponibles: Nike, Adidas, Zara, H&M, Levis, Lacoste, Ralph Lauren, ...
  ¿Qué marcas prefieres? → Nike

     Preferencias registradas:
     Colores: ['azul']
     Telas:   ['algodón']
     Marcas:  ['Nike']

  ¡Comenzando recomendaciones!

  ── Ronda 1 ──────────────────────────────────
==================================================
           RECOMENDACIÓN DEL AGENTE
==================================================
  Nombre:    Camiseta Básica Azul
  Color:     azul
  Tela:      algodón
  Marca:     Nike
  Categoría: camiseta
  Precio:    $299

─────────────────────────────────────────────────
  DECISIÓN DEL AGENTE
─────────────────────────────────────────────────
  Producto:    Camiseta Básica Azul
  Score total: 0.8500

  Desglose f(s,a):
    w1=0.50 × similitud=0.8333   → 0.4167
    w2=0.30 × preferencia=0.5000 → 0.1500
    w3=0.20 × novedad=1.0000     → 0.2000
    ─────────────────────────────────────
    TOTAL f(s,a) = 0.8500
─────────────────────────────────────────────────

  ¿Qué te parece esta recomendación?
  [L] Me gusta   [D] No me gusta   [S] Salir   [E] Ver estado del agente
  → L

  LIKE → 'Camiseta Básica Azul'
  Atributos: color=azul, tela=algodón, marca=Nike
  Cp['azul']:   1.0 → 2.0
  Tp['algodón']: 1.0 → 2.0
  Mp['Nike']:   1.0 → 2.0

  ── Ronda 2 ──────────────────────────────────
==================================================
          RECOMENDACIÓN DEL AGENTE
==================================================
  Nombre:    Sudadera Azul
  Color:     azul
  Tela:      poliéster
  Marca:     Nike
  Categoría: sudadera
  Precio:    $699

  Score total: 0.8711   ← subió respecto a la ronda anterior

  ¿Qué te parece esta recomendación?
  → S

==================================================
          RESUMEN DE SESIÓN
==================================================
  Recomendaciones totales: 1
  Likes:                   1
  Dislikes:                0
  Tasa de aceptación:      100.0%
```

El estado del agente queda guardado en `data/user_profile.json`. Al ejecutar
el sistema de nuevo, el agente retoma las preferencias aprendidas sin necesidad
de configurarlas desde cero.


### Experimentos

```bash
# Experimento 1: Evolución del aprendizaje
python experiments/experiment_01.py

# Experimento 2: Con aprendizaje vs sin aprendizaje
python experiments/experiment_02.py
```

Los resultados (CSVs + gráficas PNG) se guardan en `experiments/results/`.

---

## Ciclo del agente

```
Percepción → Estado → Decisión → Acción → Retroalimentación
     ↑                                            │
     └────────────────────────────────────────────┘
```

| Fase | Implementación | Archivo |
|---|---|---|
| Percepción | Lee preferencias y historial | `state.py` |
| Estado | `S = (Cp, Tp, Mp, H, R)` | `state.py` |
| Decisión | `a* = argmax f(s,a)` | `decision.py` |
| Acción | Recomienda producto | `recommender.py` |
| Aprendizaje | Actualiza Cp, Tp, Mp, w1-w3 | `feedback.py` |

---

## Métricas

| Métrica | Descripción |
|---|---|
| Tasa de aceptación | likes / total de recomendaciones |
| Precisión de coincidencia | atributos coincidentes / atributos evaluados |
| Evolución de pesos | cambio de w1, w2, w3 a lo largo del tiempo |

---

## Resultados de experimentos

| Experimento | Resultado |
|---|---|
| Exp 01: Aprendizaje (20 rondas) | Tasa de aceptación: 100% al final |
| Exp 02: Con vs Sin aprendizaje | Agente inteligente +20pp sobre baseline aleatorio |

---

## Herramientas

- Python 3.10+
- pandas — manejo del catálogo
- matplotlib — visualización de experimentos
- JSON — persistencia del estado del agente
