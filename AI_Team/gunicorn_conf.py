import os
from distutils.util import strtobool

# in prod async server:
#Doesnt stream...
# gunicorn -c gunicorn_conf.py Server_Config.asgi:application --worker-class uvicorn.workers.UvicornWorker

# For streaming responses with long inference times
# worker_class = 'uvicorn.workers.UvicornWorker'

#sync mode:
#streams
#gunicorn -c gunicorn_conf.py Server_Config.wsgi:application

#print new line
print('_______________________________')
print('guni conf opened')
#print in green color settings.py set Server_Config.settings.py'
print('\033[92m' + 'settings.py set Server_Config.settings.py' + '\033[0m')
# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ['DJANGO_SETTINGS_MODULE'] = 'Server_Config.settings'


# Continue with your Gunicorn configuration...

# command =  '/miniconda3/envs/AIteam/bin/gunicorn'
pythonpath ='/AITeam/AI_Team'
#bind = '137.184.129.216:8000'
# bind ='0.0.0.0:8000'
bind = "127.0.0.1:8000"
# gunicorn_conf.py

workers = 2
threads = 1
worker_connections = 100

# Timeout settings
timeout = 900  # 15 minutes
keepalive = 900
graceful_timeout = 900  # 15 minutes

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Prevent buffering in workers
bufsize = 0
# Explicitly disable response buffering
sendfile = False

# Worker lifecycle management
max_requests = 100
max_requests_jitter = 10

# Limit server backlog
backlog = 50



print('_______________________________')
print('guni conf ran to the end')