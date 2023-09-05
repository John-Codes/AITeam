import google.generativeai as palm
import pprint
# configuración de api
api_key = 'AIzaSyDW2ul61CVxQCyFM591byBSyC587YDey7o'
palm.configure(api_key=api_key)
# configuración de intancia del modelo
models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name
# variable string, entrada al usuario
pregunta = """
You are an expert at solving word problems.

Solve the following problem:

I have three houses, each with three cats.
each cat owns 4 mittens, and a hat. Each mitten was
knit from 7m of yarn, each hat from 4m.
How much yarn was needed to make all the items?

Think about it step by step, and show your work.
"""


# generación de respuesta con IA 
completion = palm.generate_text(
    model=model,
    prompt=pregunta,
    temperature=0,
)
# se imprime la respuesta
print(completion.result)

"""
FUnctions with google.generativa AI

chat(...): Calls the API and returns a types.ChatResponse containing the response.

chat_async(...): Calls the API and returns a types.ChatResponse containing the response.

configure(...): Captures default client configuration.

count_message_tokens(...)

generate_embeddings(...): Calls the API to create an embedding for the text passed in.

generate_text(...): Calls the API and returns a types.Completion containing the response.

get_model(...): Get the types.Model for the given model name.

list_models(...): Lists available models.
api_key = AIzaSyDW2ul61CVxQCyFM591byBSyC587YDey7o
implementación más facil menos configurable y personalizada
#response = palm.generate_text(prompt = pregunta)
#print('respuesta')
#print(response.result) #  'cold.
"""
