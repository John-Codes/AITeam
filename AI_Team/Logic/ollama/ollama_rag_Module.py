import os
import ollama

#import bs4
import asyncio
import chromadb
#Ollama Rag Youtube
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores.chroma import Chroma
from langchain_community import embeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.text_splitter import TokenTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import fitz
from semantic_text_splitter import CharacterTextSplitter, HuggingFaceTextSplitter
from tokenizers import Tokenizer
import re 
ollama_url = os.getenv('OLLAMA_BASE_URL', "http://localhost:11434")  #'http://ollama:11434
print('config_ollama',ollama_url)
# Configure the Ollama client with the obtained URL
ollama_api = ollama.Client(host=ollama_url)
#add static messages to chat history and pass it from views.

model_local =ChatOllama(model="mistral")
pdf ="/Resume 2024.pdf"

# Get the current working directory
current_directory = os.getcwd()
pathpdf= current_directory+pdf
vectorDBDir="UsersVectorDbFiles"

class OllamaRag:
    def __init__(self):
        pass


    #PDF Preping
    def replace_newlines_with_space(self,text):
        # Replace '\n' with a space
        return text.replace('\n', ' ')

    def clean_string_for_file_name(self,txt):
        try:
            
            match = re.search(r"([^.]*)(\.[^.]*)*$", txt)  # Search for the pattern in the string
            if match:
                txt = match.group(1)  # Extract the part before the last dot
                print(txt)  # Output: "/Resume 2024"
            #txt = txt.replace(".","")
            txt = txt.replace(" ","")
            txt = txt.replace("/","")
            txt = txt.replace("@","")
            return txt
        except Exception as csf:
            print(self.clean_string_for_file_name.__name__,csf)

    def extract_text_from_pdf(self,file_path):
        try:
            print("Path to PDF:", file_path)
            
            doc = fitz.open(file_path)
            text_contents = ""  # Initialize an empty string to store text
            for page in doc:
                text = page.get_text()
                text_contents += text  # Append the text from each page
            return self.replace_newlines_with_space(text_contents)
        except Exception as etfp:
            print(etfp)

    def semantic_text_split_no_model(self,content, maxCharacters):
        try:
            max_characters = 200
            splitter = CharacterTextSplitter(trim_chunks=False)
            chunks_no_model = splitter.chunks(content, max_characters)
            return chunks_no_model
        except Exception as sts:
            print(self.semantic_text_split_no_model.__name__,sts)

    def semantic_text_split_bert(self,content, max_tokens):
        try:
            
            tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
            splitter = HuggingFaceTextSplitter(tokenizer, trim_chunks=False)
            splitter = CharacterTextSplitter(trim_chunks=False)
            chunks = splitter.chunks(content, max_tokens)
            return chunks
        except Exception as sts:
            print(self.semantic_text_split_no_model.__name__,sts)

    def string_list_to_hf_documents(self,text_list, pathinfo):
        documents = []
        for text in text_list:
            # Create a Document instance for each text string
            doc = Document(page_content=text, metadata={'source': pathinfo})
            documents.append(doc)
        return documents

    def text_spliter_for_vectordbs(self,text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return text_splitter.split_documents(text)
    
    def print_splits(self,splits):
        
        for i, split in enumerate(splits, start=1):
            print(f"Split {i}:")
            print(split)
            print("------")  # Separator for readability


#ChromaDB Use, can read DB in files.
    def new_persisted_ChromaDb_all_mini(self,doc_splits,file_name):
            '''Works Super Well!'''
            dir = self.get_user_vectorDB_directory()
            self.vectorstore= chromadb.PersistentClient(dir)
            collection = self.vectorstore.create_collection(name=file_name)
            collection.add(
                documents=["Johnny is the Master of the planet","Johnny is the king of AI"],
                metadatas=[{"source":"my_source","page":1},{"source":"mysource"}],
                ids=["id1","id2"]
            )
    def get_user_vectorDB_directory(self):
        
        try:
            
            # Construct the path to the VectorDbFiles directory
            base_directory = current_directory = os.getcwd()
            vector_db_directory = os.path.join(base_directory, vectorDBDir)
            
            return vector_db_directory
        except Exception as gud:
            print(self.get_user_directory,gud)
        
        # If the user's directory is not found, return None
        return None
    
    def get_persisted_ChromaDB(self):
        '''WORKS REALLY WELL'''
        try:
                dir =self.get_user_vectorDB_directory()

                self.vectorstore = chromadb.PersistentClient(path=dir)
                
                #self.retriever = self.vectorstore.as_retriever()
                print(f"Got Persisted Vector Store in {dir}")
        except Exception as cmdbe:
                print(self.get_persisted_ChromaDB.__name__, cmdbe)

    def query_persisted_chromadb_rag(self,question):
        try:
            print(self.vectorstore.list_collections())
            collection=  self.vectorstore.get_collection("John")
            retrieved_docs = collection.query(
                   query_texts=[question],
                    n_results=3,
                    include=['documents']
                    
                )
            
          
            #Extracting the documents from the retrieved_docs object
            documents = retrieved_docs['documents']

            #Joining the strings in the documents into a single string
            joined_string = ' '.join(documents[0])

            #Printing the result
            print(joined_string)
            return self.ollama_llm_query_single_question(question, joined_string)
        except Exception as rg:
            print(self.query_persisted_chromadb_rag.__name__,rg)




#Chroma only for demo cant load saved files\|/
    def new_temp_chroma_and_retriever(self,doc_splits):
        try:
            self.vectorstore = Chroma.from_documents(
            documents=doc_splits,
            embedding = embeddings.ollama.OllamaEmbeddings(model='mistral'),
            collection_name="rag_chroma",
            )
            
            self.retriever= self.vectorstore.as_retriever()
            print("New Temp vector Store Created and Initialized")
        except Exception as cmdbe:
            print(self.new_temp_chroma_and_retriever.__name__, cmdbe)

    def new_Persisted_chromadb_and_retriever(self, doc_splits, x_file_name):
        try:
            # Base directory where all vector DB files will be stored
            base_directory = os.path.join(os.getcwd(), "VectorDbFiles")
            
            # Directory for specific file vectors
            x_file_vectors_directory = os.path.join(base_directory, f"{x_file_name}Vectors")
            
            # Final directory for the specific vector DB
            persist_directory = os.path.join(x_file_vectors_directory, f"{x_file_name}Vdb")

            # Ensure the final persist directory exists or create it
            os.makedirs(persist_directory, exist_ok=True)

            self.vectorstore = Chroma.from_documents(
                documents=doc_splits,
                embedding=embeddings.ollama.OllamaEmbeddings(model='mistral'),
                collection_name="rag_chroma",
                persist_directory=persist_directory  # Pass the newly formed directory to persist the data
            )
            
            self.retriever = self.vectorstore.as_retriever()
            print(f"New Persisted Vector Store Created and Initialized at {persist_directory}")
        except Exception as cmdbe:
            print(self.new_Persisted_chromadb_and_retriever.__name__, cmdbe)

    def format_docs(self,docs):
        return "\n\n".join(doc.page_content for doc in docs)
 
    def ollama_llm_query_single_question(self,question, context):
        try:    
            formatted_prompt = f"Question: {question}\n\nContext: {context}"
            response = ollama_api.chat(model='mistral', messages=[{'role': 'user', 'content': formatted_prompt}])
            return response['message']['content']
        except Exception as oll:
            print(self.ollama_llm_query_single_question.__name__,oll)
    
    def format_docs(self,docs):

        try:    
            return "\n\n".join(doc.page_content for doc in docs)
        except Exception as fm:
            print(self.format_docs.__name__,fm)

    def query_temp_rag_single_question(self,question):
        try:
            
            retrieved_docs = self.retriever.invoke(question)
            formatted_context = self.format_docs(retrieved_docs)
            return self.ollama_llm_query_single_question(question, formatted_context)
        except Exception as rg:
            print(self.query_temp_rag_single_question.__name__,rg)
    
    def query_temp_rag_and_chat(self,conversation):
        pass

    def add_pdf_to_new_temp_rag(self, pathpdf):
            text = self.extract_text_from_pdf(pathpdf)
            splits = self.semantic_text_split_bert(text, 500)
            doc_splits = self.string_list_to_hf_documents(splits, pathpdf)
            doc_splits = self.text_spliter_for_vectordbs(doc_splits)
            self.new_temp_chroma_and_retriever(doc_splits)
    
    def query_ollama(self,messages):
        
        stream = ollama_api.chat(
        model='mistral',
        messages=messages,
        stream=False,)
        
        print(stream['message']["content"])
        return stream['message']["content"]
        
    def stream_query_ollama(self, messages):
        stream = ollama_api.chat(
        model='mistral',
        messages=messages,
        stream=True,)
        
        
        for chunk in stream:
            print(chunk['message']['content'], end='', flush=True)
            yield chunk['message']['content']




if __name__ == "__main__":

       try:
            
            o = OllamaRag()
            o.add_pdf_to_new_temp_rag(pathpdf)
            result = o.query_temp_rag_single_question("Who is Johnny?")
            print(result)

        
       except Exception as loade:
            print( loade)