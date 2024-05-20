from django.http import JsonResponse
from .Chat.chat_history_module import Chat_history
from AI_Team.Logic.AIManager.llm_api_Handler_module import ai_Handler
def validate_request_data(data):
    
    current_chat = data.get('current_chat')
    
    if not current_chat:
        return None, JsonResponse({'error': 'current_chat is required'}, status=400)
    
    
    return current_chat, None

def get_chat_history_from_session(request):
    if 'chat_history' not in request.session:
        return Chat_history()
    else:
        chat_history = Chat_history()
        chat_history.__dict__ = request.session['chat_history']
        return chat_history


def get_ai_handler_from_session(request):
    if 'ai_handler' in request.session:
        ai_handler = ai_Handler()
        ai_handler.set_retriever(request.session['ai_handler']['retriever'])
    return ai_handler
        
    

def update_session_with_chat_history(request, chat_history):
    request.session['chat_history'] = chat_history.__dict__