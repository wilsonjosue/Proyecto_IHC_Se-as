from ClaseJuego import ClaseJuego 
from asistente import AsistenteVoz

import threading
import time
import customtkinter as ct
import tkinter as tk

import csv
import cv2
from PIL import Image
import mediapipe as mp
from model import KeyPointClassifier
import itertools
import copy

class Juego_senias(AsistenteVoz):

    def __init__(self, callback):
        # Llama al constructor de la clase base (AsistenteVoz)
        super().__init__()

        # Juego
        self.EstamosJugando = False
        self.estado_voz = True
        self.ObjetoJuego = ClaseJuego()

        # Camara
        self.frame_camara, self.video_frame, self.video_lable = None, None, None
        self.Camera_feed_start = None

        # Inicialización de variables y configuración inicial de la camara
        self.cap = cv2.VideoCapture(0)
        self.prev = ""
        self.keypoint_classifier = None
        self.keypoint_classifier_labels = []
        self.keypoint_classifier = None

        # Imagen
        self.frame_imagen = None

        # Muñeco
        self.frame_munieco, self.Lienzo, self.EntradaTexto = None, None, None

        # Palabra
        self.frame_palabra, self.Texto1, self.Etiqueta1 = None, None, None

        # Jugadas
        self.Texto2, self.Etiqueta2 = None, None

        # Botones
        self.frame_botones, self.BotonEnviarTexto, self.BotonSalir, self.BotonNuevoJuego = None, None, None, None

        # Salir a las opciones
        self.callback = callback

    def ejecutar(self):
        # Load the KeyPointClassifier model

        self.keypoint_classifier = KeyPointClassifier()

        # Read labels from a CSV file
        with open('model/keypoint_classifier/label.csv', encoding='utf-8-sig') as f:
            keypoint_classifier_labels_reader = csv.reader(f)
            self.keypoint_classifier_labels = [row[0] for row in keypoint_classifier_labels_reader]

        # INTERFAZ
        app = ct.CTk()
        app.geometry("1200x690")
        app.title("Juego del ahorcado")
        app.resizable(False, False)

        self.entrada_teclado(app)
        self.titulo(app)
        self.camara(app)
        #self.imagen()
        self.munieco(app)
        self.palabra(app)
        self.botones(app)
        self.JuegoNuevo()

        #self.iniciar_hilo_voz()

        app.mainloop()

        self.estado_voz = False

        print("*******************")

    def iniciar_hilo_voz(self):
        hilo_voz = threading.Thread(target=self.ejecutar_en_otro_hilo)
        hilo_voz.start()

    def ejecutar_en_otro_hilo(self):
        time.sleep(5)
        while self.estado_voz:
            captura_voz = self.enviar_voz_interfaz()

            print(f"recibido: {captura_voz}")

            if captura_voz == "enter":
                self.BotonEnviar()
            elif captura_voz == "nuevo juego":
                self.JuegoNuevo()
            elif captura_voz == "salir":
                self.estado_voz = False
            else:
                self.texto_a_audio("No pude escucharte, ¿podrías repetirlo?")

            time.sleep(0.5)  # Agrega una pausa para no consumir demasiados recursos



        print("TERMINADO....")

    def enviar_voz_interfaz(self):
        palabra = self.capturar_voz()
        if palabra["suceso"] and palabra["mensaje"]:
                return palabra["mensaje"].lower()

        if not palabra["suceso"]:
            print(f"\nAlgo no está bien. No puedo reconocer tu micrófono o no lo tienes enchufado. <{palabra['error']}>")
            self.texto_a_audio("Algo no está bien. No puedo reconocer tu micrófono o no lo tienes enchufado.")



    #TODO LO RELACIONADO CON LA ENTRADA DEL TECLADO
        
    def entrada_teclado(self,app):
            app.bind("<Return>",lambda x: self.BotonEnviar())
            app.bind("<Control_R>",lambda x: self.JuegoNuevo())
            app.bind("<Control_L>",lambda x: self.JuegoNuevo())
            app.bind("<Escape>",lambda x: exit())
            # Asociar la función update_text con el evento de presionar tecla
            app.bind("<Key>", self.update_text)

    def update_text(self, event):
        # Obtener la tecla presionada
        key_pressed = event.char

        # Omitir ciertas teclas
        if key_pressed not in {'\r', '\x1b', '\uf702', '\uf703'}:  # '\r': Enter, '\x1b': Escape, '\uf702' y '\uf703': Control
            # Actualizar el texto de la etiqueta
            self.EntradaTexto.configure(text=key_pressed)



    # TODO LO RELACIONADO CON EL JUEGO DEL AHORCADO

    def JuegoNuevo(self):
        self.EstamosJugando=True
        self.ObjetoJuego.nuevojuego()
        #AÑADIR IMAGEN PARA LA PALABRA
        self.__ActualizarVista()

    def BotonEnviar(self):
        if self.EstamosJugando:
            self.ObjetoJuego.jugar(self.EntradaTexto.cget("text"))
            if self.ObjetoJuego.getVictoria() or not(self.ObjetoJuego.getJugadorEstaVivo()):
                self.EstamosJugando=False
            self.__ActualizarVista()
        else:
            self.JuegoNuevo()
        self.EntradaTexto.configure(text="")


    def __ActualizarVista(self):
        if self.EstamosJugando:
            letrero=""
            for x in self.ObjetoJuego.getLetrero(): letrero+=x+" "
            self.Texto1.set(letrero)
            mensaje="Tus jugadas: "
            for x in self.ObjetoJuego.getLetrasUsadas():mensaje+=x
            self.Texto2.set(mensaje)
        else:
            if self.ObjetoJuego.getVictoria():
                self.Texto1.set("¡Felicidades Has ganado! :) ")
                self.Texto2.set("La palabra es "+self.ObjetoJuego.getPalabra())
            else:
                self.Texto1.set("Lo siento, perdiste :( ")
                self.Texto2.set("La palabra era "+self.ObjetoJuego.getPalabra())
        self.__Dibujo()


    
    # TODO LO RELACIONADO CON LA CAMARA
            
    # Function to open the camera and perform hand gesture recognition
    def open_camera1(self):
        self.Camera_feed_start.configure(state="disabled")
        width, height = 800, 600
        with mp.solutions.hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5, static_image_mode=False) as hands:
            _, frame = self.cap.read()
            opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            opencv_image = cv2.resize(opencv_image, (width, height))

            processFrames = hands.process(opencv_image)
            if processFrames.multi_hand_landmarks:
                for lm in processFrames.multi_hand_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(frame, lm, mp.solutions.hands.HAND_CONNECTIONS)

                    landmark_list = self.calc_landmark_list(frame, lm)

                    pre_processed_landmark_list = self.pre_process_landmark(landmark_list)

                    hand_sign_id = self.keypoint_classifier(pre_processed_landmark_list)

                    #print(f"hand_sign_id: {hand_sign_id}")
                    #print(f"len(self.keypoint_classifier_labels): {len(self.keypoint_classifier_labels)}")

                    if 0 <= hand_sign_id < len(self.keypoint_classifier_labels):
                        cur = self.keypoint_classifier_labels[hand_sign_id]
                        if cur == self.prev:
                            self.EntradaTexto.configure(text=cur)
                        elif cur:
                            self.prev = cur
                        #print(cur) #VALOR DE LA CAMARA ********************************************************
                    else:
                        print("Invalid hand_sign_id:", hand_sign_id)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            frame = cv2.flip(frame, 1)
            captured_image = Image.fromarray(frame)
            my_image = ct.CTkImage(dark_image=captured_image, size=(500, 370))
            self.video_lable.configure(image=my_image)
            self.video_lable.after(10, self.open_camera1)

    # Function to calculate the landmark points from an image
    def calc_landmark_list(self, image, landmarks):
        image_width, image_height = image.shape[1], image.shape[0]

        landmark_point = []

        # Iterate over each landmark and convert its coordinates
        for landmark in landmarks.landmark:
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)

            landmark_point.append([landmark_x, landmark_y])

        return landmark_point

    # Function to preprocess landmark data
    def pre_process_landmark(self, landmark_list):
        temp_landmark_list = copy.deepcopy(landmark_list)

        # Convert to relative coordinates
        base_x, base_y = 0, 0
        for index, landmark_point in enumerate(temp_landmark_list):
            if index == 0:
                base_x, base_y = landmark_point[0], landmark_point[1]

            temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
            temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

        # Convert to a one-dimensional list
        temp_landmark_list = list(
            itertools.chain.from_iterable(temp_landmark_list))

        # Normalization
        max_value = max(list(map(abs, temp_landmark_list)))

        def normalize_(n):
            return n / max_value

        temp_landmark_list = list(map(normalize_, temp_landmark_list))

        return temp_landmark_list
    


    # TODO LO RELACIONADO CON LA INTERFAZ

    def titulo(self, app):
        font_title = ct.CTkFont(family='Consolas', weight='bold', size=25)
        title = ct.CTkLabel(app,
                            text = 'JUEGO SEÑAS',
                            fg_color='steelblue',
                            text_color= 'white',
                            height= 30,
                            font=font_title,
                            corner_radius= 8)
        title.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(5,4), padx=(7,10))

    def camara(self,app):
        self.frame_camara = ct.CTkFrame(master=app)   #, width=680, height = 400
        self.frame_camara.grid(row=1, column=0, columnspan=2, padx = (14,5), pady=(3,0))

        # Create the video frame
        self.video_frame = ct.CTkFrame(master=self.frame_camara, corner_radius=12) #, width=650, height=330
        self.video_frame.pack(side=ct.LEFT,fill=ct.BOTH,expand = ct.TRUE ,padx=(10,10),pady=(5,5))

        # Create the video label
        self.video_lable = ct.CTkLabel(master=self.video_frame, text='', width=600, height=370, corner_radius=12) #cambios
        self.video_lable.pack(fill=ct.BOTH, padx=(0, 0), pady=(0, 0))

        # Cargar imagen de cámara apagada
        camera_off_image = ct.CTkImage(light_image=Image.open("camara_apagada.png"), size=(590, 350))
        self.video_lable.configure(image=camera_off_image)

        # Create a button to start the camera feed
        self.Camera_feed_start = ct.CTkButton(master=self.frame_camara, text='START', width=150, height=40, border_width=0, corner_radius=12, command=lambda: self.open_camera1()) #, command=lambda: self.camara_ia.open_camera1()
        self.Camera_feed_start.pack(side=ct.LEFT, pady=(5, 10))

    """def imagen(self):
        self.frame_imagen=ct.CTkFrame(master=self.app, width=750, height=400, fg_color="green") 
        self.frame_imagen.grid(row=1, column=1, padx = (10,10),pady=(10,10))"""

    def munieco(self,app):
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

    def palabra(self,app):
        self.frame_palabra=ct.CTkFrame(master=app, width=750, height=210, fg_color="transparent")
        self.frame_palabra.grid(row=2, column=1, padx = (20,10),pady=(10,10))

        #Palabra
        self.Texto1=tk.StringVar()

        self.Etiqueta1=ct.CTkLabel(self.frame_palabra, textvariable=self.Texto1, width=680, height=2)
        self.Etiqueta1.pack(side=ct.TOP, padx = (10,5), pady=(5,15))
        self.Etiqueta1.configure(fg_color="transparent", font=("Verdana",60))

        #Jugadas
        self.Texto2=tk.StringVar()
        self.Texto2.set("Tus jugadas: ")

        self.Etiqueta2=ct.CTkLabel(self.frame_palabra, textvariable=self.Texto2, width=40, height=2)
        self.Etiqueta2.pack(side=ct.BOTTOM, padx = (12,5), pady=(15,5))
        self.Etiqueta2.configure(fg_color="transparent" ,font=("Verdana",30))

    def botones(self,app):
        self.frame_botones = ct.CTkFrame(master=app, height=50, fg_color="transparent")
        self.frame_botones.grid(row=3, column=0, columnspan=2, pady=(4,4), padx=(10,10))

        font_title = ct.CTkFont(family='Consolas', weight='bold', size=24)

        self.BotonEnviarTexto=ct.CTkButton(self.frame_botones, text=">>>", width=80, command = self.BotonEnviar)
        self.BotonEnviarTexto.grid(row=0, column=0, sticky="ew", padx = 25)
        self.BotonEnviarTexto.configure(font=font_title, fg_color='steelblue', text_color= 'white', corner_radius= 8)  

        self.BotonNuevoJuego = ct.CTkButton(self.frame_botones, text="NUEVO JUEGO", width=250, command=self.JuegoNuevo)
        self.BotonNuevoJuego.grid(row=0, column=1, sticky="ew", padx = 120)
        self.BotonNuevoJuego.configure(font=font_title, fg_color='steelblue', text_color= 'white', corner_radius= 8)

        self.BotonSalir=ct.CTkButton(self.frame_botones, text="SALIR", width=120, command =lambda: self.cerrar_ventana(app))
        self.BotonSalir.grid(row=0, column=2, sticky="ew", padx = 25)
        self.BotonSalir.configure(font=font_title, fg_color='steelblue', text_color= 'white', corner_radius= 8)
        
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

    def cerrar_ventana(self, app):
        self.desvincular_eventos(app)
        app.destroy()
        if self.callback:
            self.callback()

    def desvincular_eventos(self, app):
        app.unbind("<Return>")
        app.unbind("<Control_R>")
        app.unbind("<Control_L>")
        app.unbind("<Escape>")
        app.unbind("<Key>")


if __name__ == "__main__":
    prueba = Juego_senias(callback=None)
    prueba.ejecutar()
        