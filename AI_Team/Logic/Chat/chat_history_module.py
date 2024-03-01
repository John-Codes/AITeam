

class Chat_history:
    
    
    def add_to_context(self, prompt, response):
        self.conversations.append({"role": "user", "content": prompt})
        self.conversations.append({"role": "assistant", "content": response})

    def get_conversation(self):

        return self.conversations