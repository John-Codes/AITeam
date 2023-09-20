key = 'AIzaSyDW2ul61CVxQCyFM591byBSyC587YDey7o'
import google.generativeai as palm
from app import continue_conversation

Successfully = True
# gives the AI context to personalize messages
context = 'you attend to a client to give him information about the AITeam project'
try:
    # connection to the api
    palm.configure(api_key=key)
except Exception as e:
    print(f"Error al conectarse a la API: {e}")
    Successfully = False
# if we connect to the api successfully
if Successfully:    
    # while loop to keep the chat running
    # num_ messages controls whether to start or continue the conversation, since they are two different methods
    num_message = 0
    while True:
        
        # Request user input
        user_input = input("Usuario: ")

        if user_input.lower() == "exit":
            break

        try:
            # check if the conversation starts or continues
            if num_message == 0:
                # start with method palm
                response = palm.chat(context="Respond only with yes or no", messages=user_input, temperature=1)
                # once started in the next step of the loop it should start saving the conversation
                print('IA:', response.last)
                print('the entire response', response)

                num_message += 1
            else:
                print('continuamos conversación')
                next_message = continue_conversation(response, str(user_input))
                # continue with the reply method, this is important so that the AI takes previous messages into account
                print('IA:', next_message.last)
                print('the entire response', next_message)
            
            # Print the response from the AI
           
        except Exception as e:
            print(f"something was wrong, please try again: {e}")
else:
    print("Network connection error, try again")
