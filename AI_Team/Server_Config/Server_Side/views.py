from django.http import JsonResponse
from django.shortcuts import render
from AI_Team.Logic.LLMs import Call, Check_Cuestion
from AI_Team.Logic.response_utils import render_html

def chat_ui(request):
    # Initializing the response_data dictionary.
    response_data = {}

    # Ensure the request is a POST request.
    if request.method == "POST":
        user_message = request.POST.get('message')
        phase = request.POST.get('phase')
        
        # Handle the user's message.
        if phase == 'user_message':
            #print('when phase is user_message',user_message)
            response_data['user_message_div'] = render_html('chat_messages/user_message.html', user_message)
            return JsonResponse(response_data)

        # Handle the AI's response.
        elif phase == 'ai_response':
            #print('when phase is ai_response',user_message)
            try:
                ai_response = Call(user_message, "Palm2")
            except Exception as e:
                response_data['error'] = f"Something went wrong: {e}"
                return JsonResponse(response_data, status=500)  # Respond with a 500 status code for internal errors.

            # Ensure the AI returned a response.
            if ai_response:
                response_data['ia_message_div'] = render_html('chat_messages/ia_message.html', ai_response, format = True)
                Check_Cuestion(user_message)
            else:
                response_data['error'] = 'The API could not respond.'
                return JsonResponse(response_data, status=400)  # Respond with a 400 status code for bad requests.
            
            return JsonResponse(response_data)

    # Render the chat UI template for non-POST requests.
    return render(request, 'chat_ui.html')



def login(request):  
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        print(email, password)      

    return render(request, 'login.html')