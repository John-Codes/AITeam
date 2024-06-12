import pyttsx3
from whisperspeech.pipeline import Pipeline
from django.conf import settings
import os

print(settings.MEDIA_ROOT)
# mete todo esto en una función con parametro como text
def text_to_audio_es(text):
# Inicializar el motor de pyttsx3
    engine = pyttsx3.init()

    # Configurar propiedades del motor si es necesario
    engine.setProperty('rate', 150)  # Velocidad del habla
    engine.setProperty('volume', 1)  # Volumen (0.0 a 1.0)

    # Obtener y configurar voces
    voices = engine.getProperty('voices')

    # Buscar la voz con el ID 'spanish-latin-am'
    selected_voice = None
    for voice in voices:
        if voice.id == 'spanish-latin-am':
            selected_voice = voice
            break

    # Configurar la voz seleccionada
    if selected_voice:
        engine.setProperty('voice', selected_voice.id)
    else:
        print("La voz 'spanish-latin-am' no se encontró.")

    # Obtener la ruta del directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construir la ruta completa del archivo de salida
    output_file = os.path.join(current_dir, 'output_audio.mp3')
    engine.say(text, "niños")
    # Convertir text a voz y guardar en un archivo
    engine.save_to_file(text, output_file)
    engine.runAndWait()

    return output_file

def text_to_audio_en(text):
    # Crear una instancia del modelo de voz
    
    pipe = Pipeline(s2a_ref='collabora/whisperspeech:s2a-q4-tiny-en+pl.model')
    # Generar la señal de audio a partir del texto
    pipe.generate_to_file('output.mp3', text)
    

def clear_text_input(text):
    # Eliminar caracteres especiales y espacios en blanco
    clean_text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
    return clean_text