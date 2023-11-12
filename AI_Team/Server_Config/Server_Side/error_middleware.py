# middleware.py
import datetime
import json
from django.http import JsonResponse
from AI_Team.Logic.sender_mails import notice_error_forms# Asegúrate de importar correctamente tu función

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # Captura la excepción y prepara los datos del error
        error_time = datetime.datetime.now()
        error_data = {
            "error": str(exception),
            "url": request.path,
            "method": request.method,
            "time": error_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        # Intentar obtener el ID del usuario si está autenticado
        user = getattr(request, 'user', None)
        if user:
            error_data["user_id"] = user.username
        if request.method == 'POST':
            try:
                error_data["post_data"] = json.loads(request.body)
            except json.JSONDecodeError:
                error_data["post_data"] = request.POST

        # Enviar error por correo electrónico
        notice_error_forms(error_data)

        # Puedes decidir qué hacer a continuación: 
        # Mostrar una página de error o devolver una respuesta JSON
        return JsonResponse({"error": "internal server error"}, status=500)
