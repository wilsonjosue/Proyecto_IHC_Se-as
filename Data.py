#Importamos librerias
import cv2
import os
# Importamos la clase SeguimientoManos
import SeguimientoManos as sm
#Creacion de la carpeta
nombre = 'B'

direccion = 'C:/Users/danie/OneDrive/Documentos/PhytonProjects/ProyectoIHCMejora/LenguajeVocales/data'
carpeta = direccion + '/'+ nombre

#Contador
cont = 0

# Si no esta creada la carpeta
if not os.path.exists(carpeta):
    print("CARPETA CREADA: ", carpeta )
    os.makedirs(carpeta)

# Lectura de la camara
cap = cv2.VideoCapture(0)

# Cambiar la resoluciion
cap.set(3, 1120)
cap.set(4, 720)

# Declarar detector
detector = sm.detectormanos(Confdeteccion = 0.9)

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
        # recorte = cv2.resize(recorte, (640,640), interpolation = cv2.INTER_CUBIC)

        #Almacenar nuestras imagenes que serviran para el etiquetado/entrenamiento
        cv2.imwrite(carpeta + "/B_{}.jpg".format(cont), recorte)
        
        #aumentar contador
        cont = cont +1

        cv2.imshow("RECORTE", recorte)

        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), [0, 255, 0], 2)
 
    # Mostrar FPS
    cv2.imshow("LENGUAJE VOCALES", frame)

    #Leer nuestro teclado
    t = cv2.waitKey(1)
    if t == 27 or cont == 40:
        break

cap.release()
cv2.destroyAllWindows()