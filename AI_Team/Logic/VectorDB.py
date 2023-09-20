import os
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

class VectorDB:
    def __init__(self):
        self.vector_store = None

    def split_text_into_chunks(self, text):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        return text_splitter.split_text(text=text)

    def convert_text_to_embeddings(self, chunks):
        embeddings = OpenAIEmbeddings()
        return FAISS.from_texts(chunks, embedding=embeddings)

    def save_vector_store(self, store_name, vector_store):
        with open(f"{store_name}.pkl", "wb") as f:
            pickle.dump(vector_store, f)

    def load_vector_store(self, store_name):
        if os.path.exists(f"{store_name}.pkl"):
            with open(f"{store_name}.pkl", "rb") as f:
                self.vector_store = pickle.load(f)
        else:
            raise FileNotFoundError(f"File {store_name}.pkl not found!")

    def process_text(self, text, store_name):
        chunks = self.split_text_into_chunks(text)
        if os.path.exists(f"{store_name}.pkl"):
            self.load_vector_store(store_name)
        else:
            self.vector_store = self.convert_text_to_embeddings(chunks)
            self.save_vector_store(store_name, self.vector_store)

    def query(self, query_text, k=3):
        try:
            if self.vector_store:
                vector = self.vector_store.similarity_search(query=query_text, k=k)
                return vector
            else:
                raise Exception("Vector store not loaded or created!")
        except Exception as e:
            print('we get a issue:', e)