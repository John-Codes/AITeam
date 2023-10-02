from .VectorDB import VectorDB
from .LLMs import CallPalm
from .context_messages import CONTEXT_MESSAGES
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import google.generativeai as palm
from pathlib import Path
import os
# Query:
def consulta_IA_openai(pregunta):
    # Absolute path to the .txt file
    current_dir = Path(__file__).parent
    ruta_absoluta = current_dir / "memory_text" / "memoryAI.txt"

    # Data preparation:
    with open(ruta_absoluta, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Instantiate the VectorDB class and process the content
    store_name = "memoryAI_store"  # Define a name for the vector store

    vector_db = VectorDB()

    vector_db.process_text(contenido, store_name)
    # Retrieve the most similar text fragments using the VectorDB class.
    docs = vector_db.query(pregunta)

    if not docs:
        return "Lo siento, no tengo información al respecto."

    # Set up the OpenAI model and get a response based on the retrieved documents and the question.
    llm = OpenAI()
    chain = load_qa_chain(llm=llm, chain_type="stuff")
    with get_openai_callback() as cb:
        response = chain.run(input_documents=docs, question=pregunta)
        # You can also print the callback if needed
        #print(cb)
    
    return response

# Global variable for the VectorDB instance
vector_db = None

def initialize_vector_db(context):
    global vector_db

    # Utilizar la función context_palm para obtener el contenido del archivo txt 
    # según el contexto proporcionado.
    vector_db_instance = VectorDB()
    contenido = vector_db_instance.context_palm(context)

    # Definir el nombre del vector store basado en el contexto
    store_name = f"memory-AI-with-{context}-store"
    
    # Instanciar la clase VectorDB y procesar el contenido
    vector_db = VectorDB()
    vector_db.process_text(contenido, store_name)

def Consulta_IA_PALM(prompt, context):
    global vector_db

    if vector_db is None:
        initialize_vector_db(context)

    message_error ='An error has occurred, please reload the page to connect to AI Team'
    
    # Retrieve the most similar text fragments using the VectorDB class.
    try:
        contenido = vector_db.context_palm(context)
    except FileNotFoundError:
        return message_error

    conversation = vector_db.get_conversation(context)
    
    examples = CONTEXT_MESSAGES.get(context, [])
    
    if conversation:
        examples.extend(conversation)

    try:
        palm_response = CallPalm(prompt, contenido, examples)
        print('this is response',palm_response)
    except Exception as e:
        palm_response = message_error
        print('response of google palm doesnt work', e)

    if palm_response != message_error:
        vector_db.add_to_context(prompt, palm_response)

    return palm_response
