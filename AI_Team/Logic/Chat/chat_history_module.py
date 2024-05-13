#CONTEXT MESSAGES = PAGE STATIC MESSAGES
from AI_Team.Logic.context_messages import CONTEXT_MESSAGES
class Chat_history:
    

    def __init__(self):
        self.messages=[]
    
    # def add_to_context(self, prompt, response):
    #     self.messages.append({"role": "user", "content": prompt})
    #     self.messages.append({"role": "assistant", "content": response})

    # def get_conversation(self):

    #     return self.messages
    def get_messages(self):
        return self.messages
    def add_user_message(self,prompt):
        self.messages.append({"role": "user", "content": prompt})

    def add_system_message(self,prompt):
        self.messages.append({"role": "system", "content": prompt})
    def set_page_static_messages(self,pagemessages):
        self.messages.append(CONTEXT_MESSAGES[pagemessages][0])
        self.messages.append(CONTEXT_MESSAGES[pagemessages][1])
        self.messages.append(pagemessages)