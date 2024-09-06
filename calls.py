import requests
import json
from qbClient import AuthClient
import urllib.parse

# Ruta al archivo de texto plano
file_path = 'config.txt'

# Función para cargar las variables de un archivo de texto plano
def load_variables_from_txt(file_path):
    variables = {}
    with open(file_path, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                variables[key] = value
    return variables

# Cargar las variables desde el archivo .txt
variables = load_variables_from_txt(file_path)

# Obtener los valores de las variables de entorno desde el diccionario
client_secrets = {
    "client_id": variables.get("CLIENT_ID"),
    "client_secret": variables.get("CLIENT_SECRET"),
    "redirect_uri": variables.get("REDIRECT_URI"),
    "environment": variables.get("ENVIRONMENT")
}

realmId = variables.get('REALM_ID')
authCode = variables.get('AUTH_CODE')

#print("Client Secrets = ",client_secrets)
auth_client = AuthClient(**client_secrets)
com_id = realmId
base_url = 'https://quickbooks.api.intuit.com/v3/company/'


def getCustomerData(accessToken):
    #making Request
    base_url = 'https://quickbooks.api.intuit.com'
    url = '{0}/v3/company/{1}/companyinfo/{1}'.format(base_url, realmId)
    auth_header = 'Bearer {0}'.format(accessToken)
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)

    print("Response = ",response)
    #print("Response Data = ",response.text)

    print("Success")

import os

def refresh_token():
    refreshToken = variables.get('REFRESH_TOKEN')  # Usamos el diccionario cargado desde el archivo .txt
    response = auth_client.refresh(refresh_token=refreshToken)
    
    # Leer el archivo y cargar las líneas
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Actualizar las líneas correspondientes a ACCESS_TOKEN y REFRESH_TOKEN
    with open(file_path, 'w') as file:
        for line in lines:
            if line.startswith('ACCESS_TOKEN='):
                file.write(f'ACCESS_TOKEN={response["access_token"]}\n')
            elif line.startswith('REFRESH_TOKEN='):
                file.write(f'REFRESH_TOKEN={response["refresh_token"]}\n')
            else:
                file.write(line)

    print("Tokens actualizados en el archivo config.txt.")

    # Actualizar el diccionario `variables` para reflejar los nuevos valores
    variables['ACCESS_TOKEN'] = response["access_token"]
    variables['REFRESH_TOKEN'] = response["refresh_token"]

    return response, variables['ACCESS_TOKEN']

# Suponiendo que ya has cargado las variables usando el método anterior


def getVendorByName(accessToken, name):
    
    encoded_name = urllib.parse.quote(name)
    
    # Construir la URL base y los encabezados de autenticación
    auth_header = f'Bearer {accessToken}'
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    vendor = False
    
    endpoint = f"{base_url}{com_id}/query?query=select * from vendor where DisplayName='{encoded_name}'&minorversion=73"
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'QueryResponse' in data and 'Vendor' in data['QueryResponse']:
            vendor = data['QueryResponse']['Vendor'][0]
        else:
            print("No vendor found.")
            
    else:
        print(f"Error fetching vendors: {response.status_code}, {response.text}")
    
    return vendor

def getAccountByName(accessToken, name):
    
    encoded_name = urllib.parse.quote(name)
    
    # Construir la URL base y los encabezados de autenticación
    auth_header = f'Bearer {accessToken}'
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    account = False
    
    endpoint = f"{base_url}{com_id}/query?query=select * from account where FullyQualifiedName='{encoded_name}'&minorversion=73"
    response = requests.get(endpoint, headers=headers)
    
    # Manejar la respuesta
    if response.status_code == 200:
        data = response.json()
        if 'QueryResponse' in data and 'Account' in data['QueryResponse']:
            account = data['QueryResponse']['Account'][0]
        else:
            print("No more accounts found.")
    else:
        print(f"Error fetching accounts: {response.status_code}, {response.text}")

    return account


