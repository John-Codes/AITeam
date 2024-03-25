FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y curl

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Copia el script de entrada al contenedor
COPY entrypoint.sh /app/

# Hace el script de entrada ejecutable
RUN chmod +x /app/entrypoint.sh

# Configura el script de entrada como el punto de entrada
ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 8000

# Source .env file
CMD ["gunicorn", "-c", "gunicorn.conf.py", "AI_Team.Server_Config.wsgi:application",  "--bind", "0.0.0.0:8000"]