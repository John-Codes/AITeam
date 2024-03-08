import os


def process_temporary_files(request):
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