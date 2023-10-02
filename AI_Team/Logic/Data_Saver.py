import json
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

    def read_from_json(self, filename, key=None):
        # Lee datos de un archivo JSON. Si se proporciona una key, devuelve solo el valor de esa key.

        file_path = self.base_path / f"{filename}.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"No JSON file found with the name '{filename}'")

        with file_path.open('r', encoding='utf-8') as file:
            data = json.load(file)
        
        if key:
            return data.get(key)

        return data

    def json_to_dict(self, filename):
        # Convierte un archivo JSON a un diccionario de Python
        return self.read_from_json(filename)
