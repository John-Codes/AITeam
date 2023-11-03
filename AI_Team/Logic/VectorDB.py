import os
import pickle
from Server_Config.Server_Side.models import ClienContext
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import faiss
from pathlib import Path
from hashids import Hashids
# quitar el punto para usar Gradio.py
from .Data_Saver import DataSaver
import re
hashids = Hashids(salt = os.getenv("salt"), min_length=8)
class VectorDB:
    def __init__(self):
        self.vector_store = None
        self.conversations = []

    def split_text_into_chunks(self, text):
        # split text of type str into chunks, parts of the text of type str
        text = text.replace("\n","")
        text = re.sub(r'\s+', ' ', text)
        print(len(text))
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
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
        vectorstore_dir = Path(__file__).parent / "vectorstore"
        vectorstore_dir.mkdir(parents=True, exist_ok=True)
        with open(vectorstore_dir / f"{store_name}.pkl", "wb") as f:
            pickle.dump(vector_store, f)

    def load_vector_store(self, store_name):
        vectorstore_dir = Path(__file__).parent / "vectorstore"
        if (vectorstore_dir / f"{store_name}.pkl").exists():
            with open(vectorstore_dir / f"{store_name}.pkl", "rb") as f:
                self.vector_store = pickle.load(f)
        else:
            raise FileNotFoundError(f"File {store_name}.pkl not found in the 'vectorstore' directory!")

    def process_text(self, text, store_name):
        # split a large thext into smalls texts
        chunks = self.split_text_into_chunks(text)
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

    def get_conversation(self):

        return self.conversations
    
    def context_palm(self, context):
        extract_products = []
        if context not in ["main", "subscription", "panel-admin"]:
            try:
                get_products = DataSaver()
                extract_products = get_products.read_from_json(f'memory-AI-with-{context}', ['products'])
                output_dict = {}
                for product in extract_products['products']:
                    product_name = product['name']
                    output_dict[product_name] = product
                extract_products = output_dict
                decode = hashids.decode(context)
                id_context = int(decode[0])
                # Intenta obtener el contexto del cliente por su ID
                client_context = ClienContext.objects.get(client__id=id_context)
                return client_context.context, extract_products
            except Exception as e:
                print(e)
        else:
            current_dir = Path(__file__).parent
            ruta_absoluta = current_dir / "memory_text" / f"memory-AI-with-{context}.txt"

            if not ruta_absoluta.exists():
                raise FileNotFoundError(f"No file found for context '{context}'")

            with open(ruta_absoluta, 'r', encoding='utf-8') as f:
                contenido = f.read()
            return contenido, extract_products
    def get_context_palm(self, prompt):
        consulta =self.query(prompt)
        consulta_str = str(consulta)
        # Usar regex para extraer el contenido del texto
        content_pattern = r'Document\(page_content=\'(.*?)\'\)'
        matches = re.findall(content_pattern, consulta_str)
        
        # Combina todas las coincidencias encontradas en una sola cadena de texto
        cleaned_text = ' '.join(matches)
        return cleaned_text
        