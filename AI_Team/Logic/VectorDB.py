import os
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS, vectara
import faiss
import pathlib

class VectorDB:
    def __init__(self):
        self.vector_store = None
        self.conversation_buffer = []

    def split_text_into_chunks(self, text):
        # split text of type str into chunks, parts of the text of type str
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        return text_splitter.split_text(text=text)

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
            print('we get a issue:', e)
    
    def add_to_context(self, prompt, response):
        # Adding the user prompt and the AI response to the conversation buffer as a tuple
        self.conversation_buffer.append((prompt, response))

    def get_conversation(self):
        # Return the entire conversation history as a list of tuples
        return self.conversation_buffer
    
    def context_palm(self):
        current_dir = Path(__file__).parent
        ruta_absoluta = current_dir / "memory_text" / "memoryAI.txt"

        # Data preparation:
        with open(ruta_absoluta, 'r', encoding='utf-8') as f:
            contenido = f.read()

        return contenido