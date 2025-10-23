#!/usr/bin/env python3
"""
Complete Dgraph data loading script with vendors, services, and locations
"""
import json
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_dgraph():
    """Wait for Dgraph to be ready"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://localhost:8081/health', timeout=5)
            if response.status_code == 200:
                logger.info("Dgraph is ready!")
                return True
        except:
            pass
        logger.info(f"Waiting for Dgraph... attempt {attempt + 1}/{max_attempts}")
        time.sleep(2)
    return False

def set_schema():
    """Set Dgraph schema"""
    schema = """
    vendor_id: string @index(exact) .
    name: string @index(fulltext) .
    email: string @index(exact) .
    phone: string @index(exact) .
    website: string .
    rating: float @index(float) .
    established_year: int @index(int) .
    description: string @index(fulltext) .
    contract_start_date: datetime @index(datetime) .
    contract_expiry_date: datetime @index(datetime) .
    address: string @index(fulltext) .
    city: string @index(exact) .
    state: string @index(exact) .
    country: string @index(exact) .
    country_code: string @index(exact) .
    postal_code: string @index(exact) .
    latitude: float @index(float) .
    longitude: float @index(float) .
    is_primary: bool .
    service_name: string @index(fulltext) .
    category: string @index(exact) .
    service_description: string @index(fulltext) .
    is_active: bool .
    has_locations: [uid] @reverse(belongs_to_vendor) .
    provides_services: [uid] @reverse(provided_by_vendor) .
    belongs_to_vendor: uid @reverse(has_locations) .
    provided_by_vendor: uid @reverse(provides_services) .
    embedding: string .
    """
    
    try:
        response = requests.post('http://localhost:8081/admin/schema', data=schema)
        if response.status_code == 200:
            logger.info("Schema set successfully")
            return True
        else:
            logger.error(f"Schema setting failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error setting schema: {e}")
        return False

def create_comprehensive_data():
    """Create comprehensive vendor, service, and location data"""
    data = {
        "set": [
            # Vendor 1: TechCorp Solutions
            {
                "uid": "_:techcorp",
                "dgraph.type": "Vendor",
                "vendor_id": "vendor_001",
                "name": "TechCorp Solutions",
                "email": "contact@techcorp.com",
                "phone": "+1-555-1000",
                "website": "https://www.techcorp.com",
                "rating": 4.7,
                "established_year": 2018,
                "description": "Leading technology solutions provider specializing in cloud infrastructure and software development.",
                "contract_start_date": "2023-01-15T00:00:00Z",
                "contract_expiry_date": "2025-01-15T00:00:00Z"
            },
            {
                "uid": "_:techcorp_loc1",
                "dgraph.type": "Location",
                "address": "123 Tech Street, Suite 100",
                "city": "San Francisco",
                "state": "California",
                "country": "United States",
                "country_code": "US",
                "postal_code": "94105",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "is_primary": True,
                "belongs_to_vendor": "_:techcorp"
            },
            {
                "uid": "_:techcorp_service1",
                "dgraph.type": "Service",
                "service_name": "Cloud Infrastructure",
                "category": "Technology",
                "service_description": "Complete cloud infrastructure setup and management",
                "is_active": True,
                "provided_by_vendor": "_:techcorp"
            },
            {
                "uid": "_:techcorp_service2",
                "dgraph.type": "Service",
                "service_name": "Data Analytics",
                "category": "Analytics",
                "service_description": "Advanced data analytics and business intelligence",
                "is_active": True,
                "provided_by_vendor": "_:techcorp"
            },
            {
                "uid": "_:techcorp_service3",
                "dgraph.type": "Service",
                "service_name": "Security Services",
                "category": "Security",
                "service_description": "Cybersecurity and data protection services",
                "is_active": True,
                "provided_by_vendor": "_:techcorp"
            },
            
            # Vendor 2: DataFlow Systems
            {
                "uid": "_:dataflow",
                "dgraph.type": "Vendor",
                "vendor_id": "vendor_002",
                "name": "DataFlow Systems",
                "email": "info@dataflow.com",
                "phone": "+1-555-0500",
                "website": "https://www.dataflow.com",
                "rating": 5.0,
                "established_year": 2015,
                "description": "Data processing and analytics solutions for enterprise clients.",
                "contract_start_date": "2023-03-01T00:00:00Z",
                "contract_expiry_date": "2025-03-01T00:00:00Z"
            },
            {
                "uid": "_:dataflow_loc1",
                "dgraph.type": "Location",
                "address": "456 Data Drive",
                "city": "Austin",
                "state": "Texas",
                "country": "United States",
                "country_code": "US",
                "postal_code": "73301",
                "latitude": 30.2672,
                "longitude": -97.7431,
                "is_primary": True,
                "belongs_to_vendor": "_:dataflow"
            },
            {
                "uid": "_:dataflow_service1",
                "dgraph.type": "Service",
                "service_name": "Cloud Infrastructure",
                "category": "Technology",
                "service_description": "Scalable cloud infrastructure solutions",
                "is_active": True,
                "provided_by_vendor": "_:dataflow"
            },
            {
                "uid": "_:dataflow_service2",
                "dgraph.type": "Service",
                "service_name": "Data Analytics",
                "category": "Analytics",
                "service_description": "Real-time data processing and analytics",
                "is_active": True,
                "provided_by_vendor": "_:dataflow"
            },
            {
                "uid": "_:dataflow_service3",
                "dgraph.type": "Service",
                "service_name": "Security Services",
                "category": "Security",
                "service_description": "Data security and compliance solutions",
                "is_active": True,
                "provided_by_vendor": "_:dataflow"
            },
            
            # Vendor 3: CloudMaster Inc
            {
                "uid": "_:cloudmaster",
                "dgraph.type": "Vendor",
                "vendor_id": "vendor_003",
                "name": "CloudMaster Inc",
                "email": "hello@cloudmaster.com",
                "phone": "+1-555-0300",
                "website": "https://www.cloudmaster.com",
                "rating": 4.5,
                "established_year": 2022,
                "description": "Cloud computing and infrastructure management specialists.",
                "contract_start_date": "2023-06-01T00:00:00Z",
                "contract_expiry_date": "2025-06-01T00:00:00Z"
            },
            {
                "uid": "_:cloudmaster_loc1",
                "dgraph.type": "Location",
                "address": "789 Cloud Avenue",
                "city": "Seattle",
                "state": "Washington",
                "country": "United States",
                "country_code": "US",
                "postal_code": "98101",
                "latitude": 47.6062,
                "longitude": -122.3321,
                "is_primary": True,
                "belongs_to_vendor": "_:cloudmaster"
            },
            {
                "uid": "_:cloudmaster_service1",
                "dgraph.type": "Service",
                "service_name": "Cloud Infrastructure",
                "category": "Technology",
                "service_description": "Enterprise cloud infrastructure and migration",
                "is_active": True,
                "provided_by_vendor": "_:cloudmaster"
            },
            {
                "uid": "_:cloudmaster_service2",
                "dgraph.type": "Service",
                "service_name": "Data Analytics",
                "category": "Analytics",
                "service_description": "Cloud-based analytics and reporting",
                "is_active": True,
                "provided_by_vendor": "_:cloudmaster"
            },
            {
                "uid": "_:cloudmaster_service3",
                "dgraph.type": "Service",
                "service_name": "Security Services",
                "category": "Security",
                "service_description": "Cloud security and monitoring",
                "is_active": True,
                "provided_by_vendor": "_:cloudmaster"
            },
            
            # Vendor 4: SecureNet Pro
            {
                "uid": "_:securenet",
                "dgraph.type": "Vendor",
                "vendor_id": "vendor_004",
                "name": "SecureNet Pro",
                "email": "security@securenet.com",
                "phone": "+1-555-0900",
                "website": "https://www.securenet.com",
                "rating": 4.9,
                "established_year": 2023,
                "description": "Cybersecurity and network protection experts.",
                "contract_start_date": "2023-09-01T00:00:00Z",
                "contract_expiry_date": "2025-09-01T00:00:00Z"
            },
            {
                "uid": "_:securenet_loc1",
                "dgraph.type": "Location",
                "address": "321 Security Boulevard",
                "city": "New York",
                "state": "New York",
                "country": "United States",
                "country_code": "US",
                "postal_code": "10001",
                "latitude": 40.7589,
                "longitude": -73.9851,
                "is_primary": True,
                "belongs_to_vendor": "_:securenet"
            },
            {
                "uid": "_:securenet_service1",
                "dgraph.type": "Service",
                "service_name": "Security Services",
                "category": "Security",
                "service_description": "Advanced cybersecurity and threat protection",
                "is_active": True,
                "provided_by_vendor": "_:securenet"
            },
            {
                "uid": "_:securenet_service2",
                "dgraph.type": "Service",
                "service_name": "Cloud Infrastructure",
                "category": "Technology",
                "service_description": "Secure cloud infrastructure solutions",
                "is_active": True,
                "provided_by_vendor": "_:securenet"
            },
            
            # Vendor 5: Analytics Plus
            {
                "uid": "_:analyticsplus",
                "dgraph.type": "Vendor",
                "vendor_id": "vendor_005",
                "name": "Analytics Plus",
                "email": "analytics@analyticsplus.com",
                "phone": "+1-555-0200",
                "website": "https://www.analyticsplus.com",
                "rating": 4.7,
                "established_year": 2018,
                "description": "Business intelligence and data analytics solutions.",
                "contract_start_date": "2023-02-15T00:00:00Z",
                "contract_expiry_date": "2025-02-15T00:00:00Z"
            },
            {
                "uid": "_:analyticsplus_loc1",
                "dgraph.type": "Location",
                "address": "654 Analytics Lane",
                "city": "Boston",
                "state": "Massachusetts",
                "country": "United States",
                "country_code": "US",
                "postal_code": "02101",
                "latitude": 42.3601,
                "longitude": -71.0589,
                "is_primary": True,
                "belongs_to_vendor": "_:analyticsplus"
            },
            {
                "uid": "_:analyticsplus_service1",
                "dgraph.type": "Service",
                "service_name": "Data Analytics",
                "category": "Analytics",
                "service_description": "Advanced business intelligence and analytics",
                "is_active": True,
                "provided_by_vendor": "_:analyticsplus"
            },
            {
                "uid": "_:analyticsplus_service2",
                "dgraph.type": "Service",
                "service_name": "Cloud Infrastructure",
                "category": "Technology",
                "service_description": "Analytics-focused cloud infrastructure",
                "is_active": True,
                "provided_by_vendor": "_:analyticsplus"
            }
        ]
    }
    
    # Add relationships
    for item in data["set"]:
        if item.get("dgraph.type") == "Vendor":
            vendor_uid = item["uid"]
            # Find related locations and services
            locations = [loc["uid"] for loc in data["set"] if loc.get("belongs_to_vendor") == vendor_uid]
            services = [srv["uid"] for srv in data["set"] if srv.get("provided_by_vendor") == vendor_uid]
            
            if locations:
                item["has_locations"] = locations
            if services:
                item["provides_services"] = services
    
    return data

def load_data():
    """Load data into Dgraph"""
    try:
        data = create_comprehensive_data()
        
        response = requests.post(
            'http://localhost:8081/mutate?commitNow=true',
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            logger.info("Data loaded successfully!")
            logger.info(f"Response: {response.text}")
            return True
        else:
            logger.error(f"Data loading failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return False

def test_queries():
    """Test some queries to verify data is loaded"""
    queries = [
        {
            "name": "All Vendors",
            "query": """
            {
                vendors(func: has(name)) {
                    uid
                    name
                    email
                    rating
                    has_locations {
                        city
                        state
                        country
                    }
                    provides_services {
                        service_name
                        category
                    }
                }
            }
            """
        },
        {
            "name": "All Services",
            "query": """
            {
                services(func: has(service_name)) {
                    uid
                    service_name
                    category
                    provided_by_vendor {
                        name
                        rating
                    }
                }
            }
            """
        },
        {
            "name": "All Locations",
            "query": """
            {
                locations(func: has(city)) {
                    uid
                    city
                    state
                    country
                    belongs_to_vendor {
                        name
                        rating
                    }
                }
            }
            """
        }
    ]
    
    for query_info in queries:
        try:
            response = requests.post(
                'http://localhost:8081/query',
                json={'query': query_info['query']},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ {query_info['name']} query successful")
                logger.info(f"Results: {json.dumps(result, indent=2)}")
            else:
                logger.error(f"❌ {query_info['name']} query failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Error testing {query_info['name']}: {e}")

def main():
    """Main function"""
    logger.info("Starting Dgraph data loading...")
    
    # Wait for Dgraph to be ready
    if not wait_for_dgraph():
        logger.error("Dgraph is not ready. Exiting.")
        return
    
    # Set schema
    if not set_schema():
        logger.error("Failed to set schema. Exiting.")
        return
    
    # Load data
    if not load_data():
        logger.error("Failed to load data. Exiting.")
        return
    
    # Test queries
    logger.info("Testing queries...")
    test_queries()
    
    logger.info("Dgraph setup completed successfully!")

if __name__ == "__main__":
    main()
