import os
from pathlib import Path
# quitar el punto para usar Gradio.py
from .VectorDB import VectorDB
from .Data_Saver import DataSaver
from .LLMs import *
from .context_messages import CONTEXT_MESSAGES
# Query:
def consulta_IA_openai(pregunta, context):
    #this work with django
    # Absolute path to the .txt file
    #current_dir = Path(__file__).parent
    #ruta_absoluta = current_dir / "memory_text" / str(context)

    # Data preparation:
    with open(context, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Instantiate the VectorDB class and process the content
    store_name = "memoryAI_store"  # Define a name for the vector store

    vector_db = VectorDB()

    vector_db.process_text(contenido, store_name)
    # Retrieve the most similar text fragments using the VectorDB class.
    docs = vector_db.query(pregunta)

    if not docs:
        return "Lo siento, no tengo información al respecto."

    # Call a gpt with openai, if this dont work, the function call the CallChatGPT function LLMs
    response = CallChatGPT_Langchain(pregunta, docs, context)

    return response

vector_db = None

class ContextManager:
    def __init__(self):
        self.last_context = None

context_manager = ContextManager()

def Consulta_IA_PALM(prompt, context):
    global vector_db
    
    last_context = context_manager.last_context

    if vector_db is None:
        vector_db = VectorDB()    

    # Restart the Vector Store class if switch chats (context)
    if context != last_context:
        vector_db = VectorDB()
        context_manager.last_context = context

    
    message_error ='An error has occurred, please reload the page to connect to AI Team'
    
    # Retrieve the most similar text fragments using the VectorDB class.
    try:
        store_name = f"memoryAI_store-{context}"
        contenido, products= vector_db.context_palm(context)
        if contenido:
            vector_db.process_text(contenido, store_name)
            docs_palm = vector_db.get_context_palm(prompt)
    except FileNotFoundError:
        return message_error

    conversation = vector_db.get_conversation()
    
    examples = CONTEXT_MESSAGES.get(context, [])
    if conversation:
        # only the last 5 messages will be passed to the AI because it has a limit of 20000 bytes that cant be exceeded
        examples.extend(conversation[-5:])
    product_info = False
    try:
        # product_info = False if the user dont ask for a product, or have the data of the product
        # this execute if the prompt if from a user chat
        if context not in ["main","subscription","panel-admin"]:
            try:
                # this has to return a dict {name: product}
                ask_for_product = CallPalm2(prompt, products)
                print('ask_for_product',ask_for_product)
                # format the response
                get_name = DataSaver()
                get_name_product = get_name.format_str_to_dict(str(ask_for_product))
                # get the name of the product to verirfy if this is a product of the user json
                get_name_product= dict(get_name_product)
                product_to_check = get_name_product.get('name', None)
                product_info = products.get(product_to_check, False)
                # add the img url of the product
                if product_info:
                    product_info['img'] = f"{context}-{product_to_check}"
            except:
                product_info = False
            docs_palm = f"""You offer the following products, if the user asks about any you must give them a brief message of the information:
            \n{str(products)}\n Here's the information you should base your answer on:\n{docs_palm}"""
        #ia_response = CallPalm(prompt, docs_palm, examples)
        ia_response = runpod_calling(prompt, docs_palm, examples)
        print('runpod',ia_response)
    except Exception as e:
        print(e)
        ia_response = message_error

    if ia_response != message_error:
        vector_db.add_to_context(prompt, ia_response)
    return ia_response, product_info

def Consulta_IA_JSON(context):
    prompt = f"""I want to create a json that contains the essential information of a website, the keys of the json are 
    title, header, description, keywords, default message, list items, products, links, text, texto, titulo, encabezado, enlaces, mensaje, productos, imagenes
    the content of the json must include the meta tags keywords, description, the tag title of the page, and the header is h1 tag of the page.
    in the navigation links Each tag includes a text that the user can read and a url to which he will be redirected when clicking.
    Finally, it detects the products sent by the user, each product is an item of the list and each product has the following dictionary keys:  product name, description, value, link to buy"""
    vector_db = VectorDB()    

    message_error ='An error has occurred, please submit again the files'
    
    # Retrieve the most similar text fragments using the VectorDB class.
    try:
        store_name = f"memoryAI_store-{context}"
        contenido, products= vector_db.context_palm(context)
        if contenido:
            vector_db.process_text(contenido, store_name)
            docs_palm = vector_db.get_context_palm(prompt)
            vector_db.delete_vector_store(store_name)
    except FileNotFoundError:
        return message_error
    try:            
        # Verificación de palabras clave
        keys = ['title', 'header', 'description', 'keywords', 'default message', 'list items', 'products', 'links', 'text', 'texto', 'titulo', 'encabezado', 'enlaces', 'mensaje', 'productos', 'imagenes']
        num_keys = 0
        text_lower = docs_palm.lower()  # Convierte el texto a minúsculas

        for key in keys:
            if f"{key} " in text_lower:
                print(key)
                num_keys += 1
        keys = True if num_keys > 3 else False
        json_response = ""
        if keys:
            json_response, toeknizer = generate_json(docs_palm)
    except Exception as e:
        print(e)
        json_response = message_error

    return json_response, keys