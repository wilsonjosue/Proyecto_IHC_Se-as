import pygame
import random
from abecedario import ClasificadorSenia
import cv2
from threading import Thread
from PIL import Image
import numpy as np

# Configuración de la pantalla
ANCHO = 800
ALTO = 600
COLOR_LETRA = (0, 0, 0)
FPS = 60

class JuegoLetras:
    def __init__(self, callback):
        self.callback = callback
        self.pantalla = None
        self.reloj = None
        self.fuente = None
        self.fondo = None
        self.clasificador_senia = None
        self.camara = None
        self.letras = []
        self.velocidad = 2
        self.letra_detectada = None
        self.jugando = False
        self.puntuacion = 0
        self.vidas = 50
        self.boton_empezar = None
        self.boton_salir = None

    def inicializar(self):
        """Inicializa todos los componentes necesarios para el juego."""
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Minijuego: Letras que caen")
        self.reloj = pygame.time.Clock()
        self.fuente = pygame.font.Font(None, 74)

        # Cargar la imagen de fondo
        self.fondo = pygame.image.load("fondo1.jpg")
        self.fondo = pygame.transform.scale(self.fondo, (ANCHO, ALTO))

        # Inicializar detección de señas
        self.clasificador_senia = ClasificadorSenia()
        self.camara = cv2.VideoCapture(0)
        self.camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.camara.isOpened():
            print("Error: No se pudo acceder a la cámara")
            self.jugando = False
            return

        # Configurar botones
        self.boton_empezar = pygame.Rect(100, 500, 200, 50)
        self.boton_salir = pygame.Rect(500, 500, 200, 50)

    def ejecutar(self):
        """Bucle principal del juego."""
        # Inicializar el juego solo cuando se ejecute
        self.inicializar()

        if not self.jugando:  # Si no se pudo inicializar la cámara
            print("El juego no puede iniciarse debido a problemas con la cámara.")
            return

        self.dibujar_botones()
        pygame.display.update()

        # Bandera de estado
        en_juego = False

        while not en_juego:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                # Verificar clic en el botón "Empezar"
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if self.boton_empezar.collidepoint(evento.pos):
                        en_juego = True
                        Thread(target=self.procesar_camara, daemon=True).start()

                # Verificar clic en el botón "Salir"
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if self.boton_salir.collidepoint(evento.pos):
                        pygame.quit()
                        exit()

            self.dibujar_botones()
            pygame.display.update()

        # Bucle principal del juego
        contador = 0
        while self.jugando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.jugando = False

            if contador % 90 == 0:
                self.generar_letra()

            self.mover_letras()
            self.verificar_colision()

            for letra in self.letras:
                if letra["posicion"][1] >= ALTO - 50:
                    self.letras.remove(letra)
                    self.vidas -= 1

            if self.vidas <= 0:
                self.jugando = False

            self.dibujar()
            contador += 1
            self.reloj.tick(FPS)

        self.mostrar_puntuacion_final()

