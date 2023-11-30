import runpod
import json
import requests
import sys
import os
# Configura tu API key de RunPod
api_key = os.getenv("RUNPOD_API_KEY")
runpod.api_key = api_key
api_url = "https://api.runpod.io/graphql"
# Función para iniciar un pod
def start_pod(id_gpu, nombre, template_id):
    nombre = 'aiteam_endpoint'
    template_id = "xkhgg72fuo"
    try:
        query = f"""mutation {{ saveEndpoint(input: {{ gpuIds: "{id_gpu}", name: "{nombre}", templateId: "{template_id}" }})
          {{ gpuIds id idleTimeout locations name scalerType scalerValue templateId workersMax workersMin }} }}"""
        data = {'query': query}
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
        response = requests.post(api_url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print("Response:", response.text)
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

# Función para detener un pod
def stop_pod(id_servidor):
    try:
        query = f'mutation {{ deleteEndpoint(id: "{id_servidor}") }}'
        data = {'query': query}
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
        response = requests.post(api_url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print("Response:", response.text)
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None


def view_servers():
    try:
        query = 'query Endpoints { myself { endpoints { gpuIds id idleTimeout locations name networkVolumeId pods { desiredStatus } scalerType scalerValue templateId workersMax workersMin } serverlessDiscount { discountFactor type expirationDate } } }'
        data = {'query': query}
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
        response = requests.post(api_url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print("Response:", response.text)
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

    
# Main script
# Ejemplo de uso de las funciones
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python script.py <ACCIÓN> <ID_GPU>")
        sys.exit(1)

    accion = sys.argv[1]
    id_gpu = sys.argv[2]

    if accion == "crear":
        nombre_servidor = "Nuevo Servidor"
        template_id = "xkhgg72fuo"
        resultado_creacion = start_pod(id_gpu, nombre_servidor, template_id)
        print("Resultado de la creación del servidor:", resultado_creacion)
    elif accion == "ver":
        resultado_ver_servidores = view_servers()
        print("Tus servidores:", resultado_ver_servidores)
    elif accion == "eliminar":
        resultado_eliminacion = stop_pod(id_gpu)
        print("Resultado de la eliminación del servidor:", resultado_eliminacion)
    else:
        print("Acción no válida. Las acciones válidas son 'crear', 'ver' y 'eliminar'.")