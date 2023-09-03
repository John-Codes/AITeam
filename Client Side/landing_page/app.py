import google.generativeai as palm
import os
palm.configure(api_key=os.environ['API_KEY'])

response = palm.generate_text(prompt="The opposite of hot is")
print(response.result) #  'cold.'

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

"""
