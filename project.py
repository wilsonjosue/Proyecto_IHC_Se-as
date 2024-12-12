import time
from asistente import AsistenteVoz
from juego_AH import Juego_senias
from juego_LC import JuegoLetras
import customtkinter as ctk


class VirtualAssistant:
    def __init__(self):
        self.asistente_voz = AsistenteVoz()
        self.mi_juego2 = JuegoLetras(callback=self.presentar_opciones)
        self.mi_juego = Juego_senias(callback=self.presentar_opciones)
        self.option_label = None
        self.win_choose = None
        self.console = None  # Consola embebida para mensajes

    def texto_a_audio(self, comando):
        self.asistente_voz.texto_a_audio(comando)

    def capturar_voz(self):
        return self.asistente_voz.capturar_voz()

    def enviar_voz(self):
        return self.asistente_voz.enviar_voz()

    def imprimir_mensaje(self, mensaje):
        """Imprime un mensaje en la consola embebida y el terminal, y lo lee en voz alta."""
        if self.console:
            self.console.insert(ctk.END, f"{mensaje}\n")
            self.console.see(ctk.END)  # Auto-scroll hacia abajo
        print(mensaje)
        self.texto_a_audio(mensaje)  # Leer el mensaje en voz alta

    def do_learn(self):
        self.option_label.configure(text="Escogiste Aprendizaje")
        self.imprimir_mensaje("Iniciando aprendizaje...")
        self.win_choose.destroy()

    def do_game2(self):
        self.option_label.configure(text="Escogiste Juego Letras Caen")
        self.imprimir_mensaje("Iniciando Juego Letras Caen...")
        self.win_choose.destroy()

    def do_game(self):
        self.option_label.configure(text="Escogiste Juego Del Ahorcado")
        self.imprimir_mensaje("Iniciando Juego Del Ahorcado...")
        self.win_choose.destroy()

    def presentar_opciones(self):
        self.win_choose = ctk.CTk()
        self.win_choose.geometry("800x600")
        self.win_choose.title("Asistente Virtual - Selección de Juegos")

        # Encabezado
        title = ctk.CTkLabel(
            self.win_choose,
            text="Seleccione un modo de juego",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.pack(pady=20)

        # Consola para mensajes
        self.console = ctk.CTkTextbox(
            self.win_choose,
            width=700,
            height=200,
            font=("Arial", 12),
            wrap="word",
        )
        self.console.pack(pady=(10, 20))
        self.imprimir_mensaje("Bienvenido al Asistente Virtual.")
        self.imprimir_mensaje(
            "Opciones disponibles:\n"
            "1) Juego Reconoce Señas\n"
            "2) Juego Letras Caen\n"
            "3) Juego Del Ahorcado"
        )

        # Botones para opciones
        button_frame = ctk.CTkFrame(self.win_choose)
        button_frame.pack(pady=20)

        learn_button = ctk.CTkButton(
            button_frame,
            text="Juego Reconoce Señas",
            command=self.do_learn,
            width=200,
        )
        learn_button.grid(row=0, column=0, padx=10, pady=10)

        juego2_button = ctk.CTkButton(
            button_frame,
            text="Juego Letras Caen",
            command=self.do_game2,
            width=200,
        )
        juego2_button.grid(row=0, column=1, padx=10, pady=10)

        juego_button = ctk.CTkButton(
            button_frame,
            text="Juego Del Ahorcado",
            command=self.do_game,
            width=200,
        )
        juego_button.grid(row=0, column=2, padx=10, pady=10)

        # Etiqueta para mostrar selección
        self.option_label = ctk.CTkLabel(
            self.win_choose, text="", font=ctk.CTkFont(size=16)
        )
        self.option_label.pack(pady=10)

        self.win_choose.mainloop()

        if self.option_label.cget("text") == "Escogiste Aprendizaje":
            self.mi_aprendizaje.ejecutar()
        elif self.option_label.cget("text") == "Escogiste Juego Letras Caen":
            self.mi_juego2.ejecutar()
        elif self.option_label.cget("text") == "Escogiste Juego Del Ahorcado":
            self.mi_juego.ejecutar()

    def ejecutar_programa(self):
        self.presentar_opciones()


# Main para iniciar
if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # Modos: System (por defecto), Dark, Light
    ctk.set_default_color_theme("blue")  # Opciones: blue, dark-blue, green
    virtual_assistant = VirtualAssistant()
    virtual_assistant.ejecutar_programa()