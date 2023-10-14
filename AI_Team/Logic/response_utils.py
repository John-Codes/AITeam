
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
import json
import re
from .Data_Saver import DataSaver

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
    pattern_bold = r'\*\*(.*?)\*\*'
    matches = re.findall(pattern_bold, response)

    # Reemplazar cada coincidencia con las etiquetas HTML de negrita
    for match in matches:
        response = response.replace(f'**{match}**', f'<strong>{match}</strong><br>')

    # Si la respuesta contiene un formato de tabla
    if '|' in response:
        lines = response.split('\n')
        table_lines = [line for line in lines if line.strip().startswith('|')]
        
        if table_lines:
            # Extracting content before, the table, and after
            before_table = '\n'.join(lines[:lines.index(table_lines[0])]).strip()
            after_table = '\n'.join(lines[lines.index(table_lines[-1])+1:]).strip()
            
            table_html = '<table>'
            for line in table_lines:
                # Header
                if '|---' in line:
                    continue  # skip line with |---|---|
                elif line == table_lines[0]:
                    table_html += '<thead><tr>'
                    for header in line.split('|')[1:-1]:
                        table_html += f'<th>{header.strip()}</th>'
                    table_html += '</tr></thead>'
                # Rows
                else:
                    table_html += '<tr>'
                    for cell in line.split('|')[1:-1]:
                        table_html += f'<td>{cell.strip()}</td>'
                    table_html += '</tr>'
            table_html += '</table>'
            
            # Combining all parts with <p> tags with the "message-content" class for content before and after table
            response = f'<p class="message-content">{before_table}</p>{table_html}<p class="message-content">{after_table}</p>'
    
    # Cambia asteriscos por <br> para saltos de línea
    response = response.replace('*', '<br>')

    return mark_safe(response)
