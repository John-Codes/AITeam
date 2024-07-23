# middleware.py
import datetime
import json
import traceback
from django.http import JsonResponse
from Logic.sender_mails import notice_error_forms# Asegúrate de importar correctamente tu función

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)
        print("Response: ", response)
        return response

    def process_exception(self, request, exception):
        # Captura la excepción y prepara los datos del error
        error_time = datetime.datetime.now()
        error_traceback = traceback.format_exc()  # Obtener la traza de la excepción

        # Formatear los datos del error
        error_message = (
            f"Time: {error_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"URL: {request.path}\n"
            f"Method: {request.method}\n"
            f"Error: {str(exception)}\n"
            f"Traceback:\n{error_traceback}\n"
        )

        # Intentar obtener el ID del usuario si está autenticado
        user = getattr(request, 'user', None)
        try:
            email_contact = user.email
        except:
            email_contact= "user no authenticate"
        # Datos del POST si el método es POST
        if request.method == 'POST':
            post_data = request.POST if request.POST else request.body
            error_message += f"Post Data: {post_data}\n"

        # Enviar error por correo electrónico
        notice_error_forms(error_message, email_contact, request.path)


        # Puedes decidir qué hacer a continuación: 
        # Mostrar una página de error o devolver una respuesta JSON
        #return JsonResponse({"error": "internal server error", "traceback": error_traceback}, status=500)
