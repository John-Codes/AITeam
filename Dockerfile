FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y curl

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Instalar el modelo Mistral
RUN curl http://localhost:11434/api/generate -d '{"model": "mistral"}'

EXPOSE 8000

# Copy .env file
COPY .env /app/

# Source .env file
CMD ["sh", "-c", "source /app/.env && gunicorn AI_Team.Server_Config.wsgi:application --bind 0.0.0.0:8000"]