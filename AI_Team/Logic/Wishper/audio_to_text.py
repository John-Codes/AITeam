from faster_whisper import WhisperModel
import os
import torch
import gc
model = WhisperModel("large-v1", device="cuda", compute_type="float16")

def audio_to_text(audio_path, lenguage):
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

    delete_audio_file(audio_path)

    return texto_transcrito

def delete_audio_file(audio_path):
    if os.path.exists(audio_path):
        os.remove(audio_path)

