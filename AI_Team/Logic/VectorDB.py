import os
import pickle
from Server_Config.Server_Side.models import ClienContext
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import faiss
from pathlib import Path
# quitar el punto para usar Gradio.py
from .Data_Saver import DataSaver
import re

class VectorDB:
    def __init__(self):
        self.vector_store = None
        self.conversations = []

    def split_text_into_chunks(self, text):
        # split text of type str into chunks, parts of the text of type str
        text = text.replace("\n","")
        text = re.sub(r'\s+', ' ', text)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        return chunks

    def convert_text_to_embeddings(self, chunks):
        #convert text into embeddings, type int, texto to vectors
        embeddings = OpenAIEmbeddings()
        return FAISS.from_texts(chunks, embedding=embeddings)

    def save_vector_store(self, store_name, vector_store):
        with open(f"{store_name}.pkl", "wb") as f:
            pickle.dump(vector_store, f)

    def load_vector_store(self, store_name):
        #save the text into memory of pc in pkl format
        if os.path.exists(f"{store_name}.pkl"):
            with open(f"{store_name}.pkl", "rb") as f:
                self.vector_store = pickle.load(f)
        else:
            raise FileNotFoundError(f"File {store_name}.pkl not found!")

    def process_text(self, text, store_name):
        # split a large thext into smalls texts
        chunks = self.split_text_into_chunks(text)
        # if vector store was saved, loaded to the file
        if os.path.exists(f"{store_name}.pkl"):
            self.load_vector_store(store_name)
        # else save the vectorstore convert the text into vectors and seve in the memory
        else:
            self.vector_store = self.convert_text_to_embeddings(chunks)
            self.save_vector_store(store_name, self.vector_store)

    def query(self, query_text, k=3):
        try:
            if self.vector_store:
                # similarity search to a questios of user into the vectorsetor, this return text 
                vector = self.vector_store.similarity_search(query=query_text, k=k)
                return vector
            else:
                raise Exception("Vector store not loaded or created!")
        except Exception as e:
            print('we get a issue to realize a query:', e)
    
    def add_to_context(self, prompt, response):
        self.conversations.append((prompt, response))

    def get_conversation(self, context):

        return self.conversations
    
    def context_palm(self, context):
        print('empezamos a cargar el contenido')
        if context not in ["main", "subscription", "panel-admin"]:
            print('context not in valid contexts')
            try:
                # Intenta obtener el contexto del cliente por su ID
                client_context = ClienContext.objects.get(client__id=context)
                print('we found the context')
                return client_context.context
            except Exception as e:
                print(' we dont found vector becouse')
                print(e)

        current_dir = Path(__file__).parent
        ruta_absoluta = current_dir / "memory_text" / f"memory-AI-with-{context}.txt"

        if not ruta_absoluta.exists():
            raise FileNotFoundError(f"No file found for context '{context}'")

        with open(ruta_absoluta, 'r', encoding='utf-8') as f:
            contenido = f.read()

        return contenido
    def get_context_palm(self, prompt):
        consulta =self.query(prompt)
        consulta_str = str(consulta)
        # Usar regex para extraer el contenido del texto
        content_pattern = r'Document\(page_content=\'(.*?)\'\)'
        matches = re.findall(content_pattern, consulta_str)
        
        # Combina todas las coincidencias encontradas en una sola cadena de texto
        cleaned_text = ' '.join(matches)
        print('cleaned_text')
        print(cleaned_text)
        return cleaned_text
        