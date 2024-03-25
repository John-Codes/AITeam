# gunicorn.conf.py

# Tiempo de espera antes de que se finalice un worker si no se recibe una respuesta
timeout = 900 # 2 minutos de tiempo de espera

# Tiempo máximo para permitir conexiones pendientes al apagar workers
graceful_timeout = 120  # 30 segundos de tiempo de espera para conexiones pendientes

# Configuración de los workers
workers = 8 # Número de workers que manejarán las solicitudes

# Resto de la configuración de Gunicorn...
#gunicorn -c gunicorn.conf.py tu_proyecto_django.wsgi:application
