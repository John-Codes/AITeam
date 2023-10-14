import os
import openai
import google.generativeai as palm
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
# quitar el punto para usar Gradio.py
from .sender_mails import *
from .json_page import ContentPage


def generate_json(user_info):
    #openai.api_base = "https://openrouter.ai/api/v1"
    #openai.api_key =os.getenv("Open_Router_API_KEY")
    print('prompt to generate json')
    print(user_info)
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
        "Each tag includes a text that the user can read and a URL to which he will be redirected when clicking."
    )
    _input = prompt.format_prompt(question=user_query, user_info= user_info)
    print('calling the open_router')
    chat_model = ChatOpenAI(
        model="openai/gpt-4-32k",
        openai_api_key=os.getenv("Open_Router_API_KEY"),
        openai_api_base= "https://openrouter.ai/api/v1",
        headers={
            "HTTP-Referer": 'http://127.0.0.1:8000/', # To identify your app. Can be set to localhost for testing
        },
        max_tokens=3000
    )
    print('we call openrouter')
    # Run the Chain and capture the output
    output = chat_model(_input.to_messages())
    try:
        parsed = parser.parse(output.content)
        #print(output.content)
        #print(parsed)
        print('json return')
        return 'website = {' + str(parsed) + '}', output.content
    except Exception as  e:
        json_succes = str(e)
        print('an error has ocurred',json_succes)
        return json_succes
    
    

def CallChatGPT(projectDescription):
    try:
        response = ChatOpenAI(
        model="openai/gpt-4-32k",
        openai_api_key=os.getenv("Open_Router_API_KEY"),
        openai_api_base= "https://openrouter.ai/api/v1",
        headers={
            "HTTP-Referer": 'http://127.0.0.1:8000/', # To identify your app. Can be set to localhost for testing
        },
        max_tokens=3000,
        temperature=0.6,
        messages = [
        {
        "role": "user",
        "content": f"{projectDescription}",
        }
        ],
        )
      # Extract the GPT response string
        gpt_response_string = response['choices'][0]['message']['content']
        return gpt_response_string
    except Exception as e:
        print(e.message)

def CallChatGPT_Langchain(pregunta,docs, context):
    try:
        llm =  ChatOpenAI(
        model="openai/gpt-4-32k",
        openai_api_key=os.getenv("Open_Router_API_KEY"),
        openai_api_base= "https://openrouter.ai/api/v1",
        headers={
            "HTTP-Referer": 'http://127.0.0.1:8000/', # To identify your app. Can be set to localhost for testing
        },
        max_tokens=3000,
        temperature=1,
        )
        
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
    print('acces to the Check cuestion function')
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
