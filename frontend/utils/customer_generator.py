import pandas as pd
import random
from datetime import datetime, timedelta

def generate_customer_data():
    customer_types = ['VIP', 'Regular', 'New']
    customers = []

    for i in range(100):
        customer_id = f"CUST-{i+1}"
        name = f"Customer {i+1}"
        email = f"customer{i+1}@example.com"
        phone = f"+1234567890{i+1}"
        customer_type = random.choice(customer_types)
        created_at = datetime.now() - timedelta(days=random.randint(0, 365))
        
        customers.append({
            "Customer ID": customer_id,
            "Name": name,
            "Email": email,
            "Phone": phone,
            "Type": customer_type,
            "Created At": created_at
        })

    return pd.DataFrame(customers)

def generate_interaction_data():
    interaction_types = ['Email', 'Call', 'Meeting']
    interactions = []

    for i in range(200):
        interaction_id = f"INT-{i+1}"
        customer_id = f"CUST-{random.randint(1, 100)}"
        interaction_type = random.choice(interaction_types)
        date = datetime.now() - timedelta(days=random.randint(0, 30))
        notes = f"Interaction {i+1}: {interaction_type} with customer"
        
        interactions.append({
            "Interaction ID": interaction_id,
            "Customer ID": customer_id,
            "Type": interaction_type,
            "Date": date,
            "Notes": notes
        })

    return pd.DataFrame(interactions)