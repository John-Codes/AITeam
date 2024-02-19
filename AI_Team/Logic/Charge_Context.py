from Server_Config.Server_Side.models import Client, ClienContext
#from langchain.document_loaders import PyPDFLoader
from .Data_Saver import DataSaver
from .sender_mails import image_seve_fail_email
from .response_utils import *
from .Memory import Consulta_IA_JSON
import tempfile
import os
from hashids import Hashids
from django.utils.translation import gettext as _

hashids = Hashids(salt = os.getenv("salt"), min_length=8)
"""sumary_line

Keyword arguments:
argument -- description
Return: return_description
"""

class Charge_Context:
    def extract_text(self, user, uploaded_file):
        file_size = uploaded_file.size
        # Detectar el tipo de archivo basado en su extensión
        if uploaded_file.name.endswith('.txt'):
            contenido = uploaded_file.read().decode()

        elif uploaded_file.name.endswith('.pdf'):
            # Cargar el archivo PDF con PyPDFLoader
            # Guardar el contenido del archivo en un archivo temporal
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name
            
            # Cargar el PDF utilizando PyPDFLoader
            # loader = PyPDFLoader(temp_file_path)
            # documentos = loader.load()
            
            # Extraer el contenido de cada página del PDF
            contenido = ""
            # for documento in documentos:
            #     contenido += documento.page_content
            
            # Eliminar el archivo temporal
            os.remove(temp_file_path)
            print('PDF extracted')
        context =self.save_context(user, contenido, file_size)
        return context
    
    def save_context(self, user_id, text, file_size):
        context_details = {
            'status': 'failed',
            'message': ''
        }

        try:

            client = Client.objects.get(pk=user_id)
            
            # Intenta obtener el contexto existente del cliente
            user_context, created = ClienContext.objects.get_or_create(client=client)
            existing_context_size = len(user_context.context.encode('utf-8'))
            # Comprobar si el tamaño total excede los 100 MB
            total_size = existing_context_size + file_size
            if total_size > 100 * 1024 * 1024:  # 100 MB en bytes
                context_details['status'] = _('Total size including existing data exceeds the 100 MB limit')
                return context_details
            if user_context.context != text and not user_context.context in text:
                user_context.context += f"\n{text}"
            else:
                user_context.context = text

            user_context.save()
            
            # Actualiza el diccionario de detalles con el éxito
            context_details['status'] = 'saved'
        
            if created:
                context_details['status'] = _('New context created successfully.')
            else:
                context_details['status'] = _('context updated successfully.')
                # extract contiene el str de texto los primeros y ultimos 50 caracteres
            context_details['extract'] = f"{user_context.context[:200]}...{user_context.context[-200:]}" if len(user_context.context) > 450 else user_context.context
            
            context_user = hashids.encode(user_id)
            print("Llamamos a la IA")
            json_read, data_page = Consulta_IA_JSON(context_user)
            context_details['keywords'] = json_read
            if json_read:
                print(json_read)
                # Llamar a create_page de DataSaver
                data_saver = DataSaver()
                data_saver.create_page(user_id, json_read)
                context_details['status'] += _(' and site generated successfully.')
        except Client.DoesNotExist:
            context_details['status'] = _('Login required')
        except Exception as e:
            context_details['status'] = _(f'Error saving context, an email has send to support: {str(e)}')
            image_seve_fail_email(context_details)
        context_details['type'] = 'text'
        return context_details


    def save_image_product(self, user_id, image):
        #print('guardamos imagen')
        get_products = DataSaver()
        extract_products = get_products.read_from_json(f'memory-AI-with-{user_id}', ['products'])
        #print('extraemos productos')
        products = dict(extract_products)
        name_file = str(image).split('.')[0]
        product_names = [product['name'] for product in products['products']]  # Lista de nombres de productos

        # Inicializa image_details con un estado de 'no coincidente' por defecto
        image_details = {
            'image_name': name_file,
            'status': 'Name not matched',
            'matched_products': product_names  # Lista de nombres de productos del usuario
        }

        # Revisa con un for que la imagen sea la misma que el nombre del producto
        for product in products['products']:
            #print(f"Comparando: {product['name']} con {name_file}")

            if product['name'] == name_file:
                #configuración de rutas
                BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                media_folder = os.path.join(BASE_DIR, "Client_Side", "media_products")
                image_name = f"{user_id}-{product['name']}.png"
                image_path = os.path.join(media_folder, image_name)

                try:
                    if os.path.exists(image_path):
                        os.remove(image_path)

                    with open(image_path, 'wb+') as destination:
                        for chunk in image.chunks():
                            destination.write(chunk)
                    # Actualiza los detalles de la imagen con éxito
                    image_details = {
                        'name': image_name,
                        'status': _('Saved Successfully'),
                    }
                    #print('Imagen guardada para el cliente:', user_id)
                except Exception as e:
                    #print('Error al guardar la imagen:', e)
                    # Actualiza los detalles de la imagen con el estado de error
                    image_details = {
                        'name': image_name,
                        'status': ('Save Failed, an email has send to support'),
                        'error': str(e),
                    }
                    image_seve_fail_email(image_details, user_id)
                break  # Sale del bucle ya que la imagen ha sido guardada
            image_details['type'] = 'image'
        return image_details
    
    def process_uploaded_files(self, request):
        uploaded_files = request.FILES.getlist('uploaded_files')
        if not uploaded_files:
            return None

        upload_details = []
        for file in uploaded_files:
            if file.name.endswith('.png'):
                details = self.save_image_product(request.user.id, file)
            else:
                details = self.extract_text(request.user.id, file)
            upload_details.append(details)
        
        return upload_details
    
    def handle_user_input(self, request, user_message, uploaded_files_details):
        response_data = {}

        # Procesar mensaje del usuario
        if user_message:
            response_data['user_message_div'] = render_html('chat_messages/user_message.html', message=user_message)
        else:
            response_data['user_message_div'] = ''

        # Procesar archivos subidos
        if uploaded_files_details:
            for file_detail in uploaded_files_details:
                if file_detail['type'] == 'image':
                    image_html = render_html('chat_messages/image_message.html', file_detail)
                    response_data['user_message_div'] += image_html
                elif file_detail['type'] == 'text':
                    details = file_datail.get('keywords', False)
                    if details:
                        request.session['create-json-page'] = True
                    text_html = render_html('chat_messages/text_message.html', file_detail)
                    response_data['user_message_div'] += text_html

        return response_data
