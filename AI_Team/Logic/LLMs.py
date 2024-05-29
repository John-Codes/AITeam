import os
import openai
import json
import google.generativeai as palm
from AI_Team.Logic.Chat.chat_history_module import Chat_history
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOllama
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
#from ollama.ollama_rag_Module import OllamaRag
# quitar el punto para usar Gradio.py
from .sender_mails import *
from .json_page import ContentPage, Product
import tiktoken
import runpod
import requests

#ollama = OllamaRag()
chat = Chat_history()
# agrega a la función  esta función la clase Count_Tokens y usala para contar los tokens generados

def calling_runpod(context, last_messsages, prompt_user):
    id_gpu = "ampere48"
    api_key = os.getenv("RUNPOD_API_KEY")
    url = f'https://api.runpod.io/graphql?{api_key}=pewpew'
    headers = {'content-type': 'application/json'}
    data = {
        "query": f"""
        mutation {{
            saveEndpoint(input: {{
                gpuIds: "{id_gpu}",
                idleTimeout: 5,
                locations: "US",
                name: "Generated Endpoint -fb",
                networkVolumeId: "",
                scalerType: "QUEUE_DELAY",
                scalerValue: 4,
                templateId: "xkhgg72fuo",
                workersMax: 3,
                workersMin: 0
            }}) {{
                gpuIds
                id
                idleTimeout
                locations
                name
                scalerType
                scalerValue
                templateId
                workersMax
                workersMin
            }}
        }}
        """
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response)
    print(response.json())

