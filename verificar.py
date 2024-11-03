import os
import cv2

# Directorio de las imágenes
directorio = r'C:/Users/danie/OneDrive/Documentos/PhytonProjects/ProyectoIHCMejora/FormatoYoloLZ/train'
nombre_base = 'Z'

# Listar y ordenar todos los archivos .jpg en el directorio
imagenes = sorted([f for f in os.listdir(directorio) if f.endswith('.jpg')])

# Renombrar las imágenes
for i, imagen_nombre in enumerate(imagenes):
    # Cargar la imagen con cv2
    imagen_path = os.path.join(directorio, imagen_nombre)
    imagen = cv2.imread(imagen_path)
    
    # Crear el nuevo nombre y guardar la imagen
    nuevo_nombre = f"{nombre_base}_{i}.jpg"
    nuevo_path = os.path.join(directorio, nuevo_nombre)
    cv2.imwrite(nuevo_path, imagen)
    
    # Eliminar el archivo con el nombre antiguo
    os.remove(imagen_path)

print("Renombrado completo.")