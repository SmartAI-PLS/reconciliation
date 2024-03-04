import json
import time
import streamlit as st
from difflib import get_close_matches

similarity_threshold = 0.5

def reconsile(extracted_data):
    metadata = None
    data = None

    with open('reconciliation_metadata.json', 'r') as f:
        metadata = json.load(f)
    with open(extracted_data, 'r') as f:
        data = json.load(f)
    
    CompanyIdentifier = str(data['CompanyName']+'-'+data['Address'])

    if CompanyIdentifier in metadata['CompaniesIdentifier']:
        # print('Company Name matched')
        pass
    else:
        # print('Company Name not matched')
        metadata['CompaniesIdentifier'] = list(metadata['CompaniesIdentifier'])
        metadata['CompaniesIdentifier'].append(CompanyIdentifier)
        with open('reconciliation_metadata.json', 'w') as f:
            json.dump(metadata, f)
        create_table(CompanyIdentifier)
    operator = 1
    if data['Type'] == "Invoice":
        operator = -1
    for product in data['Products']:
        product['Quantity'] = operator * product['Quantity']
        product['Price'] = operator * product['Price']
    data['Total'] = operator * data['Total']
    # print(data)
    with open(CompanyIdentifier+".json", 'r') as f:
        table = json.load(f)
        # print(table)
    table['ReconciliationStatus']["Descrepencies"] = dict(table['ReconciliationStatus']["Descrepencies"])
    for product in data['Products']:
        match_list = get_close_matches(product['Description'], table['DescriptionSet'], 1, similarity_threshold)
        print(match_list)
        if len(match_list) > 0:
            product['Description'] = match_list[0]
        if product['Description'] not in table['DescriptionSet']:
            table['DescriptionSet'].append(product['Description'])
            table['ReconciliationStatus']["Descrepencies"][product['Description']] = [product['Quantity'], product['Price'], product["IsMilestone"]]
            # print(table['ReconciliationStatus']["Descrepencies"])
        else:
            table['ReconciliationStatus']["Descrepencies"][product['Description']][0] += product['Quantity']
            table['ReconciliationStatus']["Descrepencies"][product['Description']][1] += product['Price']
    table['ReconciliationStatus']["Total"] += data['Total']
    # print(table)
    table = dict(table)
    with open(CompanyIdentifier+".json", 'w') as f:
        json.dump(table, f)
        

def create_table(CompaniesIdentifier):
    CompaniesIdentifier+=".json"
    with open('temptable.json', 'r') as f:
        table = json.load(f)
    table['CompaniesIdentifier'] = CompaniesIdentifier
    with open(CompaniesIdentifier, 'w') as f:
        json.dump(table, f)

def validate_invoice(extracted_data):
    with open(extracted_data, 'r') as f:
        data = json.load(f)

    if data["Type"] == "PurchaseOrder":
        return 1
    
    CompanyIdentifier = str(data['CompanyName']+'-'+data['Address'])
    
    with open('reconciliation_metadata.json', 'r') as f:
        metadata = json.load(f)

    if not CompanyIdentifier in metadata['CompaniesIdentifier']:
        return -1
    
    with open(CompanyIdentifier+".json", 'r') as f:
        table = json.load(f)

    for product in data['Products']:
        match_list = get_close_matches(product['Description'], table['DescriptionSet'], 1, similarity_threshold)
        if len(match_list) == 0:
            return -2
        else:
            product['Description'] = match_list[0]
    for product in data['Products']:
        if product['Quantity'] > table['ReconciliationStatus']["Descrepencies"][product['Description']][0]:
            return -3
        elif product['Price'] > table['ReconciliationStatus']["Descrepencies"][product['Description']][1]:
            return -4
    return 1
            
def pipe_line(extracted_data):
    validaion_status = validate_invoice(extracted_data)
    if validaion_status == 1:
        reconsile(extracted_data)
    elif validaion_status == -1:
        st.error('Company not registered')
    elif validaion_status == -2:
        st.error('Product not registered')
    elif validaion_status == -3:
        st.error('Quantity not valid')
    elif validaion_status == -4:
        st.error('Price not valid')
        
# print(validate_invoice('extracted_data1.json'))
# reconsile('extracted_data1.json')
# reconsile('extracted_data2.json')
# reconsile('extracted_data3.json')
# reconsile('extracted_data4.json')
# for i in range(1, 5):
#     pipe_line('extracted_data'+str(i)+'.json')
#     time.sleep(10)