import os
from pathlib import Path
# quitar el punto para usar Gradio.py
from .VectorDB import VectorDB
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
        contenido = vector_db.context_palm(context)
        if contenido:
            vector_db.process_text(contenido, store_name)
            docs_palm = vector_db.get_context_palm(prompt)
    except FileNotFoundError:
        return message_error

    conversation = vector_db.get_conversation()
    
    examples = CONTEXT_MESSAGES.get(context, [])
    if conversation:
        # only the last 20 messages will be passed to the AI because it has a limit of 20000 bytes that cannot be exceeded
        examples.extend(conversation[-7:])

    try:
        palm_response = CallPalm(prompt, docs_palm, examples)
    except Exception as e:
        palm_response = message_error

    if palm_response != message_error:
        vector_db.add_to_context(prompt, palm_response)
    
    return palm_response