import os
import openai
import google.generativeai as palm
from sender_mails import email_send
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import requests
import json
from sender_mails import *

def main():
    #result = CallChatGPT("Make python helloworld program")
    #result = CallPalm2("Make python helloworld program")
    Call("Make python helloworld program", "Palm2")


def Call(projectDescription, LLMName):
    if LLMName == "ChatGPT":
        return CallChatGPT(projectDescription)
    elif LLMName == "Palm2":
        return CallPalm2(projectDescription)


def CallChatGPT(projectDescription):
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

def CallChatGPT_Langchain(pregunta,docs, context):
    try:
        llm = ChatOpenAI(max_tokens=2048,temperature=1.0,model_name="gpt-3.5-turbo")
        chain = load_qa_chain(llm=llm,chain_type="stuff")
        with get_openai_callback() as cb:
            response = chain.run(input_documents=docs, question=pregunta)
    except Exception as e:
        prompt =f"""Por favor traduce este error {e} a una explicación fácil de entender para personas que no sepan programar.
        Y dales una sugerencia de cómo pueden evitar cometer el mismo error."""
        response = CallChatGPT(prompt)
        asunto = f'Error Notice from context: {context}'
        mensaje = f'''
        An error has ocurred when the user asked: \n
        {pregunta} \n
        this was asked in a chat with context: {context}
        '''
        notice_error(asunto, mensaje)
    return response

def CallPalm2(projectDescription):
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

    return response.result

def Check_Cuestion(prompt):
    #print("Función CallPalm2 invocada con:", projectDescription)
    try:
        palm.configure(api_key=os.getenv("Palm2APIKey"))
        #print('conectamos con check email')
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

def CallPalm(cuestion,context, examples):
    try:
        palm.configure(api_key=os.getenv("Palm2APIKey"))
    except Exception as e:
        print('something was wrong when trying to connect to the api', e)

    response = palm.chat(
        context=context,
        examples=examples,
        messages=cuestion,
        temperature=0.5)

    return response.last
        

if __name__ == "__main__":
    main()

