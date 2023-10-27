from Server_Config.Server_Side.models import Client, ClienContext
from langchain.document_loaders import PyPDFLoader
from .Data_Saver import DataSaver
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
    def save_image_product(self, user_id, image):
        print('guardamos imagen')
        get_products = DataSaver()
        extract_products = get_products.read_from_json(f'memory-AI-with-{user_id}', ['products'])
        print('extraemos productos')
        products = dict(extract_products)
        name_file =str(image).split('.')[0]
        # revisa con un for que la imagen sea la misma que el nombre del producto, en este caso debe solo comprobar la llave name del diccionario
        for product in products['products']:
            print(f"Comparando: {product['name']} con {name_file}")

            if product['name'] == name_file:
                
                # Get the base directory of the project
                BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                media_folder = os.path.join(BASE_DIR, "Client_Side", "media_products")
                image_name = f"{user_id}-{product['name']}.png"
                image_path = os.path.join(media_folder, image_name)
                # If an image with the same name already exists, overwrite it
                # If not, save the new image directly
                try:
                    if os.path.exists(image_path):
                        os.remove(image_path)
                    # Save the image in the media folder using chunks
                    with open(os.path.join(media_folder, image_name), 'wb+') as destination:
                        for chunk in image.chunks():
                            destination.write(chunk)
                except Exception as e:
                    print('Error al guardar la imagen:', e)
                print('Imagen guardada para el cliente:', user_id)
                