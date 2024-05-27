import os
from ..response_utils import render_html
from ..Charge_Context import Charge_Context
from ..ollama.ollama_rag_Module import OllamaRag
#process_uploaded_files
o = OllamaRag()
def proccess_context_files(request, context):
    temp_file = proccess_temporary_files(request)
    return temp_file
    #if context == 'main':
    #    temp_file = proccess_temporary_files(request)
    #    return temp_file
    #elif context == 'panel-admin':
    #    rag_permanent = proccess_chat_creation_files(request)
    #    return rag_permanent

def proccess_chat_creation_files(request):
    #details = Charge_Context().process_uploaded_files(request)
    #print(details)
    try:
        pathpdf, message = proccess_temporary_files(request)
        user_email = request.user.email
        user_email = o.clean_string_for_file_name(user_email)
        # creación del rag con pdf
        text = o.extract_text_from_pdf(pathpdf)
        splits = o.semantic_text_split_bert(text,200)
        doc_splits = o.string_list_to_hf_documents(splits, pathpdf)
        doc_splits = o.text_spliter_for_vectordbs(doc_splits)
        
        #o.new_Persisted_Chroma_and_retriever(doc_splits)
        o.new_persisted_ChromaDb_all_mini(doc_splits,user_email)
    
        return 'no path', message   
    except Exception as e:
        return 'no path', str(e)
     
def proccess_temporary_files(request):
    # Get the list of uploaded files from the request
    uploaded_files = request.FILES.getlist('uploaded_files')
    # If no files were uploaded, return None for both paths and message
    if not uploaded_files:
        return None, None
    
    pdf_paths = []  # List to store the paths of the saved PDF files

    # Get the current directory path where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path for the temporary folder to store the PDF files
    parent_dir = os.path.dirname(current_dir)
    temp_pdfs_dir = os.path.join(parent_dir,'temporal_pdfs')

    try:
        # Check if the temporary folder exists, if not, create it
        if not os.path.exists(temp_pdfs_dir):
            os.makedirs(temp_pdfs_dir)
    except Exception as e:
        # If an error occurs while creating the temporary directory, return an error message
        error_message = f"An error occurred while creating the temporary directory: {str(e)}"
        return None, error_message

    for file in uploaded_files:
        if file.name.endswith('.pdf'):
            # Get the name of the file
            filename = file.name
            # Construct the full path to save the PDF file in the desired location
            file_path = os.path.join(temp_pdfs_dir, filename)
            try:
                # Save the file to the filesystem
                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
            except Exception as e:
                # If an error occurs while saving the PDF file, return an error message
                error_message = f"An error occurred while saving the PDF file: {str(e)}"
                return None, error_message
            # Add the path of the saved file to the list
            pdf_paths.append(file_path)
            
    
    # Success message
    success_message = "The PDF has been successfully uploaded. You can now ask questions about its content."

    # Return the paths of the saved PDF files and the success message
    return file_path, success_message

#eliminación de archivos temporales
def delete_temp_pdfs(temporal_file_to_delete):
    if os.path.exists(temporal_file_to_delete):
        os.remove(temporal_file_to_delete)