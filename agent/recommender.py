"""
Agente Principal del sistema

Ciclo:
    Percepción → Estado → Decisión → Acción → Retroalimentación

Conecta todos los componentes y expone una interfaz limpia para la aplicación principal.

Ciclo del agente (por ronda):
    1. percibir()   → leer estado actual S
    2. decidir()    → calcular a* = argmax f(s,a)
    3. actuar()     → mostrar recomendación al usuario
    4. aprender()   → procesar feedback y actualizar S
"""

import pandas as pd
import os
from agent.state    import AgentState
from agent.decision import decidir, imprimir_decision
from agent.feedback import procesar_feedback, ajustar_pesos, imprimir_cambios

# Ruta al catálogo de productos
CATALOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.csv')

# Opciones válidas de atributos (para validar entrada del usuario)
COLORES_VALIDOS = ['azul', 'rojo', 'verde', 'negro', 'blanco', 'gris']
TELAS_VALIDAS   = ['algodón', 'poliéster', 'lino', 'mezclilla', 'franela', 'piqué', 'lana', 'cuero']
MARCAS_VALIDAS  = ['Nike', 'Adidas', 'Zara', 'H&M', 'Levis', 'Lacoste',
                   'Ralph Lauren', 'Tommy Hilfiger', 'Calvin Klein', 'Puma']


