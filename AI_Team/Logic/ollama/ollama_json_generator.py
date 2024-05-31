import ollama
from django.utils.translation import gettext as _

class jsonPageDescriptionOllama:
    def __init__(self, summary):
        self.summary = summary

    def call_ollama(self, user_prompt, system_prompt):
        """ Central method to call the Ollama API. """
        try:
            ollama_response = ollama.chat(
                
                model='llama3', 
                messages=[
                    {'role': 'system', 'content': _(f"Always respond clearly, concisely, briefly, and simply. Answer plainly to the user's instruction, avoid long answers and unnecessary suggestions.\n {system_prompt}")},
                    {'role': 'user', 'content': user_prompt}
                ]
            )
            return ollama_response['message']['content']
        except Exception as e:
            print(e)
            print("Error calling Ollama. Please try again.")
    
    def create_title(self):
        """ Generates the title using Ollama. """
        system_prompt = _("Generate a title for a web page based on the PDF summary. The title should be catchy, concise, and reflect the main theme of the content. It should not be too long and a maximum of 3 words.")
        user_prompt = _("I need a catchy and concise title for a web page that reflects the main theme of this summary: %(summary)s. It should be brief. Respond in the same language as this message.") % {'summary': self.summary}
        return self.call_ollama(user_prompt, system_prompt)

    def create_header(self):
        """ Generates the title header using Ollama. """
        system_prompt = _("Generate a content for a html title tag based on the content that the user gives. The title should be informative and concise, ideal for display in the browser tab, so it should be a maximum of 5 words.")
        user_prompt = _("I need a header for the browser tab that is brief and captures the essence of this content: %(summary)s. It should be sufficiently informative but concise, ideal for display in the browser tab, so it should be a maximum of 5 words. Respond in the same language as this message.") % {'summary': self.summary}
        
        return self.call_ollama(user_prompt, system_prompt)

    def create_description(self):
        """ Generates the description using Ollama. """
        system_prompt = _("Generate an SEO meta description for a web page based on the content that the user gives. It should be attractive and summarize the key points. It should not be too long and a maximum of 160 characters.")
        user_prompt = _("I need a description for the 'description' meta tag of a web page, which should be short and concise between 150 and 160 characters. This description will help improve SEO and will not be directly visible to users. It should summarize the key points of this content: %(summary)s. Respond in the same language as this message.") % {'summary': self.summary}
        
        return self.call_ollama(user_prompt, system_prompt)

    def create_keywords(self):
        """ Generates the keywords using Ollama. """
        system_prompt = _("Generate a list of 10 relevant SEO keywords based on the PDF content. The keywords should be separated by commas.")
        user_prompt = _("I need a list of 10 keywords that are relevant for SEO and based on this content: %(summary)s. They should be well-selected and separated by commas. Respond in the same language as this message.") % {'summary': self.summary}
        keywords = self.call_ollama(user_prompt, system_prompt)
        return keywords

    def create_default_message(self):
        """ Generates the default message using Ollama. """
        system_prompt = _("Generate a default message to be displayed to users on the web page to explain the purpose of the content or the interactive chat.")
        user_prompt = _("I want to create a chat where the following summary or content will be discussed: %(summary)s. I need a short and concise text so that, upon entering the chat, people know what the topic or purpose of the chat is. The chat is by message. Respond in the same language as this message.") % {'summary': self.summary}
        
        return self.call_ollama(user_prompt, system_prompt)

    def create_list_items(self):
        """ Generates the list items using Ollama based on URLs found in the summary. """
        system_prompt = _("Generate a list of items with text and URL based on the URLs present in the summary. " \
                        "The expected format is [{text: 'text seen by the user', url: 'url'}]. remember that text should be short and concise (maximum 3 words). " \
                        "If there are no URLs in the summary, return a list of empty strings.")
        user_prompt = _("Summary: %(summary)s. Please use only the URLs that are in the text, and generate a list of items with text and URL. IF there are no URLs in the summary, return a list of empty strings. Respond in the same language as this message.") % {'summary': self.summary}
        
        # Call to Ollama
        response_text = self.call_ollama(user_prompt, system_prompt)
        
        return response_text
        
    def generate_json(self):
        # Collect individual responses
        title_response = self.create_title()
        header_response = self.create_header()
        description_response = self.create_description()
        keywords_response = self.create_keywords()
        default_message_response = self.create_default_message()
        list_items_response = self.create_list_items()
        try:
        # Concatenate all responses to send to Ollama
            concatenated_responses = f"Title: {title_response}\nHeader: {header_response}\nDescription: {description_response}\nKeywords: {keywords_response}\nDefault Message: {default_message_response}\nList Items: {list_items_response}"

            # Instructions for Ollama
            system_prompt = _("Generate a JSON with the following structure, using only the provided information. Do not add additional text or greetings, only the JSON. The JSON should contain the following keys with the expected data types: 'title' (string), 'header' (string), 'description' (string), 'keywords' (list of strings), 'default_message' (string), and 'list_items' (list of objects with 'text' and 'url', if there is no url in the content list_items will be an empty list, without objects). Each key should contain only the relevant and direct information from the provided context. Do not invent information; use only the given data. Remember that each key, each value, each item of any list must go with double quotes, make sure to place them well in the JSON, do not use single quotes and less leave the keys and values of the json without quotes as this brings problems when processing the quotes.")
            user_prompt = _("My task is to create a JSON from a given context. The structure of the JSON should be as follows: You must include the following keys: 'title' which is a brief and descriptive string, 'header' which is a brief string for the browser tab, 'description' which is a string for the SEO meta tag description, 'keywords' which is a list of relevant SEO strings, 'default_message' which is a string that introduces the purpose of the chat on the page, and 'list_items' which is a list of objects where each item has the keys 'text' and 'url', or an empty list if there are no URLs. Make sure that each part of the content corresponds to the appropriate key of the JSON: %(concatenated_responses)s. Use only the provided information and ensure that the format is strictly JSON, for this you must use double quotes when declaring the keys, the values. The keys or fields of the JSON should always be in English, but the content values should be in the same language as this message.") % {'concatenated_responses': concatenated_responses}

            # Final call to Ollama to generate the JSON
            final_json = self.call_ollama(user_prompt, system_prompt)

            return str(final_json)
        except Exception as e:
            print('generate_json',f"Error: {e}")
            return None