"""
WSGI config for landingpage project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

# Imprimir la ruta del sistema actual para ver dónde se está ejecutando
#print("Ruta del sistema actual:", sys.path)

# Añadir 'AI_Team' a la ruta del sistema y verificar
sys.path.append('AI_Team')
#print("Ruta del sistema después de agregar 'AI_Team':", sys.path)

# Imprimir el directorio actual para verificar desde dónde se está ejecutando
#print("Directorio actual:", os.getcwd())

# Verificar el valor de DJANGO_SETTINGS_MODULE
#print("Valor de DJANGO_SETTINGS_MODULE antes de establecer:", os.environ.get("DJANGO_SETTINGS_MODULE"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_Team.Server_Config.settings")

# Verificar el valor de DJANGO_SETTINGS_MODULE después de establecer
#print("Valor de DJANGO_SETTINGS_MODULE después de establecer:", os.environ.get("DJANGO_SETTINGS_MODULE"))

from django.core.wsgi import get_wsgi_application

# Si hay un error al obtener la aplicación WSGI, imprimirá un error antes de fallar
try:
    application = get_wsgi_application()
    #print("Aplicación WSGI creada exitosamente.")
except Exception as e:
    print("Error al crear la aplicación WSGI:", str(e))
