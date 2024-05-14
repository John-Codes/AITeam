from AI_Team.Logic.context_messages import CONTEXT_MESSAGES

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
        self.messages.append(CONTEXT_MESSAGES[current_chat][0])
        self.messages.append(CONTEXT_MESSAGES[current_chat][1])

    def reset_history(self, pagemessages):
        self.messages = []
        self.set_page_static_messages(pagemessages)

    def set_current_chat(self, current_chat):
        if self.current_chat is None or self.current_chat != current_chat:
            self.current_chat = current_chat
            self.reset_history(current_chat)