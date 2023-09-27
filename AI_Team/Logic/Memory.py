from .VectorDB import VectorDB
from .LLMs import CallPalm, CallPalm2
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

def initialize_vector_db():
    global vector_db

    current_dir = Path(__file__).parent
    ruta_absoluta = current_dir / "memory_text" / "memoryAI.txt"

    # Data preparation:
    with open(ruta_absoluta, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Instantiate the VectorDB class and process the content
    store_name = "memoryAI_store"  # Define a name for the vector store
    vector_db = VectorDB()
    vector_db.process_text(contenido, store_name)

def Consulta_IA_PALM(prompt):

    global vector_db

    # If the vector_db is not initialized, initialize it
    if vector_db is None:
        initialize_vector_db()

    # Retrieve the most similar text fragments using the VectorDB class.
    contenido = vector_db.context_palm()
    #docs = vector_db.query(prompt)
    examples = [("Whats Ai_Team","AITeam is an artificial intelligence assistant for programmers and code developers.")]
    conversation = vector_db.get_conversation()
    if conversation:
        print('conversation',conversation)
        examples.extend(conversation)
    # Generate a response using google.generativeai
    try:
        palm_response = CallPalm(prompt, contenido, examples)
        print('palm response',palm_response)
    except Exception as e:
        palm_response = 'an error has ocurred, please reload the page for connect to AI Team'
        print('response of google palm dont work', e)

    if palm_response != 'an error has ocurred, please reload the page for connect to AI Team':
        # Add the prompt and the IA response to the vector
        vector_db.add_to_context(prompt, palm_response)

    return palm_response