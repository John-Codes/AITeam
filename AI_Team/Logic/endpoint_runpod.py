import os
import requests
def save_endpoint():
    # Obtener las variables de entorno
    print('creamos endpoint en runpod')
    api_key = os.getenv("RUNPOD_API_KEY")
    template_id = os.getenv("runpod_template_id")
    network_volume_id = os.getenv("runpod_network_volume_id")

    # URL y headers
    url = "https://api.runpod.io/graphql?api_key=" + api_key
    headers = {"content-type": "application/json"}

    # Datos para el cuerpo de la petición
    data = {
        "query": """
            mutation {
                saveEndpoint(input: {
                    gpuIds: "AMPERE_16",
                    idleTimeout: 5,
                    locations: "US",
                    name: "chat_test",
                    networkVolumeId: "%s",
                    scalerType: "QUEUE_DELAY",
                    scalerValue: 4,
                    templateId: "%s",
                    workersMax: 2,
                    workersMin: 0
                }) {
                    gpuIds id idleTimeout locations name scalerType scalerValue templateId workersMax workersMin
                }
            }
        """ % (network_volume_id, template_id)
    }

    # Realizar la petición POST
    response = requests.post(url, headers=headers, json=data)
    print('relizamos el request', response)
    print(response.json())
    # Devolver la respuesta
    return response.json()

def modify_endpoint(endpoint_id):
    api_key = os.getenv("RUNPOD_API_KEY")
    template_id = os.getenv("TEMPLATE_ID")

    url = f"https://api.runpod.io/graphql?api_key={api_key}"
    headers = {"content-type": "application/json"}
    data = {
        "query": f"""
            mutation {{
                saveEndpoint(input: {{
                    id: "{endpoint_id}",
                    gpuIds: "AMPERE_16",
                    name: "Generated Endpoint -fb",
                    templateId: "{template_id}",
                    workersMax: 0
                }}) {{
                    id gpuIds name templateId workersMax
                }}
            }}
        """
    }

    try:
        print('intentamos modificar el endpoint')
        response = requests.post(url, headers=headers, json=data)
        #response.raise_for_status()
        print(response.json())
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error: {err}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def delete_endpoint(endpoint_id):
    api_key = os.getenv("RUNPOD_API_KEY")
    endpoint_modified = modify_endpoint(endpoint_id)
    if endpoint_modified:
        url = f"https://api.runpod.io/graphql?api_key={api_key}"
        headers = {"content-type": "application/json"}
        data = {
            "query": f"""
                mutation {{
                    deleteEndpoint(id: "{endpoint_id}")
                }}
            """
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error: {err}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Failed to modify endpoint.")

def runpod_post_query(endpoint_id, prompt):
    api_key = os.getenv("RUNPOD_API_KEY")
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'input': {
            'Prompt': prompt,
            'SetModelName': None,
            'TokenCount': 2000,
            'Train': False,
            'DataSet': None
        }
    }

    response = requests.post(url, headers=headers, json=data)
    data = response.json()
    print(data)
    job_id = data.get('id')
    return job_id

def runpod_get_status(endpoint_id, job_id):
    api_key = os.getenv("RUNPOD_API_KEY")
    url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    estatus = 'IN_QUEUE'
    while estatus != 'COMPLETED':
        response = requests.get(url, headers=headers)
        data = response.json()
        estatus = data.get('status')
    ia_response = data.get('output')
    print(ia_response)
    return ia_response