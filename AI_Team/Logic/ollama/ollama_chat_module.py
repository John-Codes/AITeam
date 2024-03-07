import ollama

# stream = ollama.chat(
#     model='mistral',
#     messages=[{'role': 'user', 'content': 'Why is the sky blue?'}],
#     stream=True,
# )

# for chunk in stream:
#   print(chunk['message']['content'], end='', flush=True)

# def query_ollama(messages):
#     stream = ollama.chat(
#     model='mistral',
#     messages=messages,
#     stream=True,)
    
    
#     return stream