class ClothesRecommenderAgent:
    """
    Agente inteligente de recomendación de ropa.

    Implementa el ciclo completo:
        Percepción → Estado → Decisión → Acción

    Atributos:
        state   → estado del agente S = (Cp, Tp, Mp, H, R)
        catalog → DataFrame con todos los productos disponibles
    """

    def __init__(self):
        self.state   = AgentState()
        self.catalog = pd.read_csv(CATALOG_PATH)
        print("\n" + "═" * 50)
        print("     CLOTHES RECOMMENDER — Agente IA")
        print("═" * 50)

    # PERCEPCIÓN
    def percibir_preferencias_iniciales(self):
        """
        PERCEPCIÓN: El agente solicita las preferencias iniciales del usuario.

        Esto inicializa el estado S si el usuario no tiene historial previo.
        Si ya existe un perfil guardado, se reutiliza (memoria entre sesiones).
        """
        tiene_perfil = bool(self.state.Cp or self.state.Tp or self.state.Mp)

        if tiene_perfil:
            print("\n Perfil existente detectado. Continuando sesión anterior.")
            print(self.state.resumen())
            respuesta = input("\n  ¿Deseas actualizar tus preferencias? (s/n): ").strip().lower()
            if respuesta != 's':
                return

        print("\n CONFIGURACIÓN INICIAL DE PREFERENCIAS")
        print("─" * 45)
        print("  Responde con valores separados por coma.")
        print("  Puedes dejar en blanco si no tienes preferencia.")

        # Solicitar colores
        print(f"\n  Colores disponibles: {', '.join(COLORES_VALIDOS)}")
        entrada = input("  ¿Qué colores prefieres? → ").strip().lower()
        colores = [c.strip() for c in entrada.split(',') if c.strip() in COLORES_VALIDOS] if entrada else []

        # Solicitar telas
        print(f"\n  Telas disponibles: {', '.join(TELAS_VALIDAS)}")
        entrada = input("  ¿Qué telas prefieres? → ").strip().lower()
        telas = [t.strip() for t in entrada.split(',') if t.strip() in TELAS_VALIDAS] if entrada else []

        # Solicitar marcas
        print(f"\n  Marcas disponibles: {', '.join(MARCAS_VALIDAS)}")
        entrada = input("  ¿Qué marcas prefieres? → ").strip()
        marcas_norm = {m.lower(): m for m in MARCAS_VALIDAS}
        marcas = [marcas_norm[m.strip().lower()] for m in entrada.split(',')
                  if m.strip().lower() in marcas_norm] if entrada else []

        if not colores and not telas and not marcas:
            print("\n    Sin preferencias iniciales. El agente explorará el catálogo.")
        else:
            self.state.registrar_preferencias_iniciales(colores, telas, marcas)
            print(f"\n   Preferencias registradas:")
            if colores: print(f"     Colores: {colores}")
            if telas:   print(f"     Telas:   {telas}")
            if marcas:  print(f"     Marcas:  {marcas}")

    # DECISIÓN + ACCIÓN
    def recomendar(self, mostrar_desglose: bool = True) -> dict | None:
        """
        DECISIÓN + ACCIÓN: El agente elige y presenta una recomendación.

        1. Llama a decidir() → ejecuta argmax f(s,a) sobre todo el catálogo
        2. Muestra el producto ganador
        3. Retorna el producto para que el ciclo pueda pedir feedback

        Si todos los productos ya fueron vistos, reinicia la novedad
        para no quedar atascado.
        """
        # Verificar si ya se vieron todos los productos
        if len(self.state.productos_vistos()) >= len(self.catalog):
            print("\n    Ya revisaste todo el catálogo. ¡Reiniciando novedad!")
            for item in self.state.H:
                pass  # El historial se mantiene, solo se "olvida" qué fue visto

        # Obtener la mejor decisión
        top1 = decidir(self.catalog, self.state, top_n=1)

        if not top1:
            print("   No hay productos disponibles.")
            return None

        decision = top1[0]

        # Obtener fila completa del producto desde el catálogo
        fila = self.catalog[self.catalog['id'] == decision['producto_id']].iloc[0]
        producto = fila.to_dict()

        # Mostrar la recomendación
        print("\n" + "═" * 50)
        print("    RECOMENDACIÓN DEL AGENTE")
        print("═" * 50)
        print(f"  Nombre:    {producto['nombre']}")
        print(f"  Color:     {producto['color']}")
        print(f"  Tela:      {producto['tela']}")
        print(f"  Marca:     {producto['marca']}")
        print(f"  Categoría: {producto['categoria']}")
        print(f"  Precio:    ${producto['precio']}")

        if mostrar_desglose:
            imprimir_decision(decision)

        return producto

    # RETROALIMENTACIÓN / APRENDIZAJE
    def solicitar_feedback(self, producto: dict) -> str | None:
        """
        ACCIÓN: El agente solicita retroalimentación al usuario.

        El feedback es la señal de aprendizaje del sistema.
        Retorna: 'like', 'dislike', o None si el usuario quiere salir.
        """
        print("\n  ¿Qué te parece esta recomendación?")
        print("  [L] Me gusta   [D] No me gusta   [S] Salir   [E] Ver estado del agente")

        while True:
            opcion = input("  → ").strip().upper()
            if opcion in ('L', 'D', 'S', 'E'):
                break
            print("    Opción no válida. Elige L, D, S o E.")

        if opcion == 'S':
            return None
        if opcion == 'E':
            print(self.state.resumen())
            return self.solicitar_feedback(producto)  # Volver a pedir feedback
        return 'like' if opcion == 'L' else 'dislike'

    def aprender(self, producto: dict, feedback: str):
        """
        APRENDIZAJE: Actualiza el estado del agente con el feedback.

        Llama a:
            1. procesar_feedback() → actualiza Cp, Tp, Mp, H
            2. ajustar_pesos()     → ajusta w1, w2, w3 según desempeño
        """
        cambios = procesar_feedback(producto, feedback, self.state)
        imprimir_cambios(cambios)
        ajustar_pesos(self.state)


    # CICLO COMPLETO
    def ejecutar_ciclo(self, mostrar_desglose: bool = True):
        """
        Ejecuta UNA ronda completa del ciclo del agente:
            Percepción → Decisión → Acción → Retroalimentación

        Retorna True si debe continuar, False si el usuario quiere salir.
        """
        producto = self.recomendar(mostrar_desglose=mostrar_desglose)
        if producto is None:
            return False

        feedback = self.solicitar_feedback(producto)
        if feedback is None:
            return False

        self.aprender(producto, feedback)
        return True

    def ejecutar_sesion(self, mostrar_desglose: bool = True):
        """
        Ejecuta una sesión completa del agente:
            - Percibe preferencias iniciales
            - Repite el ciclo hasta que el usuario decida salir
            - Muestra métricas de la sesión al finalizar
        """
        self.state.incrementar_sesion()
        self.percibir_preferencias_iniciales()

        print("\n\n   ¡Comenzando recomendaciones!")
        print("  El agente aprenderá de tu feedback en cada ronda.\n")

        continuar = True
        ronda = 1
        while continuar:
            print(f"\n  ── Ronda {ronda} ──────────────────────────────")
            continuar = self.ejecutar_ciclo(mostrar_desglose=mostrar_desglose)
            ronda += 1

        self._mostrar_resumen_sesion()

    def _mostrar_resumen_sesion(self):
        """Muestra un resumen al finalizar la sesión."""
        likes    = self.state.data['likes_totales']
        dislikes = self.state.data['dislikes_totales']
        total    = likes + dislikes
        tasa     = (likes / total * 100) if total > 0 else 0

        print("\n" + "═" * 50)
        print("    RESUMEN DE SESIÓN")
        print("═" * 50)
        print(f"  Recomendaciones totales: {total}")
        print(f"  Likes:                   {likes}")
        print(f"  Dislikes:                {dislikes}")
        print(f"  Tasa de aceptación:      {tasa:.1f}%")
        print()
        print(self.state.resumen())
        print("\n  ¡Hasta pronto! El agente recordará tus preferencias.")
        print("═" * 50)