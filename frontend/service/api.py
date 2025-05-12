# frontend/services/api.py
import os
import sys
import requests


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fe_pages')))

CUSTOMER_API_URL = "http://localhost:5000/api/customers"
INTERACT_API_URL = "http://localhost:5000/api/interactions"


def get_customers():
    res = requests.get(CUSTOMER_API_URL)
    return res.json()

def get_customer_name(id):
    res = requests.get(f"{CUSTOMER_API_URL}/{id}")
        
    if not res.ok:
        return False, None
    
    data = res.json()
    return True, data['name']

def get_customer(id):
    res = requests.get(f"{CUSTOMER_API_URL}/{id}")
        
    if not res.ok:
        return None
    data = res.json()
    return data

def create_customer(data):
    res = requests.post(CUSTOMER_API_URL, json=data)
    return res.status_code == 200 or res.status_code == 201

def update_customer(id, data):
    res = requests.put(f"{CUSTOMER_API_URL}/{id}", json=data)
    return res.status_code == 200 or res.status_code == 201

def delete_customer(id):
    res = requests.delete(f"{CUSTOMER_API_URL}/{id}")
    return res.status_code == 200 or res.status_code == 201

def get_interaction():
    res = requests.get(INTERACT_API_URL)
    return res.json()

def get_metrics_from_api():
    try:
        response = requests.get("http://localhost:5000/api/dashboard-metrics")
        if response.status_code == 200:
            metrics = response.json() 
            print(metrics)
            return metrics
        else:
            return {}
    except Exception as e:
        return {}

def check_email_exists(email_to_check):
        
    data = get_customers()
    
    for customer in data:
        if 'email' in customer and str(customer['email']).lower() == email_to_check.lower():
            return True, customer
    
    return False, None