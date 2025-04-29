# frontend/services/api.py
import requests

BASE_URL = "http://localhost:5000"

def get_customers():
    res = requests.get(f"{BASE_URL}/customers")
    return res.json()

def create_customer(data):
    res = requests.post(f"{BASE_URL}/customers", json=data)
    return res.status_code == 200 or res.status_code == 201
