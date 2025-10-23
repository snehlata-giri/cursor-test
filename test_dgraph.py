#!/usr/bin/env python3
"""
Test Dgraph connection and create sample data
"""
import requests
import json
import time

def test_dgraph():
    """Test Dgraph connection and create sample data"""
    
    # Wait for Dgraph to be ready
    print("Waiting for Dgraph to be ready...")
    for i in range(30):
        try:
            response = requests.get('http://localhost:8080/health', timeout=5)
            if response.status_code == 200:
                print("✅ Dgraph is ready!")
                break
        except:
            pass
        print(f"Attempt {i+1}/30...")
        time.sleep(2)
    else:
        print("❌ Dgraph is not ready")
        return False
    
    # Set schema
    schema = """
    name: string @index(fulltext) .
    email: string @index(exact) .
    rating: float @index(float) .
    service_name: string @index(fulltext) .
    category: string @index(exact) .
    city: string @index(exact) .
    """
    
    try:
        response = requests.post('http://localhost:8080/admin/schema', data=schema)
        print(f"Schema response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Schema set successfully")
        else:
            print(f"❌ Schema failed: {response.text}")
    except Exception as e:
        print(f"❌ Schema error: {e}")
    
    # Create sample data
    data = {
        "set": [
            {
                "uid": "_:vendor1",
                "name": "TechCorp Solutions",
                "email": "contact@techcorp.com",
                "rating": 4.7,
                "service_name": "Cloud Infrastructure",
                "category": "Technology",
                "city": "San Francisco"
            },
            {
                "uid": "_:vendor2", 
                "name": "DataFlow Systems",
                "email": "info@dataflow.com",
                "rating": 5.0,
                "service_name": "Data Analytics",
                "category": "Analytics",
                "city": "Austin"
            }
        ]
    }
    
    try:
        response = requests.post(
            'http://localhost:8080/mutate?commitNow=true',
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Data response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Data loaded successfully")
            print(f"Response: {response.text}")
        else:
            print(f"❌ Data loading failed: {response.text}")
    except Exception as e:
        print(f"❌ Data error: {e}")
    
    # Test query
    query = """
    {
        vendors(func: has(name)) {
            name
            email
            rating
            service_name
            category
            city
        }
    }
    """
    
    try:
        response = requests.post(
            'http://localhost:8080/query',
            json={'query': query},
            headers={'Content-Type': 'application/json'}
        )
        print(f"Query response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Query successful")
            print(f"Results: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Query failed: {response.text}")
    except Exception as e:
        print(f"❌ Query error: {e}")
    
    return False

if __name__ == "__main__":
    test_dgraph()
