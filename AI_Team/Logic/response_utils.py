
from django.utils.safestring import mark_safe
import re
from django.template.loader import render_to_string

# We'll start by creating a helper function to render the HTML for messages.
def render_html(template, message, format = False):
    """Helper function to render and format the message readeble the message to HTML."""
    if format:
        format_message = format_response(message)
        return render_to_string(template, {"message": format_message})
    else:
        return render_to_string(template, {"message": message})

def format_response(response):
    # Buscar todas las palabras en negrita "**word**" en el texto de respuesta
    pattern = r'\*\*(.*?)\*\*'
    matches = re.findall(pattern, response)

    # Reemplazar cada coincidencia con las etiquetas HTML de negrita
    for match in matches:
        response = response.replace(f'**{match}**', f'<strong>{match}</strong>')

    return mark_safe(response)