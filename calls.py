import requests
import json
from qbClient import AuthClient
from dotenv import load_dotenv
import urllib.parse
import os

# Ruta al archivo de texto plano
file_path = '.env'

load_dotenv(dotenv_path=file_path)

client_secrets = {
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "redirect_uri": os.getenv("REDIRECT_URI"),
    "environment": os.getenv("ENVIRONMENT")
}

realmId = os.getenv('REALM_ID')
authCode = os.getenv('AUTH_CODE')

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

    print("Response = ", response)

    print("Success")

import os

def refresh_token():
    # refreshToken = variables.get('REFRESH_TOKEN')  # Usamos el diccionario cargado desde el archivo .txt
    refreshToken = os.getenv('REFRESH_TOKEN')
    response = auth_client.refresh(refresh_token=refreshToken)
    
    os.environ['ACCESS_TOKEN'] = response["access_token"]
    os.environ['REFRESH_TOKEN'] = response["refresh_token"]
    
    with open(file_path, 'w') as env_file:
        env_file.write(f"CLIENT_ID={os.getenv('CLIENT_ID')}\n")
        env_file.write(f"CLIENT_SECRET={os.getenv('CLIENT_SECRET')}\n")
        env_file.write(f"REDIRECT_URI={os.getenv('REDIRECT_URI')}\n")
        env_file.write(f"ENVIRONMENT={os.getenv('ENVIRONMENT')}\n")
        env_file.write(f"REALM_ID={os.getenv('REALM_ID')}\n")
        env_file.write(f"AUTH_CODE={os.getenv('AUTH_CODE')}\n")
        env_file.write(f"ACCESS_TOKEN={response['access_token']}\n")
        env_file.write(f"REFRESH_TOKEN={response['refresh_token']}\n")


    return response, os.getenv('ACCESS_TOKEN')

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
    
    print_all(accessToken)
    
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
    
    auth_header = f'Bearer {accessToken}'
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    customer = False
    
    endpoint = f"{base_url}{com_id}/query?query=select * from customer where DisplayName='{encoded_name}'&minorversion=73"
    response = requests.get(endpoint, headers=headers)
    
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
    
    auth_header = f'Bearer {accessToken}'
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    clas = False
    
    endpoint = f"{base_url}{com_id}/query?query=select * from class where FullyQualifiedName='{encoded_name}'&minorversion=73"
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'QueryResponse' in data and 'Class' in data['QueryResponse']:
            clas = data['QueryResponse']['Class'][0]
        else:
            print("No classes found.")
    else:
        print(f"Error fetching classes: {response.status_code}, {response.text}")

    return clas

def print_all(accessToken):
    
    auth_header = f'Bearer {accessToken}'
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Endpoint para obtener las órdenes de compra (ejemplo)
    company_id = com_id  # Reemplaza con el ID de tu compañía en QuickBooks
    
    endpoint = f'{base_url}{company_id}/query?query=select count(*) from account&minorversion=73'
    response = requests.get(endpoint, headers=headers)

    # Realizar la solicitud GET

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
        endpoint = f'{base_url}{company_id}/query?query=select * from account startposition {start_position} maxresults {page_size}&minorversion=73'
        response = requests.get(endpoint, headers=headers)

        # Manejar la respuesta
        if response.status_code == 200:
            data = response.json()
            if 'QueryResponse' in data and 'Account' in data['QueryResponse']:
                chunk_classes = data['QueryResponse']['Account']
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
            #print(f"\nID: {classe.get('Id')}, Name= '{classe.get('FullyQualifiedName')}'")
            pass
    else:
        print("No classes found.")

def getAllClasses(accessToken):

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