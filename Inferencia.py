#Importamos librerias
import cv2
import os
# Importamos la clase SeguimientoManos
import SeguimientoManos as sm
from ultralytics import YOLO
import torch

# Lectura de la camara
cap = cv2.VideoCapture(0)

#Cambiar la resoluciion
cap.set(3, 1120)
cap.set(4, 720)

# Leer el modelo asegurando que use la CPU
device = 'cuda' if torch.cuda.is_available() and torch.cuda.get_device_capability(0)[0] >= 3.7 else 'cpu'
print(f"Usando dispositivo: {device}")

model = YOLO('best2.pt').to(device)

# Leer nuestro modelo
#model = YOLO('best.pt')

# Declarar detector
detector = sm.detectormanos(Confdeteccion = 0.6)

while True:
    # Realizar la lectura de la cap
    ret, frame = cap.read()
    
    # Extraer informacion de las manos
    frame = detector.encontrarmanos(frame, dibujar = False)

    #Posicion de una sola mano 
    lista1, bbox, mano = detector.encontrarposicion(frame, ManoNum = 0, dibujarPuntos = False, dibujarBox = False, color = [0, 255, 0] )

    # Si hay mano

    if mano == 1:
        # Extraemos la informacion del recuadro
        xmin, ymin, xmax, ymax = bbox
        xmin = xmin - 40
        ymin = ymin - 40
        xmax = xmax + 40
        ymax = ymax + 40

        # Realizar recorte de nuestra mano
        recorte = frame[ymin:ymax, xmin:xmax] 

        # Redimencionamiento
        recorte = cv2.resize(recorte, (640,640), interpolation = cv2.INTER_CUBIC)

        # Dentro del bucle, realiza la predicción usando el dispositivo
        resultados = model.predict(recorte, conf=0.55, device=device)

        # Extraemos resultados
        #resultados = model.predict(recorte, conf = 0.55)
        
        # Si hay rersultados
        if len(resultados) != 0:
            # Iteramos : por cada resultado
            for results in resultados:
                masks = results.masks
                coordenadas = masks

                anotaciones = resultados[0].plot()

        cv2.imshow("RECORTE", anotaciones)
       #cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), [0, 255, 0], 2)
       #yolo task=segment mode=train epochs=30 data=dataset.yaml model=yolov8n.pt imgsz=640 batch=2 device=cpu

    # Mostrar FPS
    cv2.imshow("LENGUAJE VOCALES", frame)

    #Leer nuestro teclado
    t = cv2.waitKey(1)
    if t == 27:
        break

cap.release()
cv2.destroyAllWindows()