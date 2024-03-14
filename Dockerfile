# slim version is missing things to auto run ollama as a process
#FROM python:3.9.18-slim 
#FROM ollama/ollama cant start because it clashes with local ollama server.

FROM ubuntu:20.04



# Update the package lists and install packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*
# Set environment variables
ENV PORT 8000
ENV PYTHONUNBUFFERED=1


# Verify Python version
#RUN python --version

# Set up the working directory
WORKDIR /app

# Install curl
RUN apt-get update && apt-get install -y curl

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh
RUN ollama --version
# Copy the requirements file and install dependencies
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django application code
COPY . .

# Expose port 8000
EXPOSE $PORT

# Define the command to run the Django server
#CMD ["gunicorn", "AI_Team.Server_Config.wsgi:application", "--bind", "0.0.0.0:8000"]
FROM ubuntu:latest

# Update the package lists and install packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PORT 8000
ENV PYTHONUNBUFFERED=1

# Set up the working directory
WORKDIR /app

# Install curl
RUN apt-get update && apt-get install -y curl

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh
RUN ollama --version

# Start Ollama server as a process
CMD ["ollama", "serve"]
