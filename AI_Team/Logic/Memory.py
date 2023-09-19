from .VectorDB import VectorDB
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import google.generativeai as palm
# Query:
def consulta_IA_openai(pregunta):
    # Absolute path to the .txt file
    ruta_absoluta = ".memory_text\memoryAI.txt"

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


def consulta_IA_google(pregunta):
    # Absolute path to the .txt file
    ruta_absoluta = ".memory_text\memoryAI.txt"

    # Data preparation:
    with open(ruta_absoluta, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Instantiate the VectorDB class and process the content
    store_name = "memoryAI_store"  # Define a name for the vector store
    vector_db = VectorDB()
    vector_db.process_text(contenido, store_name)
    context = vector_db.query(pregunta)

    # Create a palm.Model object
    model = palm.Model()

    # Generate text using the palm.Model object, while also providing the context
    prompt = "What is AITeam?"
    response = model.generate_text(prompt, context=context)

    return response

# Use the query function:
#respuesta = consulta_IA_google("What is AITeam")
#print(respuesta)