def calling_runpod2(context, last_messsages, prompt_user):
    print("calling_runpod")
    runpod_api = os.getenv("RUNPOD_API_KEY")
    runpod_endpoint = os.getenv("RUNPOD_ENDPOINT")
    print(runpod_endpoint)
    url = f"https://{runpod_endpoint}-8080.proxy.runpod.net/generate"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {runpod_api}"
    }
    
    payload = {
        "inputs": json.dumps({
            "input": prompt_user,
            "context": context,
            "last_messsages": last_messsages,
        })
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        print("Success!")
        return response.json()
    else:
        print("Failed!")
        print(response)
        runpod.api_key = runpod_api

        # Crea un endpoint
        endpoint = runpod.Endpoint(runpod_endpoint)

        # Ejecuta el pod
        run_request = endpoint.run({"input": "types of data in python"})
        print(run_request)
        # Imprime la respuesta del pod
        print(run_request.result())
        return f"Failed to get response: {response.status_code}, {response.text}"


def generate_json(user_info):
    
    try:
        print("generate_json")
        user_info = str(user_info)
        # Instantiate the parser with the new model.
        parser = PydanticOutputParser(pydantic_object=ContentPage)

        # Update the prompt to match the new query and desired format.
        prompt = ChatPromptTemplate(
            messages=[
                HumanMessagePromptTemplate.from_template(
                    "answer the users question as best as possible.\n{format_instructions}\n{question}\n\nUser Information:\n{user_info}"
                )
            ],
            input_variables=["question", "user_info"],
            partial_variables={
                "format_instructions": parser.get_format_instructions(),
            },
        )

        # Generate the input using the updated prompt.
        user_query = (
            "Generate a detailed Custom page content of a user info"
            "the content include the meta tags keywords, description, the tag title of the page, and the header is h1 tag of the page."
            "Each tag includes a text that the user can read and a url to which he will be redirected when clicking."
            "Finally, it detects the products sent by the user, each product is an item of the listand each product has the following dictionary keys:  product name, description, value, link to buy"
            "Remember that you only give me the text, no HTML tags, you dont generate code, only generate a json file"
        )
        _input = prompt.format_prompt(question=user_query, user_info= user_info)

        #chat.add_user_message(user_query)
        #ollama.query_ollama(chat.get_messages())
    except Exception as e:
        print('error generating the json',e)
    chat_model = ChatOllama(
        temperature=0.8,
        model="llama3",
    )
    #ChatGooglePalm(google_api_key=google_api_key, temperature=0.5, top_k=40, top_p = 0.95, max_output_tokens= 4024)
    #chat_model = ChatOpenAI(
    #    model="openai/gpt-4-32k",
    #    openai_api_key=os.getenv("Open_Router_API_KEY"),
    #    openai_api_base= "https://openrouter.ai/api/v1",
    #    headers={
    #        "HTTP-Referer": 'http://127.0.0.1:8000/', # To identify your app. Can be set to localhost for testing
    #    },
    #    max_tokens=3000
    #)
    # Run the Chain and capture the output
    output = chat_model.invoke(_input.to_messages())
    try:
        parsed = parser.parse(output.content)
        return output.content
    except Exception as  e:
        print('error')
        print(e)
        json_succes = str(e)
        return json_succes
    
    

# def CallChatGPT(projectDescription):
#     try:
#         encoding = tiktoken.encoding_for_model("gpt-4")
#         token_prompt = len(encoding.encode(projectDescription))
#         response = ChatOpenAI(
#         model="openai/gpt-4-32k",
#         openai_api_key=os.getenv("Open_Router_API_KEY"),
#         openai_api_base= "https://openrouter.ai/api/v1",
#         headers={
#             "HTTP-Referer": 'http://127.0.0.1:8000/', # To identify your app. Can be set to localhost for testing
#         },
#         max_tokens=3000,
#         temperature=0.6,
#         messages = [
#         {
#         "role": "user",
#         "content": f"{projectDescription}",
#         }
#         ],
#         )
#       # Extract the GPT response string
#         gpt_response_string = response['choices'][0]['message']['content']

#         return gpt_response_string, token_prompt
#     except Exception as e:
#         print(e.message)

# def CallChatGPT_Langchain(pregunta,docs, context):
#     try:
#         encoding = tiktoken.encoding_for_model("gpt-4")
#         pregunta_tokens = len(encoding.encode(pregunta))
#         docs_tokens = sum(len(encoding.encode(docs)) for doc in docs)
#         total_tokens =pregunta_tokens + docs_tokens
#         max_tokens = 3000 + total_tokens
#         llm =  ChatOpenAI(
#         model="openai/gpt-4-32k",
#         openai_api_key=os.getenv("Open_Router_API_KEY"),
#         openai_api_base= "https://openrouter.ai/api/v1",
#         headers={
#             "HTTP-Referer": 'http://127.0.0.1:8000/', # To identify your app. Can be set to localhost for testing
#         },
#         max_tokens=max_tokens,
#         temperature=1,
#         )
        
#         chain = load_qa_chain(llm=llm,chain_type="stuff")
#         with get_openai_callback() as cb:
#             response = chain.run(input_documents=docs, question=pregunta)
#     except Exception as e:
#         prompt =f"""Por favor traduce este error {e} a una explicación fácil de entender para personas que no sepan programar.
#         Y dales una sugerencia de cómo pueden evitar cometer el mismo error."""
#         response, total_tokens = CallChatGPT(prompt)
#         asunto = f'Error Notice from context: {context}'
#         mensaje = f'''
#         An error has ocurred when the user asked: \n
#         {pregunta} \n
#         this was asked in a chat with context: {context}
#         '''
#         notice_error(asunto, mensaje)
#     return response, total_tokens

def CallPalm2(prompt, products):
    google_api_key = os.getenv("Palm2APIKey")
    prompt = str(prompt)
    # Instantiate the parser with the new model.
    parser = PydanticOutputParser(pydantic_object=Product)

    # Update the prompt to match the new query and desired format.
    detected_products = ChatPromptTemplate(
        messages=[
            HumanMessagePromptTemplate.from_template(
                "answer the users question in a json format.\n{format_instructions}Products:\n{products}\n{question}\n\nUser ask for any product?:\n{prompt}"
            )
        ],
        input_variables=["question", "prompt", "products"],
        partial_variables={
            "format_instructions": parser.get_format_instructions(),
        },
    )

    # Generate the input using the updated prompt.
    user_query = (
        """Extract the name of each product, then look if the user has mentioned any of these products by name,
            if they ask about any product you must answer with the following format:
            {name: Product Name}
            If the user does not mention or ask any of the products that I have shown you then you simply have to answer {name: no products}, 
            for example if in the dict there are the products Coca-Cola and Pepsi and the user asks for another soft drink called Fanta, you must return No Product
            """
    )
    _input = detected_products.format_prompt(question=user_query, prompt= prompt, products = products)
    #chat_model = ChatGooglePalm(google_api_key=google_api_key, temperature=0.7, top_k=40, top_p = 0.95, max_output_tokens= 4024)
    #output = chat_model(_input.to_messages())
    try:        
        return 0 #output.content
    except Exception as  e:
        print('error')
        print(e)
        json_succes = str(e)
        return json_succes

def Check_Cuestion(prompt):
    #print("Función CallPalm2 invocada con:", projectDescription)
    try:
        palm.configure(api_key=os.getenv("Palm2APIKey"))
    except Exception as e:
        print('something was wrong when trying to connect to the api', e)

    cuestion = f'Keep in mind the grammar of the following text and answer me if it is a question or not:{prompt}'
    response = palm.chat(context="Respond only with yes or no", messages=cuestion, temperature=0)
    if prompt != '':
        response_lower = str(response.last).lower()
    else:
        response_lower = 'not'

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
    print('context', context)
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

def Call_openrouter(examples, prompt, context):
    print(examples)
    api_key = os.getenv("AIROBORS_API_KEY")
    api_endpoint = "https://openrouter.ai/api/v1/chat/completions"
    # list the messages in the prompt
    print(type(examples))
    print(isinstance(examples, list))
    examples.append({"role": "user", "content": prompt})
    print('list_messages', examples)
    # Replace with the actual headers required by the API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data=json.dumps({
        "model": "jondurbin/airoboros-l2-70b", # Optional
        "messages": examples
    })
    
    # Replace with the actual input data for the model
    # input_data = {
    #     "prompt": f'prompt: {prompt}\n\ncontext: {context}',
    # }

    # Send the request to the API
    response = requests.post(api_endpoint, headers=headers, data=data)

    # Check if the request was successful
    if response.status_code ==  200:
        # Process the response
        output = response.json()
        #print(output)
        response = output['choices'][0]['message']['content']
        #print('response',response)
    else:
        print(f"Request failed with status code {response.status_code}")
    return response 


def call_ollama(chat,promtp, context):
    pass