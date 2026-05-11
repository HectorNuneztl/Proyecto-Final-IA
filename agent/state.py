"""
Estado del agente.

Arquitectura:
    S = (Cp, Tp, Mp, H, R)

Donde:
    Cp = preferencias de color       (diccionario color -> peso)
    Tp = preferencias de tela        (diccionario tela  -> peso)
    Mp = preferencias de marca       (diccionario marca -> peso)
    H  = historial de interacciones  (lista de productos vistos + feedback)
    R  = última recomendación        (id del producto recomendado)

El estado se persiste en user_profile.json para simular
memoria entre sesiones del agente.
"""

import json
import os

# Ruta al perfil del usuario
PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_profile.json')


class AgentState:
    """
    Clase que encapsula el estado completo del agente.
    
    El agente percibe el entorno leyendo este estado y lo actualiza
    después de cada interacción con el usuario.
    """

    def __init__(self):
        """Carga el estado desde el archivo JSON o crea uno nuevo."""
        self.data = self._cargar_perfil()

    # Propiedades que exponen S = (Cp, Tp, Mp, H, R)
    @property
    def Cp(self) -> dict:
        """Preferencias de color: {color: puntaje_acumulado}"""
        return self.data['preferencias']['colores']

    @property
    def Tp(self) -> dict:
        """Preferencias de tela: {tela: puntaje_acumulado}"""
        return self.data['preferencias']['telas']

    @property
    def Mp(self) -> dict:
        """Preferencias de marca: {marca: puntaje_acumulado}"""
        return self.data['preferencias']['marcas']

    @property
    def H(self) -> list:
        """Historial de interacciones previas"""
        return self.data['historial']

    @property
    def R(self):
        """Última recomendación realizada"""
        return self.data['ultima_recomendacion']

    @property
    def pesos(self) -> dict:
        """Pesos w1, w2, w3 de la función de decisión"""
        return self.data['pesos']

    # Métodos para actualizar el estado
    def registrar_preferencias_iniciales(self, colores: list, telas: list, marcas: list):
        """
        Registra las preferencias iniciales declaradas por el usuario.
        Cada preferencia declarada recibe un puntaje base de 1.0.
        
        Esto inicializa Cp, Tp y Mp del estado S.
        """
        for color in colores:
            self.Cp[color] = self.Cp.get(color, 0) + 1.0

        for tela in telas:
            self.Tp[tela] = self.Tp.get(tela, 0) + 1.0

        for marca in marcas:
            self.Mp[marca] = self.Mp.get(marca, 0) + 1.0

        self.guardar()

    def registrar_feedback(self, producto: dict, feedback: str):
        """
        Actualiza el estado según el feedback del usuario.
        
        LIKE    → suma +1.0 a los atributos del producto en Cp, Tp, Mp
        DISLIKE → resta -0.5 a los atributos del producto

        Esta es la función de aprendizaje del agente:
        el estado cambia → las próximas decisiones cambian.
        """
        delta = +1.0 if feedback == 'like' else -0.5

        color = producto.get('color', '')
        tela  = producto.get('tela', '')
        marca = producto.get('marca', '')

        # Actualizar Cp
        if color:
            self.Cp[color] = self.Cp.get(color, 0) + delta

        # Actualizar Tp
        if tela:
            self.Tp[tela] = self.Tp.get(tela, 0) + delta

        # Actualizar Mp
        if marca:
            self.Mp[marca] = self.Mp.get(marca, 0) + delta

        # Actualizar historial H
        self.H.append({
            'producto_id': producto['id'],
            'nombre':      producto['nombre'],
            'feedback':    feedback,
            'color':       color,
            'tela':        tela,
            'marca':       marca
        })

        # Contadores globales
        if feedback == 'like':
            self.data['likes_totales'] += 1
        else:
            self.data['dislikes_totales'] += 1

        # Actualizar R
        self.data['ultima_recomendacion'] = producto['id']

        self.guardar()

    def incrementar_sesion(self):
        """Registra una nueva sesión del agente."""
        self.data['sesiones'] += 1
        self.guardar()

    def productos_vistos(self) -> set:
        """Devuelve el conjunto de IDs de productos ya mostrados."""
        return {item['producto_id'] for item in self.H}

    def resumen(self) -> str:
        """Muestra un resumen legible del estado actual del agente."""
        lineas = [
            "=" * 45,
            "  ESTADO ACTUAL DEL AGENTE",
            "=" * 45,
            f"  Sesiones:        {self.data['sesiones']}",
            f"  Likes totales:   {self.data['likes_totales']}",
            f"  Dislikes totales:{self.data['dislikes_totales']}",
            "",
            f"  Cp (colores):    {self.Cp}",
            f"  Tp (telas):      {self.Tp}",
            f"  Mp (marcas):     {self.Mp}",
            "",
            f"  Pesos actuales:",
            f"    w1 (similitud):   {self.pesos['w1_similitud']:.3f}",
            f"    w2 (preferencia): {self.pesos['w2_preferencia']:.3f}",
            f"    w3 (novedad):     {self.pesos['w3_novedad']:.3f}",
            "=" * 45,
        ]
        return "\n".join(lineas)

    # Persistencia
    def _cargar_perfil(self) -> dict:
        """Lee el estado desde el archivo JSON."""
        with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    def guardar(self):
        """Persiste el estado actualizado en el archivo JSON."""
        with open(PROFILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)