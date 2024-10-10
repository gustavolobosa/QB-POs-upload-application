#read a cdsv file and return a list of dictionaries
import pandas as pd
from calls import getAccountByName, getVendorByName, getCustomerByName, getClassByName, createPurchaseOrder
from mapping import project_accounts
from logger import log_message

# TODO: crear ejecutable auto-py-to-exe
# TODO: fix mail_vendor
# TODO: agregar fucnionalidad con variables de ambiente

def map_vendor_id(vendor_name, accessToken, log_window):
    
    vendor = getVendorByName(accessToken, vendor_name)
    
    if vendor:
        log_message(log_window, f"Vendor ID:  {vendor['Id']}, Vendor Name: {vendor['DisplayName']}\n")
        # log_message(log_window, f"Vendor ID:  {vendor['Id']}, Vendor Name: {vendor['DisplayName']}, Vendor Email: {vendor['PrimaryEmailAddr']['Address']}\n")
        return vendor['Id'] #, vendor['PrimaryEmailAddr']['Address']

    log_message(log_window, f"{vendor_name} Vendor not found, this PO will not be processed\n", 'red')
    return None

def map_category_id(category_name, accessToken, log_window):
    
    category = getAccountByName(accessToken, category_name)
    
    if category:
        log_message(log_window, f"Category ID:  {category['Id']}, Category Name: {category['Name']}")
        return category['Id']
        
    log_message(log_window, f"{category_name} Category not found, this PO will not be processed", 'red')
    return None

def map_customer_id(customer_name, accessToken, log_window):
    
    customer = getCustomerByName(accessToken, customer_name)
    
    if customer:
        log_message(log_window, f"Customer ID: {customer['Id']}, Customer Name: {customer['DisplayName']}")
        return customer['Id']
        
    log_message(log_window, f"{customer_name} Customer not found, this PO will not be processed", 'red')
    return None

def map_class_id(primary_class, accessToken, log_window):
        
    clas = getClassByName(accessToken, primary_class)
    
    if clas:
        log_message(log_window, f"Class ID: {clas['Id']}, Class Name: {clas['FullyQualifiedName']}\n")
        return clas['Id']
            
    log_message(log_window, f"{primary_class} Class not found, this PO will not be processed \n", 'red')
    return None

def create_category_lines(accessToken, amount, description, categories, class_id, log_window):

    lines = []
    
    log_message(log_window, f"Creating lines for categories:\n")
    lines_number = len(categories)
    for cat in categories:
        cat = cat.strip()
        cat_id = map_category_id(cat, accessToken, log_window)
        if cat in project_accounts:
            customer_id = map_customer_id(project_accounts[cat], accessToken, log_window)
        
        elif "Work In Progress BESS" in cat:
            customer_id = map_customer_id("02.01.02.07 Pagos Storage", accessToken, log_window)
        
        elif "Work In Progress DEV" in cat:
            customer_id = map_customer_id("02.01.02.06 Pagos Desarrollo", accessToken, log_window)
            
        else:
            log_message(log_window, f"{cat} category not found in proyects accounts, wrong mapping, this PO will not be processed \n", 'red')
            return False

        lines.append({
                    "Amount": amount/lines_number,
                    "DetailType": "AccountBasedExpenseLineDetail",
                    "Description": description,
                    "AccountBasedExpenseLineDetail": {
                        "AccountRef": {
                            "value": f'{cat_id}'
                        },
                        "CustomerRef": {
                            "value": f'{customer_id}'
                        },
                        "ClassRef": {
                            "value": f'{class_id}'
                        }
                    }
                },)
        
        if cat_id is None:
            return False
        
        if customer_id is None:
            return False
        
      
    return lines

def createPO(accessToken, nums, ruta, log_window):
    
    print("Reading file...")
    df = pd.read_csv(ruta)
    processed = []
    processed_check = []
    
    for index, fila in df.iterrows():
        
        Purchase_order_dict = fila.to_dict()

        if str(Purchase_order_dict['ID']) in nums and Purchase_order_dict['Approval State'] == 'Approved':
            log_message(log_window, f"\nPO number {Purchase_order_dict['ID']} processing\n", 'blue')
            
            #Vendor
            vendor = Purchase_order_dict['Vendor'].strip()
            id_vendor = map_vendor_id(vendor, accessToken, log_window)
            
            if id_vendor is None:
                continue

            #Amount
            total_amt = float(Purchase_order_dict['Total PO Amt'].replace('$','').replace(',',''))

            #descripcion
            description = Purchase_order_dict['Memo/Description']
            
            #class
            class_id = map_class_id(Purchase_order_dict['Budget Category'].strip(), accessToken, log_window)
            if class_id is None:
                continue
            
            #Proyect
            categories = Purchase_order_dict['Project'].split(',')
            
            if id_vendor is None:
                log_message(log_window, f"Vendor {Purchase_order_dict['Vendor']} does not exist in QuickBooks")
            
            elif class_id is None:
                log_message(log_window, f"Class {Purchase_order_dict['Budget Category']} does not exist in QuickBooks")
            
            else:                
                category_lines = create_category_lines(accessToken, total_amt, description, categories, class_id, log_window)
                
                if category_lines is False:
                    log_message(log_window, f"PO {Purchase_order_dict['ID']} will not be processed\n", 'red')
                    continue

                purchase_order_data = {
                    "Line": category_lines,
                    "VendorRef": {
                        "value": f'{id_vendor}'
                    },
                     "ShipAddr": {
                        "Id": "3112",
                        "Line1": "Grenergy USA LLC",
                        "Line2": " US"
                    },
                    # "VendorEmail": {
                    #     "value": f"{mail_vendor}"
                    # },
                    "Memo": 'Please send all invoices to USADMIN@GRENERGY.EU',
                }
                
                created, data = createPurchaseOrder(accessToken, purchase_order_data, log_window)
                                
                if created:
                    log_message(log_window, f"\nPO {Purchase_order_dict['ID']} created successfully with number: {data.get('DocNumber')} \n", 'green')
                    processed.append([Purchase_order_dict['ID'], data.get('DocNumber')])
                    processed_check.append(str(Purchase_order_dict['ID']))
                else:
                    log_message(log_window, f"PO {Purchase_order_dict['ID']} could not be created\nError: {data.status_code}, {data.text}", 'red')
            
        elif Purchase_order_dict['ID'] in nums and Purchase_order_dict['Approval State'] != 'Approved':
            log_message(log_window, f"PO {Purchase_order_dict['ID']} is not approved\n", 'red')
    
    # print all POs with their ID and number created
    for num in processed:
        log_message(log_window, f"PO {num[0]} created with number {num[1]}", 'green')
             
    if len(processed_check) < len(nums):
        log_message(log_window, f"\nPOs not processed:\n", 'red')
        print("check")
        print(processed_check)
        print("nums")
        print(nums)
        for num in nums:
            if num not in processed_check:
                log_message(log_window, f"- {num}", 'red')
                
    else:
        log_message(log_window, f"\nAll POs processed successfully\n", 'green')
                