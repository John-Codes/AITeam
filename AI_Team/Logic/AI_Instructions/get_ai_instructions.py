import os

def get_instructions(instructions_file):
    try:
        # Ruta base predefinida
        base_path = "AITeam/AI_Team/Logic/memory_text"
        file_name = f"memory-AI-with-{instructions_file}"
        # Construir la ruta completa al archivo de instrucciones
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', base_path, file_name))

        # Verificar si el archivo existe
        if not os.path.exists(file_path):
            return "El archivo no existe."

        return file_path
    except Exception as e:
        print("Error in get_instructions", str(e))