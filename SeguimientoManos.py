import math
import cv2
import mediapipe as mp
import os
import time

#----------------------------- Creamos una clase---------------------------

class detectormanos():
    #----------------------------- Prametros de la deteccion---------------------------

    def __init__(self, mode=False, maxManos = 2, model_complexity = 0, Confdeteccion = 0.5, Confsegui=0.5):
        self.mode = mode    #Creamos el objeto y el tendra su propia variable y para todos lo mismo
        self.maxManos = maxManos
        self.compl = model_complexity
        self.confdeteccion = Confdeteccion
        self.Confsegui = Confsegui

    #----------------------------- Creamos los objetos que detectaran las manos y los crearan ----------------------------

        self.mpmanos = mp.solutions.hands
        self.manos = self.mpmanos.Hands(self.mode, self.maxManos, self.compl, self.confdeteccion, self.Confsegui)
        self.dibujo = mp.solutions.drawing_utils
        self.tip = [4, 8, 12, 16, 20]

    #----------------------------- Funcion para encontrar las manos ----------------------------
    def encontrarmanos(self, frame, dibujar = True):
        imgcolor = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.resultados = self.manos.process(imgcolor)

        if self.resultados.multi_hand_landmarks:
            for mano in self.resultados.multi_hand_landmarks:
                if dibujar:
                    self.dibujo.draw_landmarks(frame, mano,self.mpmanos.HAND_CONNECTIONS) #Dibujamos las conexiones de los puntos
        return frame

    #----------------------------- Funcion para encontrar la posicion ----------------------------
    def encontrarposicion(self,frame, ManoNum=0, dibujarPuntos = True, dibujarBox = True, color = []) :
        xlista = []
        ylista = []
        bbox = []
        player = 0
        
        self.lista= []

        if self.resultados.multi_hand_landmarks:
            miMano = self.resultados.multi_hand_landmarks[ManoNum]
            prueba = self.resultados.multi_hand_landmarks
            player = len(prueba)
            #print(player)
            for id, lm in enumerate(miMano.landmark):
                alto, ancho, c = frame.shape # Extraemos las dimenciones de los fps 
                cx, cy = int(lm.x * ancho), int(lm.y * alto) # Convertimoos la informacion a pixeles
                xlista.append(cx)
                ylista.append(cy)
                self.lista.append([id, cx, cy])
                if dibujarPuntos:
                    cv2.circle(frame, (cx, cy), 3, (0,0,0), cv2.FILLED ) #dibujamos un circulo
            xmin, xmax = min(xlista), max(xlista)
            ymin, ymax = min(ylista), max(ylista)
            bbox = xmin, ymin, xmax, ymax
            if dibujarBox:
                #dibujamos cuadro
                cv2.rectangle(frame, (xmin - 20, ymin - 20), (xmax+20, ymax + 20), color, 2)
        return self.lista, bbox, player

    
    #-----------------------------Funcion para detectar y dibujar los dedos de arriba ----------------------------
    def dedosarriba(self):
        dedos = []
        if self.lista[self.tip[0]][1] > self.lista[self.tip[0]-1][1]:
            dedos.append(1)
        else:
            dedos.append(0)
        
        for id in range (1,5):
            if self.lista[self.tip[id]][2] < self.lista[self.tip[id]-2][2]:
                dedos.append(1)
            else:
                dedos.append(0)

        return dedos

    #----------------------------- Funcion para detectar la distancia entre dos puntos ----------------------------

    def distancia(self, p1, p2, frame, dibujar = True, r = 15, t = 3):
        x1, y1 = self.lista[p1][1:]
        x2, y2 = self.lista[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if dibujar:
            cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), t)
            cv2.circle(frame, (x1, y1), r, (0, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x2, y2), r, (0, 0, 255), cv2.FILLED)
            cv2.circle(frame, (cx, cy), r, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)

        return length, frame, [x1, y1, x2, y2, cx, cy]

#----------------------------- Funcion principal ----------------------------

def main():
    ptiempo = 0
    ctiempo = 0

    #----------------------------- Leemos la camara web  ----------------------------
    cap = cv2.VideoCapture(0)
    #----------------------------- Creamos el objeto ----------------------------
    detector = detectormanos()
    #----------------------------- Realizamos la deteccion de manos ----------------------------
    while True:
        ret, frame = cap.read()
        #Unsa vez que obtengamos la imagen la enviaremos
        frame = detector.encontrarmanos(frame)
        lista, bbox = detector.encontrarmanos(frame)
        #if len (lista) != 0; 
            #print(Lista[4])
        #....................................Mostramos los fps.....................................
        ctiempo = time.time()
        fps = 1 / (ctiempo - ptiempo)
        ptiempo = ctiempo

        cv2.putText(frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAON, 3, (225, 0,255), 3)

        cv2.imshow("Manos", frame)
        k = cv2.waitKey(1)

        if k == 27:
            break
    cap.release()
    cv2.destroyAllWindows()