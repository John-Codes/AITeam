from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as palm
from ..Logic.LLMs import Call
import os
#key = 'AIzaSyDW2ul61CVxQCyFM591byBSyC587YDey7o'

def chat_ui(request):  
    if request.method == "POST":
        """ obtener e imprimir key del ambiente
        api_key = os.getenv("Palm2APIKey")

        # Check if the key exists and print it
        if api_key:
            print(f"The API key is: {api_key}")"""

        user_message = request.POST.get('message')
        print('user_message', user_message)
        response_data = {}
        response = None
        try:
            response = Call(user_message,"Palm2")
        except Exception as e:
            response_data['error'] = f"Something went wrong: {e}"      

        if response:
            response_data['ai_response'] = response
        else:
            response_data['ai_response'] = 'the api dont could response'
            
        return JsonResponse(response_data)

    return render(request, 'chat_ui.html')