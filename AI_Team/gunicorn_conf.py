import os
from distutils.util import strtobool

#print new line
print('_______________________________')
print('guni conf opened')
# command =  '/miniconda3/envs/AIteam/bin/gunicorn'
pythonpath ='/AITeam/AI_Team'
#bind = '137.184.129.216:8000'
# bind ='0.0.0.0:8000'
bind = "127.0.0.1:8000"
# gunicorn_conf.py

# For streaming responses with long inference times
worker_class = 'uvicorn.workers.UvicornWorker'
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