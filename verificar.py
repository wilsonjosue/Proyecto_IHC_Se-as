import os
ruta_img = 'C:/Users/danie/OneDrive/Documentos/PhytonProjects/ProyectoIHCMejora/LenguajeVocales/dataset/val/images'
ruta_labels = 'C:/Users/danie/OneDrive/Documentos/PhytonProjects/ProyectoIHCMejora/LenguajeVocales/dataset/val/labels'

def verificar_annotaciones(ruta_img, ruta_labels):
    imgs = set(os.listdir(ruta_img))
    labels = set(os.listdir(ruta_labels))

    sin_etiqueta = imgs - {f.replace('.txt', '.jpg') for f in labels}
    if sin_etiqueta:
        print("Imágenes sin etiqueta:", sin_etiqueta)
    else:
        print("Todas las imágenes tienen etiquetas correspondientes.")

verificar_annotaciones("dataset/train/images", "dataset/train/labels")
verificar_annotaciones("dataset/val/images", "dataset/val/labels")