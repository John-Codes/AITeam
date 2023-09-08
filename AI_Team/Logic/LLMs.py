import os
import openai
import google.generativeai as palm
from .sender_mails import email_send

def main():
    #result = CallChatGPT("Make python helloworld program")
    #result = CallPalm2("Make python helloworld program")
    Call("Make python helloworld program", "Palm2")


def Call(projectDescription, LLMName, key=None):
    if LLMName == "ChatGPT":
        return CallChatGPT(projectDescription)
    elif LLMName == "Palm2":
        return CallPalm2(projectDescription, key)


def CallChatGPT( projectDescription):
    try:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
            messages = [
        {
        "role": "user",
        "content": f"{projectDescription}",
        }
        ],
        temperature=0.6,
        max_tokens=3000,
        )
      # Extract the GPT response string
        gpt_response_string = response['choices'][0]['message']['content']
        return gpt_response_string
    except Exception as e:
        print(e.message)

def CallPalm2(projectDescription, key):
    #print("Función CallPalm2 invocada con:", projectDescription)
    try:
        palm.configure(api_key=os.getenv("Palm2APIKey"))
    except Exception as e:
        print('something was wrong when trying to connect to the api', e)
    
    prompt = f"""{projectDescription}"""

    print('the prompt what IA is accessing:', prompt)
    try:
        response =palm.generate_text(
            model= 'models/text-bison-001',
            temperature= 0.7,
            candidate_count= 1,
            top_k= 40,
            top_p= 0.95,
            max_output_tokens= 4024,
            stop_sequences= [],
            safety_settings= [{"category":"HARM_CATEGORY_DEROGATORY","threshold":1},{"category":"HARM_CATEGORY_TOXICITY","threshold":1},{"category":"HARM_CATEGORY_VIOLENCE","threshold":2},{"category":"HARM_CATEGORY_SEXUAL","threshold":2},{"category":"HARM_CATEGORY_MEDICAL","threshold":2},{"category":"HARM_CATEGORY_DANGEROUS","threshold":2}],
            prompt = prompt
            
    )    
    except Exception as e:
        response = str(e)
        print('error when generating text by the AI', e)
        print(response)

    """response = palm.generate_text(
    **defaults,
    prompt=prompt
    )"""

    #print('this the prompt', prompt)
    #print('this is the unique result', response.result)
    #print('this is the entire result', response)

    return response.result

def Check_Cuestion(prompt):
    #print("Función CallPalm2 invocada con:", projectDescription)
    try:
        palm.configure(api_key=os.getenv("Palm2APIKey"))
        print('conectamos con check email')
    except Exception as e:
        print('something was wrong when trying to connect to the api', e)

    cuestion = f'Keep in mind the grammar of the following text and answer me if it is a question or not:{prompt}'
    response = palm.chat(context="Respond only with yes or no", messages=cuestion, temperature=0)
    response_lower = str(response.last).lower()
    print('yes or not:',response_lower)

    affirmative_expressions = ['is a question','yes' ]
    negative_expressions = ['not,' 'no', 'statement']
    affirmative = False
    for expr in affirmative_expressions:
        if expr in response_lower:
            affirmative = True
            break
    for expr in negative_expressions:
        if expr in response_lower:
            affirmative = False
            break
    if affirmative:
        email_send(prompt)
        

if __name__ == "__main__":
    main()

