from AI_Team.Logic.context_messages import CONTEXT_MESSAGES
from AI_Team.Logic.Chat.chat_history_module import Chat_history as messages
#from AITeam.AI_Team.Logic.Chat.chat_history_module import Chat_history as messages
from AI_Team.Logic.ollama.ollama_rag_Module import OllamaRag as o
#from ollama.ollama_rag_Module import OllamaRag as o


class ai_Handler:

    def __init__(self):
        self.ai = o()
        self.messages = messages()
        

    def call_ollama_no_rag(self,messages):
       return o.query_ollama(messages)

    def call_router(self,prompt,context):
        
        try:
            self.messages.add_system_message(context)
            self.messages.add_user_message(prompt)
            return self.ai.query_ollama(self.messages.get_messages())
        except Exception as clr:
            print(clr)
        
        

    def call_ai_temp_rag(self,prompt):
        
        return self.ai.query_temp_rag_single_question(prompt)

    def create_temp_rag_with_a_pdf(self,pdfdirectory):
        
        self.ai.add_pdf_to_new_temp_rag(pdfdirectory)


    

    
    


