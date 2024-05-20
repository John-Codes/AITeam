from AI_Team.Logic.context_messages import CONTEXT_MESSAGES
from AI_Team.Logic.Chat.chat_history_module import Chat_history as messages
#from AITeam.AI_Team.Logic.Chat.chat_history_module import Chat_history as messages
from AI_Team.Logic.ollama.ollama_rag_Module import OllamaRag as o
#from ollama.ollama_rag_Module import OllamaRag as o


class ai_Handler:

    def __init__(self):
        self.ai = o()
        self.messages = messages()
        self.retriever = None
        

    def call_ollama_no_rag(self,messages):
       return o.query_ollama(messages)

    def call_ollama_stream(self, messsages):
        return self.ai.stream_query_ollama(messsages)

    def update_messages(self,ia_response, prompt):
        if ia_response:
            self.messages.add_system_message(ia_response)
        self.messages.add_user_message(prompt)
        return self.messages.get_messages()
    
    def reset_history(self, current_chat_user):
        self.messages.set_current_chat(current_chat_user)
        return self.messages.get_messages()
    #deprecated
    def call_router(self,prompt,context):
        #
        try:
            #self.messages.add_system_message(context)
            self.messages.add_user_message(prompt)
            return self.ai.query_ollama(self.messages.get_messages())
        except Exception as clr:
            print(clr)
    
    def call_router_async(self, prompt, context):
        try:
            print('call router', prompt, context)
            self.messages.add_system_message(context)
            self.messages.add_user_message(prompt)
            # Llamada a la función asíncrona
            return self.messages.get_messages()
        except Exception as clr:
            print(clr)
        
        

    def call_ai_temp_rag(self,prompt):
        # return a formmated prompt with the context
        return self.ai.query_temp_rag_single_question(prompt)

    def create_temp_rag_with_a_pdf(self,pdfdirectory, rag_name):
        
        self.ai.add_pdf_to_new_temp_rag(pdfdirectory)
    
    def create_perm_rag_with_a_pdf(self,pdfdirectory,rag_name):
        
        self.ai.add_pdf_to_new_perm_rag(pdfdirectory, rag_name)

    def get_vectorstore_by_rag_name(self, rag_name):

        self.ai.find_vectorstore_by_rag_name(rag_name)

    def static_messages(self, context):
        self.messages.set_page_static_messages(context)
        return self.messages

