from ClaseJuego import ClaseJuego
from abecedario import ClasificadorSenia  # Importamos ClasificadorSenia
import threading
import time
import customtkinter as ct
import tkinter as tk
import cv2
from PIL import Image


class Juego_senias:
    def __init__(self, callback):
        # Inicialización de la clase base y otras variables
        self.callback = callback
        self.ObjetoJuego = ClaseJuego()  # Lógica del juego del ahorcado
        self.clasificador_senia = ClasificadorSenia()  # Inicializamos ClasificadorSenia
        self.EstamosJugando = False
        # Variables para la interfaz y la cámara
        self.cap = cv2.VideoCapture(0)
        self.frame_camara, self.video_frame, self.video_label = None, None, None
        # Variables para el juego
        self.EntradaTexto = None
        self.Texto1, self.Texto2 = None, None  # Inicializadas más tarde
        #self.Texto1, self.Texto2 = tk.StringVar(), tk.StringVar()
        #self.Texto2.set("Tus jugadas: ")

    def ejecutar(self):
        # Configuración de la interfaz
        app = ct.CTk()
        app.geometry("1200x690")
        app.title("Juego del Ahorcado")
        app.resizable(False, False)

        #Crear variables después de inicializar la raíz
        self.Texto1 = tk.StringVar()
        self.Texto2 = tk.StringVar()
        self.Texto2.set("Tus jugadas: ")

        # Crear elementos de la interfaz
        self.titulo(app)
        self.camara(app)
        self.munieco(app)
        self.palabra(app)
        self.botones(app)
        self.JuegoNuevo()

        # Iniciar cámara para detección de manos
        self.iniciar_hilo_camara()

        app.mainloop()

    def iniciar_hilo_camara(self):
        # Inicia un hilo para capturar las letras detectadas por la cámara
        threading.Thread(target=self.procesar_camara, daemon=True).start()

    def procesar_camara(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                continue

            letra_detectada, frame_procesado = self.clasificador_senia.procesar_mano(frame)

            if letra_detectada:
                self.EntradaTexto.configure(text=letra_detectada)
                self.BotonEnviar()  # Enviar automáticamente la letra detectada al juego

            # Actualizar el feed de la cámara en la interfaz
            frame_procesado = cv2.cvtColor(frame_procesado, cv2.COLOR_BGR2RGBA)
            frame_procesado = cv2.flip(frame_procesado, 1)
            img = Image.fromarray(frame_procesado)
            self.video_label.configure(image=ct.CTkImage(dark_image=img, size=(500, 370)))
    # todo LO RELACIONADO CON EL JUEGO DEL AHORCADO
    def JuegoNuevo(self):
        self.EstamosJugando = True
        self.ObjetoJuego.nuevojuego()
        self.__ActualizarVista()

    def BotonEnviar(self):
        if self.EstamosJugando:
            letra = self.EntradaTexto.cget("text")
            if letra:
                self.ObjetoJuego.jugar(letra.upper())
                if self.ObjetoJuego.getVictoria() or not self.ObjetoJuego.getJugadorEstaVivo():
                    self.EstamosJugando = False
                self.__ActualizarVista()
        else:
            self.JuegoNuevo()
        self.EntradaTexto.configure(text="")

    def __ActualizarVista(self):
        if self.EstamosJugando:
            # Actualizamos la palabra oculta y las letras usadas
            letrero=""
            for x in self.ObjetoJuego.getLetrero(): letrero+=x+" "  
            self.Texto1.set(letrero)
            mensaje="Tus jugadas: "
            for x in self.ObjetoJuego.getLetrasUsadas():mensaje+=x
            self.Texto2.set(mensaje)
            #self.Texto1.set(" ".join(self.ObjetoJuego.getLetrero()))
            #self.Texto2.set("Tus jugadas: " + ", ".join(self.ObjetoJuego.getLetrasUsadas()))
        else:
            # Mensajes finales
            if self.ObjetoJuego.getVictoria():
                self.Texto1.set("¡Felicidades! Ganaste.")
            else:
                self.Texto1.set(f"Lo siento, perdiste. La palabra era: {self.ObjetoJuego.getPalabra()}")
            self.Texto2.set("")
        self.__Dibujo() # esto acciona para dibujar el hombrecito

    def titulo(self, app):
        font_title = ct.CTkFont(family='Consolas', weight='bold', size=25)
        title = ct.CTkLabel(app, text='JUEGO DEL AHORCADO CON SEÑAS', fg_color='steelblue',
                            text_color='white', height=30, font=font_title, corner_radius=8)
        title.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(5, 4), padx=(7, 10))

    def camara(self, app):
        self.video_frame = ct.CTkFrame(master=app, corner_radius=12)
        self.video_frame.grid(row=1, column=0, columnspan=2, padx=(10, 10), pady=(5, 5))

        # Etiqueta para el feed de video
        self.video_label = ct.CTkLabel(master=self.video_frame, text='', width=600, height=370, corner_radius=12)
        self.video_label.pack(fill=ct.BOTH, padx=(0, 0), pady=(0, 0))

    # Interfaz del ahorcado muñeco
    def munieco(self, app):
        #self.EntradaTexto = ct.CTkLabel(app, text='', fg_color="black", width=200, height=50)
        #self.EntradaTexto.grid(row=2, column=0)
        self.frame_munieco=ct.CTkFrame(master=app, width=600, height=210, fg_color="transparent")
        self.frame_munieco.grid(row=2, column=0, padx = (12,5),pady=(5,3))

        self.Lienzo=ct.CTkCanvas(self.frame_munieco, width=200, height=200, bg="dark green")
        self.Lienzo.pack(side=ct.LEFT, padx=(15, 20), pady=5)

        self.EntradaTexto=ct.CTkLabel(self.frame_munieco, width=220, height=200, justify=ct.CENTER)
        self.EntradaTexto.pack(side=ct.RIGHT, padx=(20, 5), pady=5)
        myfont = ct.CTkFont(
            family='Consolas',
            weight='bold',
            size=140
        )
        self.EntradaTexto.configure(fg_color="black", font=myfont, text='')

    def palabra(self, app):
        self.Texto1.set("_ " * len(self.ObjetoJuego.getPalabra()))
        etiqueta_palabra = ct.CTkLabel(app, textvariable=self.Texto1, fg_color="white", width=600, height=100)
        etiqueta_palabra.grid(row=2, column=1)

    def botones(self, app):
        boton_nuevo = ct.CTkButton(app, text="Nuevo Juego", command=self.JuegoNuevo)
        boton_nuevo.grid(row=3, column=0)

        boton_salir = ct.CTkButton(app, text="Salir", command=app.destroy)
        boton_salir.grid(row=3, column=1)

    # para dibujar el ahorcado
    def __Dibujo(self):
        
        if self.EstamosJugando:
            oportunidades=self.ObjetoJuego.getOportunidades()
            if oportunidades==1:
                self.Lienzo.delete("all")
                self.Lienzo.create_line(30,185, 30,20, 100,20, 100,45 ,width=5,fill="white")#horca
                self.Lienzo.create_line(15,193, 15,185, 185,185, 185,193,width=5,fill="white")#horca
                self.Lienzo.create_oval(85,45, 115,75, width=3,fill="dark green",outline="white")#cabeza
                self.Lienzo.create_line(100,75, 100,135, width=3,fill="white")#torso
                self.Lienzo.create_line(100,82, 70,112, width=3,fill="white")#brazo1
                self.Lienzo.create_line(100,82, 130,112, width=3,fill="white")#brazo2
                self.Lienzo.create_line(100,135, 70,165, width=3,fill="white")#pierna1
            elif oportunidades==2:
                self.Lienzo.delete("all")
                self.Lienzo.create_line(30,185, 30,20, 100,20, 100,45 ,width=5,fill="white")#horca
                self.Lienzo.create_line(15,193, 15,185, 185,185, 185,193,width=5,fill="white")#horca
                self.Lienzo.create_oval(85,45, 115,75, width=3,fill="dark green",outline="white")#cabeza
                self.Lienzo.create_line(100,75, 100,135, width=3,fill="white")#torso
                self.Lienzo.create_line(100,82, 70,112, width=3,fill="white")#brazo1
                self.Lienzo.create_line(100,82, 130,112, width=3,fill="white")#brazo2
            elif oportunidades==3:
                self.Lienzo.delete("all")
                self.Lienzo.create_line(30,185, 30,20, 100,20, 100,45 ,width=5,fill="white")#horca
                self.Lienzo.create_line(15,193, 15,185, 185,185, 185,193,width=5,fill="white")#horca
                self.Lienzo.create_oval(85,45, 115,75, width=3,fill="dark green",outline="white")#cabeza
                self.Lienzo.create_line(100,75, 100,135, width=3,fill="white")#torso
                self.Lienzo.create_line(100,82, 70,112, width=3,fill="white")#brazo1
            elif oportunidades==4:
                self.Lienzo.delete("all")
                self.Lienzo.create_line(30,185, 30,20, 100,20, 100,45 ,width=5,fill="white")#horca
                self.Lienzo.create_line(15,193, 15,185, 185,185, 185,193,width=5,fill="white")#horca
                self.Lienzo.create_oval(85,45, 115,75, width=3,fill="dark green",outline="white")#cabeza
                self.Lienzo.create_line(100,75, 100,135, width=3,fill="white")#torso
            elif oportunidades==5:
                self.Lienzo.delete("all")
                self.Lienzo.create_line(30,185, 30,20, 100,20, 100,45 ,width=5,fill="white")#horca
                self.Lienzo.create_line(15,193, 15,185, 185,185, 185,193,width=5,fill="white")#horca
                self.Lienzo.create_oval(85,45, 115,75, width=3,fill="dark green",outline="white")#cabeza
            else:
                self.Lienzo.delete("all")
                self.Lienzo.create_line(30,185, 30,20, 100,20, 100,45 ,width=5,fill="white")#horca
                self.Lienzo.create_line(15,193, 15,185, 185,185, 185,193,width=5,fill="white")#horca
        else:
            if self.ObjetoJuego.getVictoria():
                self.Lienzo.delete("all")
                self.Lienzo.create_oval(85,45, 115,75, width=3,fill="dark green",outline="white")#cabeza
                self.Lienzo.create_line(100,75, 100,135, width=3,fill="white")#torso
                self.Lienzo.create_line(100,87, 70,57, width=3,fill="white")#brazo1
                self.Lienzo.create_line(100,87, 130,57, width=3,fill="white")#brazo2
                self.Lienzo.create_line(100,135, 70,165, width=3,fill="white")#pierna1
                self.Lienzo.create_line(100,135, 130,165, width=3,fill="white")#pierna2
            else:
                self.Lienzo.delete("all")
                self.Lienzo.create_line(30,185, 30,20, 100,20, 100,45 ,width=5,fill="white")#horca
                self.Lienzo.create_line(15,193, 15,185, 185,185, 185,193,width=5,fill="white")#horca
                self.Lienzo.create_oval(85,45, 115,75, width=3,fill="dark green",outline="white")#cabeza
                self.Lienzo.create_line(100,75, 100,135, width=3,fill="white")#torso
                self.Lienzo.create_line(100,82, 70,112, width=3,fill="white")#brazo1
                self.Lienzo.create_line(100,82, 130,112, width=3,fill="white")#brazo2
                self.Lienzo.create_line(100,135, 70,165, width=3,fill="white")#pierna1
                self.Lienzo.create_line(100,135, 130,165, width=3,fill="white")#pierna2

if __name__ == "__main__":
    juego = Juego_senias(callback=None)
    juego.ejecutar()