#!/usr/bin/env python3
"""
Load mock data into Dgraph
"""
import json
import requests
import time

def load_dgraph_data():
    """Load mock data into Dgraph"""
    try:
        # Wait for Dgraph to be ready
        print("Waiting for Dgraph to be ready...")
        time.sleep(15)
        
        # Set schema
        schema = """
        vendor: string @index(exact) @index(term) .
        service: string @index(exact) @index(term) .
        location: string @index(exact) @index(term) .
        contract_start_date: datetime @index(year) .
        contract_expiry_date: datetime @index(year) .
        category: string @index(exact) @index(term) .
        city: string @index(exact) @index(term) .
        country_code: string @index(exact) @index(term) .
        postal_code: string @index(exact) @index(term) .
        embedding: string .
        """
        
        print("Setting Dgraph schema...")
        response = requests.post('http://localhost:8080/admin/schema', data=schema)
        if response.status_code == 200:
            print("Schema set successfully")
        else:
            print(f"Schema setting failed: {response.status_code}")
            return
        
        # Load mock data
        with open('dgraph_mock_data.json', 'r') as f:
            data = json.load(f)
        
        print("Loading mock data into Dgraph...")
        response = requests.post('http://localhost:8080/mutate?commitNow=true', 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            print("Mock data loaded successfully!")
        else:
            print(f"Data loading failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error loading Dgraph data: {e}")

if __name__ == "__main__":
    load_dgraph_data()

