from Logic.context_messages import CONTEXT_MESSAGES

class Chat_history:
    def __init__(self):
        self.current_chat = None
        self.messages = []

    def get_messages(self):
        return self.messages

    def add_user_message(self, prompt):
        self.messages.append({"role": "user", "content": prompt})

    def add_system_message(self, prompt):
        self.messages.append({"role": "system", "content": prompt})

    def set_page_static_messages(self, current_chat):
        self.messages.append(CONTEXT_MESSAGES[current_chat])

    def reset_history(self, pagemessages):
        self.messages = []
        self.set_page_static_messages(pagemessages)

    def set_current_chat(self, current_chat):
        if current_chat is None or current_chat != current_chat:
            print('reseteamos el historial')
            print('current_chat de chat_history',current_chat,'current_chat', current_chat)
            current_chat = current_chat
            self.reset_history(current_chat)
            
    #metodo que agrega al inicio de una lista con elementos los mensajes estaticos
    def set_static_messages_from_list(self, list_messages, current_chat):
        # agrega al inicio de una lista con elementos los mensajes estaticos
        list_messages.insert(0, CONTEXT_MESSAGES[current_chat])
        return list_messages