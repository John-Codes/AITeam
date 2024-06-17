# import lybrarias that handle models
from whisperspeech.pipeline import Pipeline
from faster_whisper import WhisperModel
import pyttsx3
# import libraries to clear cache to use the models
import torch
import gc
# import os to manage files
import os
#generate file name
import uuid
# global instance of the model for all functions
model = WhisperModel("large-v1", device="cuda", compute_type="float16")
pipe = Pipeline(s2a_ref='collabora/whisperspeech:s2a-q4-tiny-en+pl.model')


from django.conf import settings

class AudioTextConverter():
    def __init__(self):
        self.path_audio = settings.MEDIA_ROOT
        self.audio_responses_path = os.path.join(self.path_audio, 'audio_responses_generated')
        os.makedirs(self.audio_responses_path, exist_ok=True)

    def audio_to_text(self, audio_path, lenguage):
        global model
        # Transcribir el audio
        try:
            segments, info = model.transcribe(audio_path, lenguage, beam_size=5)
        except Exception as e:
            print('an error has ocurred', e)

        # Obtener el texto transcrito
        texto_transcrito = " ".join([segment.text for segment in segments])
        
        # Eliminar el modelo y liberar memoria
        gc.collect()
        torch.cuda.empty_cache()

        self.delete_audio_file(audio_path)

        return texto_transcrito

    def delete_audio_file(self, audio_path):
        if os.path.exists(audio_path):
            os.remove(audio_path)    



    def text_to_audio_es(self, text):
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

        # Construir la ruta completa del archivo de salida
        output_file = self.generate_file_name()
        engine.say(text, "niños")
        # Convertir text a voz y guardar en un archivo
        engine.save_to_file(text, output_file)
        engine.runAndWait()

        return output_file

    def text_to_audio_en(self, text):
        # Crear una instancia del modelo de voz
        clear_text = self.clear_text_input(text)
        global pipe
        # Construir la ruta completa del archivo de salida
        
        output_file = self.generate_file_name()

        # Generar la señal de audio a partir del texto
        pipe.generate_to_file(output_file, clear_text)

        return output_file
    #method that call the corresponding method depending of the lenguage 
    def text_to_audio(self, text, lenguage):
        if lenguage == 'es':
            return self.text_to_audio_es(text)
        elif lenguage == 'en':
            return self.text_to_audio_en(text)

    def generate_file_name(self):
        unique_filename = f"{uuid.uuid4()}.mp3"
        return os.path.join(self.audio_responses_path, unique_filename)
    
    def clear_text_input(self, text):
        # Eliminar caracteres especiales y espacios en blanco
        clean_text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        return clean_text