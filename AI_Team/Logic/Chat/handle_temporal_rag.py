from ..ollama.ollama_rag_Module import OllamaRag
def process_temp_context_chat(request, crhoma_client):
    if request.session.get('temp_collection_exist', False):
        try:
            print(request.session.get('temp_collection_exist', False))
            collection_name = request.session['temp_collection_exist']['temp_uuid']
            OllamaRag.delete_collection(collection_name, crhoma_client)
            
            del request.session['temp_collection_exist']
        except Exception as e:
            print(e)