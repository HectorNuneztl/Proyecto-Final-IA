"""
app.py
======
Punto de entrada principal del sistema Clothes Recommender.

Ejecutar con:
    python app.py

Modos disponibles:
    1 → Sesión interactiva normal
    2 → Sesión con desglose de decisión visible (ideal para presentaciones)
    3 → Reiniciar perfil del usuario
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from agent.recommender import ClothesRecommenderAgent

PROFILE_PATH = os.path.join('data', 'user_profile.json')

PERFIL_VACIO = {
    "preferencias": {"colores": {}, "telas": {}, "marcas": {}},
    "pesos": {
        "w1_similitud": 0.5,
        "w2_preferencia": 0.3,
        "w3_novedad": 0.2
    },
    "historial": [],
    "ultima_recomendacion": None,
    "sesiones": 0,
    "likes_totales": 0,
    "dislikes_totales": 0
}


def menu_principal():
    print("\n" + "═" * 50)
    print("     CLOTHES RECOMMENDER")
    print("   Agente Inteligente de Recomendación de Ropa")
    print("═" * 50)
    print("\n  Selecciona un modo:")
    print("  [1] Iniciar sesión")
    print("  [2] Iniciar sesión con desglose de decisión")
    print("  [3] Reiniciar perfil del usuario")
    print("  [4] Salir")
    print()
    return input("  → ").strip()


def reiniciar_perfil():
    with open(PROFILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(PERFIL_VACIO, f, ensure_ascii=False, indent=2)
    print("\n   Perfil reiniciado. El agente comenzará desde cero.")


def main():
    while True:
        opcion = menu_principal()

        if opcion == '1':
            agente = ClothesRecommenderAgent()
            agente.ejecutar_sesion(mostrar_desglose=False)

        elif opcion == '2':
            agente = ClothesRecommenderAgent()
            agente.ejecutar_sesion(mostrar_desglose=True)

        elif opcion == '3':
            confirmacion = input("\n    ¿Seguro que deseas borrar el perfil? (s/n): ").strip().lower()
            if confirmacion == 's':
                reiniciar_perfil()

        elif opcion == '4':
            print("\n  ¡Hasta luego! \n")
            break

        else:
            print("\n    Opción no válida.")


if __name__ == '__main__':
    main()