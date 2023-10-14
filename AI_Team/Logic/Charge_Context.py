from Server_Config.Server_Side.models import Client, ClienContext
from langchain.document_loaders import PyPDFLoader
import tempfile
import os
class Charge_Context:
    def extract_text(self, uploaded_file):
        # Detectar el tipo de archivo basado en su extensión
        if uploaded_file.name.endswith('.txt'):
            text = uploaded_file.read().decode()
            return text
        elif uploaded_file.name.endswith('.pdf'):
            print(uploaded_file)
            # Guardar el contenido del archivo en un archivo temporal
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name
            
            # Cargar el PDF utilizando PyPDFLoader
            loader = PyPDFLoader(temp_file_path)
            documentos = loader.load()
            
            # Extraer el contenido de cada página del PDF
            contenido = ""
            for documento in documentos:
                contenido += documento.page_content
            
            # Eliminar el archivo temporal
            os.remove(temp_file_path)
            
            return contenido
        else:
            raise ValueError("File type not supported")
    
    def save_context(self, user_id, text):
        print('guardamos texto')
        client = Client.objects.get(pk=user_id)
        
        # Intenta obtener el contexto existente del cliente
        try:
            user_context = ClienContext.objects.get(client=client)
            user_context.context = text
            user_context.save()
            print('Contexto actualizado para el cliente:', user_id)
        except ClienContext.DoesNotExist:
            # Si el cliente no tiene un contexto, crea uno nuevo
            user_context = ClienContext(client=client, context=text)
            user_context.save()
            print('Nuevo contexto guardado para el cliente:', user_id)

