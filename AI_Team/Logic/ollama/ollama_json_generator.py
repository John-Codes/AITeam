import ollama

class jsonPageDescriptionOllama:
    def __init__(self, summary):
        self.summary = summary

    def call_ollama(self, user_prompt, system_prompt):
        """ Método central para llamar a la API de Ollama. """
        try:
            ollama_response = ollama.chat(
                
                model='llama3', 
                messages=[
                    {'role': 'system', 'content': f"Contesta siempre de forma clara, concisa, corta y sencilla. responde llanamente a la instrucción que de da el usuario, evita respuestas largas y sugerencias innecesarias.\n {system_prompt}"},
                    {'role': 'user', 'content': user_prompt}
                ]
            )
            return ollama_response['message']['content']
        except Exception as e:
            print(e)
            print ("Error al llamar a Ollama. Intenta de nuevo.")
    def create_title(self):
        """ Genera el título utilizando Ollama. """
        system_prompt = "Genera un título para una página web basado en el resumen del PDF. El título debe ser llamativo, conciso y reflejar el tema principal del contenido. Que no sea demasiado largo y de maximo 3 palabras"
        user_prompt = f"Necesito un título llamativo y conciso para una página web que refleje el tema principal de este resumen: {self.summary}. Debe ser breve. Respondeme en el mismo idioma que este mensaje."
        return self.call_ollama(user_prompt, system_prompt)

    def create_header(self):
        """ Genera el encabezado utilizando Ollama. """
        system_prompt = "Genera un encabezado secundario para una página web que complemente el título y ofrezca más detalles sobre el contenido del PDF."
        user_prompt = f"Necesito un encabezado para la pestaña del navegador que sea breve y capte la esencia de este contenido: {self.summary}. Debe ser suficientemente informativo pero conciso, ideal para mostrar en la pestaña del navegador así que debe ser corto de maximo 5 palabras. Respondeme en el mismo idioma que este mensaje."

        return self.call_ollama(user_prompt, system_prompt)

    def create_description(self):
        """ Genera la descripción utilizando Ollama. """
        system_prompt = "Genera una descripción meta para SEO de una página web basada en el contenido del PDF. Debe ser atractiva y resumir los puntos clave."
        user_prompt = f"Necesito una descripción para el meta tag 'description' de una página web, que debe ser corta y concisa. Esta descripción ayudará a mejorar el SEO y no será visible directamente para los usuarios. Debe resumir los puntos clave de este contenido: {self.summary}. Respondeme en el mismo idioma que este mensaje."

        return self.call_ollama(user_prompt, system_prompt)

    def create_keywords(self):
        """ Genera las palabras clave utilizando Ollama. """
        system_prompt = "Genera una lista de 10 palabras clave relevantes para SEO basadas en el contenido del PDF. Las palabras clave deben estar separadas por comas."
        user_prompt = f"Necesito una lista de 10 palabras clave que sean relevantes para SEO y estén basadas en este contenido: {self.summary}. Deben estar bien seleccionadas y separadas por comas. Respondeme en el mismo idioma que este mensaje."
        keywords = self.call_ollama(user_prompt, system_prompt)
        return keywords.split(", ")

    def create_default_message(self):
        """ Genera el mensaje predeterminado utilizando Ollama. """
        system_prompt = "Genera un mensaje predeterminado que se mostrará a los usuarios en la página web para explicar el propósito del contenido o del chat interactivo."
        user_prompt = f"Quiero crear un chat donde se hablará sobre el siguiente resumen o contenido: {self.summary}. Necesito un texto corto y conciso para que, al entrar al chat, las personas sepan sobre qué tema o propósito es el chat. El chat es por mensaje. Respondeme en el mismo idioma que este mensaje."

        return self.call_ollama(user_prompt, system_prompt)

    def create_list_items(self):
        """ Genera los elementos de la lista utilizando Ollama basados en URLs encontradas en el resumen. """
        system_prompt = "Genera una lista de elementos con texto y URL basados en las URLs presentes en el resumen. " \
                        "El formato esperado es [{text: 'texto que ve el usuario', url: 'url'}]. recuerda que text debe ser corto y conciso (maximo 3 palabras). " \
                        "Si no hay URLs en el resumen, no devuelvas nada."
                        
        user_prompt = f"Resumen: {self.summary}. Por favor, utiliza solo las URLs que están en el texto. Respondeme en el mismo idioma que este mensaje."

        # Llamada a Ollama
        response_text = self.call_ollama(user_prompt, system_prompt)

        return response_text
        
    def generate_json(self):
        # Recolectar respuestas individuales
        title_response = self.create_title()
        header_response = self.create_header()
        description_response = self.create_description()
        keywords_response = self.create_keywords()
        default_message_response = self.create_default_message()
        list_items_response = self.create_list_items()
        try:
        # Concatenar todas las respuestas para enviar a Ollama
            concatenated_responses = f"Title: {title_response}\nHeader: {header_response}\nDescription: {description_response}\nKeywords: {keywords_response}\nDefault Message: {default_message_response}\nList Items: {list_items_response}"

            # Instrucciones para Ollama
            system_prompt = "Genera un JSON con la siguiente estructura, utilizando únicamente la información proporcionada. No agregues texto adicional ni saludos solo el JSON. El JSON debe contener las siguientes llaves con los tipos de datos esperados: 'title' (string), 'header' (string), 'description' (string), 'keywords' (lista de strings), 'default_message' (string), y 'list_items' (lista de objetos con 'text' y 'url', si no hay una url en el contenido list_items será una lista vacía, sin objetos). Cada llave debe contener solo la información relevante y directa del contexto proporcionado. No inventes información; utiliza únicamente los datos dados. Recuerda que cada llave, cada valor, cada item de cualquier lista debe ir con comillas dobles, asegurate de colocarlas bien en el JSON, no vayas a utilizar comillas simples y menos vayas a dejar las llaves y valores del json sin comillas ya que esto trae problemas al procesar las comillas."
            user_prompt = f"Tengo como trabajo crear un JSON a partir de un contexto dado. La estructura del JSON debe ser la siguiente: Debes incluir las siguientes llaves: 'title' que es un string breve y descriptivo, 'header' que es un string breve para la pestaña del navegador, 'description' que es un string para el meta tag description de SEO, 'keywords' que es una lista de strings relevantes para SEO, 'default_message' que es un string que introduce el propósito del chat en la página, y 'list_items' que es una lista de objetos donde cada item tiene las llaves 'text' y 'url', si no hay una url en el contenido list_items debe ser una lista vacía. Asegúrate de que cada parte del contenido corresponda a la llave adecuada del JSON: {concatenated_responses}. Utiliza solo la información proporcionada y asegúrate de que el formato sea estrictamente JSON, para ello debes usar comillas dobles al declarar las llaves, los valores. Las llaves o campos del JSON siempre deben estar en ingles, pero los valores del contenido deben estar en el mismo idioma que este mensaje."

            # Llamada final a Ollama para generar el JSON
            final_json = self.call_ollama(user_prompt, system_prompt)
            # convertir a JSON
            #final_json = json.loads(final_json)
            return str(final_json)
        except Exception as e:
            print('generate_jsos',f"Error: {e}")
            return None
