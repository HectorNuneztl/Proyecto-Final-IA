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

### Experimentos

```bash
# Experimento 1: Evolución del aprendizaje
python experiments/experiment_01.py

# Experimento 2: Con aprendizaje vs sin aprendizaje
python experiments/experiment_02.py
```

Los resultados (CSVs + gráficas PNG) se guardan en `experiments/results/`.

---

## 🔁 Ciclo del agente

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

## Tecnologías

- Python 3.10+
- pandas — manejo del catálogo
- matplotlib — visualización de experimentos
- JSON — persistencia del estado del agente
