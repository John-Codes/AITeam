"""
ASGI config for landingpage project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

try:

    application = get_asgi_application()

except Exception as e:
    #print error in asgi message  in red
    print(f"ASGI   \033[91m{e}\033[0m")



