import json
import re
from pathlib import Path

class DataSaver:

    def __init__(self):
        # Definimos la ruta base para todos los archivos que manejaremos
        self.base_path = Path(__file__).parent / "memory_text"

    def save_to_json(self, data_dict, filename):
        # Guarda un diccionario en un archivo JSON

        file_path = self.base_path / f"{filename}.json"

        with file_path.open('w', encoding='utf-8') as file:
            json.dump(data_dict, file, ensure_ascii=False, indent=4)

    def read_from_json(self, filename, keys=False):
        # Lee datos de un archivo JSON. Si se proporciona una key, devuelve solo el valor de esa key.

        file_path = self.base_path / f"{filename}.json"
        
        if not file_path.exists():
            return False

        with file_path.open('r', encoding='utf-8') as file:
            data = json.load(file)
        if keys:
            data_selected = {}
            for key in keys:
                value = data.get(key)
                data_selected[key] = value
            return data_selected
        else:
            return  data

    def json_to_dict(self, filename):
        # Convierte un archivo JSON a un diccionario de Python
        return self.read_from_json(filename)
    
    def format_str_to_dict(self, json_str):
        # Primero, extraemos el contenido entre las llaves
        match = re.search(r'{.*}', json_str, re.DOTALL)
        if not match:
            print('no match a dict')

        # Luego, convertimos el string limpio a un diccionario
        try:
            clean_json_str = match.group(0)
            data_dict = json.loads(clean_json_str)
            print('json generated')
            return data_dict
        except Exception as e:
            print('not json generated')
            print(e)

    def file_exists(self, filename):
        """Check if a specific file exists."""
        file_path = self.base_path / f"{filename}.json"
        return file_path.exists()
