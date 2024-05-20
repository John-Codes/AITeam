from .pdf_handling import delete_temp_pdfs
def process_temp_context_chat(request):
    if request.session.get('temp_rag_exist', False):
        try:
            print(request.session.get('temp_rag_exist', False))
            delete_temp_pdfs(request.session['temp_rag_exist']['pdf_path'])
            del request.session['temp_rag_exist']
        except Exception as e:
            print(e)