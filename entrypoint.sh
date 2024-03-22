#!/bin/bash

# Cambia al directorio donde se encuentra el archivo .env
cd /app
# Carga las variables de entorno del archivo .env
while read -r line; do
    if [[ ! -z "$line" && "$line" != \#* ]]; then
        export "$line"
    fi
done < /app/.env

cd AI_Team
# Ejecuta collectstatic
python manage.py collectstatic --noinput

cd ..
# Ejecuta el comando CMD o ENTRYPOINT definido en el Dockerfile
exec "$@"