def getCustomerByName(accessToken, name):
    
    encoded_name = urllib.parse.quote(name)
    
    # Construir la URL base y los encabezados de autenticación
    auth_header = f'Bearer {accessToken}'
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    customer = False
    
    endpoint = f"{base_url}{com_id}/query?query=select * from customer where DisplayName='{encoded_name}'&minorversion=73"
    response = requests.get(endpoint, headers=headers)
    
    # Manejar la respuesta
    if response.status_code == 200:
        data = response.json()
        if 'QueryResponse' in data and 'Customer' in data['QueryResponse']:
            customer = data['QueryResponse']['Customer'][0]
        else:
            print("No customers found.")
    else:
        print(f"Error fetching customers: {response.status_code}, {response.text}")

    return customer

def getClassByName(accessToken, name):
    
    encoded_name = urllib.parse.quote(name)
    
    # Construir la URL base y los encabezados de autenticación
    auth_header = f'Bearer {accessToken}'
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    clas = False
    
    endpoint = f"{base_url}{com_id}/query?query=select * from class where FullyQualifiedName='{encoded_name}'&minorversion=73"
    response = requests.get(endpoint, headers=headers)
    
    # Manejar la respuesta
    if response.status_code == 200:
        data = response.json()
        if 'QueryResponse' in data and 'Class' in data['QueryResponse']:
            clas = data['QueryResponse']['Class'][0]
        else:
            print("No classes found.")
    else:
        print(f"Error fetching classes: {response.status_code}, {response.text}")

    return clas

def getAllClasses(accessToken):
    # Construir la URL base y los encabezados de autenticación
    auth_header = f'Bearer {accessToken}'
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Endpoint para obtener las órdenes de compra (ejemplo)
    company_id = com_id  # Reemplaza con el ID de tu compañía en QuickBooks
    endpoint = f'{base_url}{company_id}/query?query=select count(*) from class&minorversion=73'

    # Realizar la solicitud GET
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        count_data = response.json()
        total_count = count_data['QueryResponse']['totalCount']
    else:
        print(f"Error getting count: {response.status_code}, {response.text}")
        return

    # Paso 2: Obtener vendors en chunks
    page_size = 1000  # Ajusta el tamaño de página según tus necesidades
    start_position = 1
    classes = []

    while start_position <= total_count:
        endpoint = f'{base_url}{company_id}/query?query=select * from class startposition {start_position} maxresults {page_size}&minorversion=73'
        response = requests.get(endpoint, headers=headers)

        # Manejar la respuesta
        if response.status_code == 200:
            data = response.json()
            if 'QueryResponse' in data and 'Class' in data['QueryResponse']:
                chunk_classes = data['QueryResponse']['Class']
                classes.extend(chunk_classes)
                start_position += page_size
            else:
                print("No more classes found.")
                break
        else:
            print(f"Error fetching classes: {response.status_code}, {response.text}")
            break

    if classes:
        for classe in classes:
            print(f"\nID: {classe.get('Id')}, Name: {classe.get('Name')}")
            pass
    else:
        print("No classes found.")

    return classes

def createPurchaseOrder(accessToken, json_data, log_window):
    # Construir la URL base y los encabezados de autenticación
    auth_header = f'Bearer {accessToken}'
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Endpoint para crear una orden de compra
    company_id = com_id  # Reemplaza con el ID de tu compañía en QuickBooks
    endpoint = f'{base_url}{company_id}/purchaseorder'

    # Convertir los datos a formato JSON
    json_data = json.dumps(json_data)

    # Realizar la solicitud POST
    response = requests.post(endpoint, headers=headers, data=json_data)

    # Manejar la respuesta
    if response.status_code == 200:
        data = response.json()
        if 'PurchaseOrder' in data:
            purchase_order = data['PurchaseOrder']
            print("Purchase Order created successfully:")
            print(f"ID: {purchase_order.get('Id')}, DocNumber: {purchase_order.get('DocNumber')}\n")
            
            return True, purchase_order
        else:
            print("No Purchase Order found in response.")
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return False, response