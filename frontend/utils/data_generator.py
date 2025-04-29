import pandas as pd
import random
from datetime import datetime, timedelta

def generate_customer_data(n=100):
    data = {
        'Customer ID': [f"CUST{str(i).zfill(4)}" for i in range(n)],
        'Name': [f"Customer {i}" for i in range(n)],
        'Type': random.choices(['VIP', 'Regular', 'New'], k=n),
        'Email': [f"customer{i}@example.com" for i in range(n)],
        'Joined Date': [(datetime.now() - timedelta(days=random.randint(0, 1000))).strftime('%Y-%m-%d') for _ in range(n)]
    }
    return pd.DataFrame(data)

def generate_interaction_data(n=100):
    data = {
        'Interaction ID': [f"INT{str(i).zfill(4)}" for i in range(n)],
        'Customer': [f"Customer {random.randint(0, 99)}" for _ in range(n)],
        'Type': random.choices(['Email', 'Call', 'Meeting'], k=n),
        'Date': [(datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%Y-%m-%d') for _ in range(n)]
    }
    return pd.DataFrame(data)
