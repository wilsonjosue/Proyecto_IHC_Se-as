import time
from asistente import AsistenteVoz
from juego_AH import Juego_senias
from juego_LC import JuegoLetras
#from juego_CS import 
import customtkinter as ctk

class VirtualAssistant:
    def __init__(self):
        self.asistente_voz = AsistenteVoz()
        #self.mi_aprendizaje = Juego_(callback=self.presentar_opciones)
        self.mi_juego2 = JuegoLetras(callback=self.presentar_opciones)
        self.mi_juego = Juego_senias(callback=self.presentar_opciones)
        self.option_label = None
        self.win_choose = None
        
    def texto_a_audio(self, comando):
        self.asistente_voz.texto_a_audio(comando)

    def capturar_voz(self):
        return self.asistente_voz.capturar_voz()

    def enviar_voz(self):
        return self.asistente_voz.enviar_voz()

    def do_learn(self):
        self.option_label.configure(text="Escogiste Aprendizaje")
        self.win_choose.destroy()

    def do_game2(self):
        self.option_label.configure(text="Escogiste Juego Letras Caen")
        self.win_choose.destroy()

    def do_game(self):
        self.option_label.configure(text="Escogiste Juego Del Ahorcado")
        self.win_choose.destroy()
    
    # Se ejecuta Principal comunica con __init__(self)
    def presentar_opciones(self):

        self.win_choose = ctk.CTk()
        self.win_choose.geometry("600x75")

        text = (
            "\n 1) Aprendizaje"
            "\n 2) Juego-Letras-Caen"
            "\n 3) Juego-Del-Ahorcado"
        )
        print(text)

        text = "¿Qué opción eliges?"
        print(text)
        self.texto_a_audio(text)
        time.sleep(0.5)
        self.texto_a_audio("¿Aprendizaje? ¿Juego Letras Caen? ¿Juego Del Ahorcado?")
        print("dime")
        self.texto_a_audio("dime")

        title = ctk.CTkLabel(self.win_choose, text = "Escoja su modo")
        title.pack(side=ctk.LEFT, padx=(20, 20))
    
        learn = ctk.CTkButton(self.win_choose, text = 'Aprendizaje', command=self.do_learn)
        learn.pack(side=ctk.LEFT, padx=(5, 5))
    
        juego2 = ctk.CTkButton(self.win_choose, text = 'Juego-Letras-Caen', command=self.do_game2)
        juego2.pack(side=ctk.LEFT, padx=(5, 5))
    
        juego = ctk.CTkButton(self.win_choose, text = 'Juego-Del-Ahorcado', command=self.do_game)
        juego.pack(side=ctk.LEFT, padx=(5, 5))

        self.option_label = ctk.CTkLabel(self.win_choose, text = "")
        self.option_label.pack(side=ctk.LEFT, padx=(5, 5))
        
        self.win_choose.mainloop()

        if (self.option_label.cget("text") == "Escogiste Aprendizaje"):
            self.mi_aprendizaje.ejecutar()      
        elif (self.option_label.cget("text") == "Escogiste Juego Letras Caen"):
            self.mi_juego2.ejecutar()      
        elif (self.option_label.cget("text") == "Escogiste Juego Del Ahorcado"):
            self.mi_juego.ejecutar()

    def ejecutar_programa(self):
        self.presentar_opciones()
       
# Usage
if __name__ == "__main__":
    virtual_assistant = VirtualAssistant()
    virtual_assistant.ejecutar_programa()
