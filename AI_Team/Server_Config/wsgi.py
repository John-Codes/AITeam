"""
WSGI config for landingpage project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys




from django.core.wsgi import get_wsgi_application

# Si hay un error al obtener la aplicación WSGI, imprimirá un error antes de fallar
try:
    application = get_wsgi_application()
    #print("Aplicación WSGI creada exitosamente.")
except Exception as e:
    print("Error al crear la aplicación WSGI:", str(e))
