from django.http import JsonResponse
from .Chat.chat_history_module import Chat_history

def validate_request_data(data):
    action = data.get('action')
    current_chat = data.get('current_chat')
    message = data.get('message', '')
    
    if not current_chat:
        return None, JsonResponse({'error': 'current_chat is required'}, status=400)
    
    if action not in ['add_user_message', 'add_system_message']:
        return None, JsonResponse({'error': 'Invalid action'}, status=400)
    
    return (action, current_chat, message), None

def get_chat_history_from_session(request):
    if 'chat_history' not in request.session:
        return Chat_history()
    else:
        chat_history = Chat_history()
        chat_history.__dict__ = request.session['chat_history']
        return chat_history

def update_session_with_chat_history(request, chat_history):
    request.session['chat_history'] = chat_history.__dict__