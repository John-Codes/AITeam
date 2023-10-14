import os 
import gradio as gr
from Memory import consulta_IA_openai


context_input = 'memory_text/context_aseguradora.txt'


def message_and_history(input, history, context):
    history = history or []
    s = list(sum(history, ()))
    s.append(input)
    inp = ' '.join(s)
    output = consulta_IA_openai(inp, context_input)
    history.append((input, output))
    return history, history

block = gr.Blocks(theme=gr.themes.Monochrome())
with block:
    gr.Markdown("""<h1><center>AI Aurora </center></h1> 
    """) 
    chatbot = gr.Chatbot(show_label=False)
    message = gr.Textbox(placeholder='Escribe tu mensaje', show_label=False)
    state = gr.State()
    context = gr.State()
    submit = gr.Button("Enviar mensaje")
    submit.click(message_and_history,
    inputs=[message, state, context],
    outputs=[chatbot, state])
block.launch(share= True)

