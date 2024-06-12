from faster_whisper import WhisperModel
import os
import torch

def audio_to_text(audio_path):
    torch.cuda.empty_cache()
    # Cargar el modelo de Whisper convertido
    model = WhisperModel("medium", device="cuda", compute_type="float16")

    # Transcribir el audio
    try:
        segments, info = model.transcribe(audio_path, 'es', beam_size=5)
    except Exception as e:
        print('an error has ocurred', e)

    # Obtener el texto transcrito
    texto_transcrito = " ".join([segment.text for segment in segments])
    
    return texto_transcrito

# Ejemplo de uso
current_dir = os.path.dirname(os.path.abspath(__file__))
