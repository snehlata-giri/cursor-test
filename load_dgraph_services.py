#!/usr/bin/env python3
"""
Load service data into Dgraph
"""

import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DGRAPH_ALPHA_URL = 'http://localhost:8080'

def wait_for_dgraph():
    """Wait for Dgraph to be ready"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(f'{DGRAPH_ALPHA_URL}/health', timeout=5)
            if response.status_code == 200:
                logger.info("Dgraph is ready!")
                return True
        except:
            pass
        logger.info(f"Waiting for Dgraph... attempt {attempt + 1}/{max_attempts}")
        time.sleep(2)
    logger.error("Dgraph is not ready. Exiting.")
    return False

def set_schema():
    """Set the Dgraph schema"""
    logger.info("Setting Dgraph schema...")
    schema = """
    # Vendor properties
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

    # Location properties
    address: string @index(fulltext) .
    city: string @index(exact) .
    state: string @index(exact) .
    country: string @index(exact) .
    country_code: string @index(exact) .
    postal_code: string @index(exact) .
    latitude: float @index(float) .
    longitude: float @index(float) .
    is_primary: bool .

    # Service properties
    service_name: string @index(fulltext) .
    category: string @index(exact) .
    service_description: string @index(fulltext) .
    is_active: bool .

    # Relationships
    has_locations: [uid] @reverse(belongs_to_vendor) .
    provides_services: [uid] @reverse(provided_by_vendor) .
    belongs_to_vendor: uid @reverse(has_locations) .
    provided_by_vendor: uid @reverse(provides_services) .
    embedding: string .
    """

    try:
        response = requests.post(f'{DGRAPH_ALPHA_URL}/admin/schema', data=schema)
        if response.status_code == 200:
            logger.info("Schema set successfully")
            return True
        else:
            logger.error(f"Schema setting failed: {response.status_code}")
            logger.error(response.text)
            return False
    except Exception as e:
        logger.error(f"Error setting Dgraph schema: {e}")
        return False

def create_service_data():
    """Create comprehensive service data for Dgraph"""
    data = {
        "set": [
            # TechCorp Solutions with services
            {
                "uid": "_:vendor1",
                "dgraph.type": "Vendor",
                "vendor_id": "vendor_001",
                "name": "TechCorp Solutions",
                "email": "contact@techcorp.com",
                "phone": "+1-555-1000",
                "website": "https://www.techcorp.com",
                "rating": 4.7,
                "established_year": 2018,
                "description": "Leading provider of technology services with excellent customer satisfaction.",
                "contract_start_date": "2023-01-01T00:00:00Z",
                "contract_expiry_date": "2025-12-31T00:00:00Z",
                "has_locations": [
                    {
                        "uid": "_:location1",
                        "dgraph.type": "Location",
                        "address": "123 Tech Ave",
                        "city": "San Francisco",
                        "state": "CA",
                        "country": "USA",
                        "country_code": "US",
                        "postal_code": "94105",
                        "latitude": 37.7749,
                        "longitude": -122.4194,
                        "is_primary": True
                    }
                ],
                "provides_services": [
                    {
                        "uid": "_:service1",
                        "dgraph.type": "Service",
                        "service_name": "Cloud Infrastructure",
                        "category": "Technology",
                        "service_description": "Scalable cloud computing resources and infrastructure management.",
                        "is_active": True
                    },
                    {
                        "uid": "_:service2",
                        "dgraph.type": "Service",
                        "service_name": "Data Analytics",
                        "category": "Analytics",
                        "service_description": "Advanced data processing, analysis, and business intelligence solutions.",
                        "is_active": True
                    },
                    {
                        "uid": "_:service3",
                        "dgraph.type": "Service",
                        "service_name": "Security Services",
                        "category": "Security",
                        "service_description": "Comprehensive cybersecurity and data protection services.",
                        "is_active": True
                    }
                ]
            },
            # DataFlow Systems with services
            {
                "uid": "_:vendor2",
                "dgraph.type": "Vendor",
                "vendor_id": "vendor_002",
                "name": "DataFlow Systems",
                "email": "info@dataflow.com",
                "phone": "+1-555-0500",
                "website": "https://www.dataflow.com",
                "rating": 5.0,
                "established_year": 2015,
                "description": "Specializing in data management and business intelligence solutions.",
                "contract_start_date": "2022-06-01T00:00:00Z",
                "contract_expiry_date": "2024-05-31T00:00:00Z",
                "has_locations": [
                    {
                        "uid": "_:location2",
                        "dgraph.type": "Location",
                        "address": "456 Data Blvd",
                        "city": "Austin",
                        "state": "TX",
                        "country": "USA",
                        "country_code": "US",
                        "postal_code": "78701",
                        "latitude": 30.2672,
                        "longitude": -97.7431,
                        "is_primary": True
                    }
                ],
                "provides_services": [
                    {
                        "uid": "_:service4",
                        "dgraph.type": "Service",
                        "service_name": "Data Analytics",
                        "category": "Analytics",
                        "service_description": "Comprehensive data analysis, reporting, and visualization services.",
                        "is_active": True
                    },
                    {
                        "uid": "_:service5",
                        "dgraph.type": "Service",
                        "service_name": "Managed IT Services",
                        "category": "Technology",
                        "service_description": "Full-suite IT support, maintenance, and management solutions.",
                        "is_active": True
                    }
                ]
            },
            # CloudMaster Inc with services
            {
                "uid": "_:vendor3",
                "dgraph.type": "Vendor",
                "vendor_id": "vendor_003",
                "name": "CloudMaster Inc",
                "email": "hello@cloudmaster.com",
                "phone": "+1-555-0300",
                "website": "https://www.cloudmaster.com",
                "rating": 4.5,
                "established_year": 2022,
                "description": "Cloud-first solutions provider with cutting-edge technology.",
                "contract_start_date": "2023-03-01T00:00:00Z",
                "contract_expiry_date": "2026-02-28T00:00:00Z",
                "has_locations": [
                    {
                        "uid": "_:location3",
                        "dgraph.type": "Location",
                        "address": "789 Cloud Street",
                        "city": "Seattle",
                        "state": "WA",
                        "country": "USA",
                        "country_code": "US",
                        "postal_code": "98101",
                        "latitude": 47.6062,
                        "longitude": -122.3321,
                        "is_primary": True
                    }
                ],
                "provides_services": [
                    {
                        "uid": "_:service6",
                        "dgraph.type": "Service",
                        "service_name": "Cloud Infrastructure",
                        "category": "Technology",
                        "service_description": "Enterprise-grade cloud infrastructure and migration services.",
                        "is_active": True
                    },
                    {
                        "uid": "_:service7",
                        "dgraph.type": "Service",
                        "service_name": "Security Services",
                        "category": "Security",
                        "service_description": "Advanced security monitoring and threat protection.",
                        "is_active": True
                    }
                ]
            },
            # SecureNet Pro with services
            {
                "uid": "_:vendor4",
                "dgraph.type": "Vendor",
                "vendor_id": "vendor_004",
                "name": "SecureNet Pro",
                "email": "security@securenet.com",
                "phone": "+1-555-0900",
                "website": "https://www.securenet.com",
                "rating": 4.9,
                "established_year": 2023,
                "description": "Cybersecurity specialists with 24/7 monitoring and response.",
                "contract_start_date": "2023-07-01T00:00:00Z",
                "contract_expiry_date": "2025-06-30T00:00:00Z",
                "has_locations": [
                    {
                        "uid": "_:location4",
                        "dgraph.type": "Location",
                        "address": "321 Security Plaza",
                        "city": "New York",
                        "state": "NY",
                        "country": "USA",
                        "country_code": "US",
                        "postal_code": "10001",
                        "latitude": 40.7505,
                        "longitude": -73.9934,
                        "is_primary": True
                    }
                ],
                "provides_services": [
                    {
                        "uid": "_:service8",
                        "dgraph.type": "Service",
                        "service_name": "Security Services",
                        "category": "Security",
                        "service_description": "Comprehensive cybersecurity services including monitoring, incident response, and compliance.",
                        "is_active": True
                    },
                    {
                        "uid": "_:service9",
                        "dgraph.type": "Service",
                        "service_name": "Cloud Infrastructure",
                        "category": "Technology",
                        "service_description": "Secure cloud infrastructure with built-in security controls.",
                        "is_active": True
                    }
                ]
            },
            # Analytics Plus with services
            {
                "uid": "_:vendor5",
                "dgraph.type": "Vendor",
                "vendor_id": "vendor_005",
                "name": "Analytics Plus",
                "email": "analytics@analyticsplus.com",
                "phone": "+1-555-0200",
                "website": "https://www.analyticsplus.com",
                "rating": 4.7,
                "established_year": 2018,
                "description": "Data science and analytics experts delivering actionable insights.",
                "contract_start_date": "2023-02-01T00:00:00Z",
                "contract_expiry_date": "2025-01-31T00:00:00Z",
                "has_locations": [
                    {
                        "uid": "_:location5",
                        "dgraph.type": "Location",
                        "address": "654 Analytics Way",
                        "city": "Boston",
                        "state": "MA",
                        "country": "USA",
                        "country_code": "US",
                        "postal_code": "02101",
                        "latitude": 42.3601,
                        "longitude": -71.0589,
                        "is_primary": True
                    }
                ],
                "provides_services": [
                    {
                        "uid": "_:service10",
                        "dgraph.type": "Service",
                        "service_name": "Data Analytics",
                        "category": "Analytics",
                        "service_description": "Advanced analytics, machine learning, and predictive modeling services.",
                        "is_active": True
                    },
                    {
                        "uid": "_:service11",
                        "dgraph.type": "Service",
                        "service_name": "Machine Learning",
                        "category": "AI/ML",
                        "service_description": "Custom machine learning models and AI solutions for business optimization.",
                        "is_active": True
                    }
                ]
            }
        ]
    }
    return data

def load_data():
    """Load data into Dgraph"""
    try:
        data = create_service_data()

        response = requests.post(
            f'{DGRAPH_ALPHA_URL}/mutate?commitNow=true',
            json=data,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            logger.info("Service data loaded successfully")
            logger.info(f"Dgraph UIDs: {response.json().get('uids')}")
            return True
        else:
            logger.error(f"Data loading failed: {response.status_code}")
            logger.error(response.text)
            return False
    except Exception as e:
        logger.error(f"Error loading Dgraph data: {e}")
        return False

def test_query():
    """Test a service query to verify data"""
    logger.info("Testing Dgraph service query...")
    query = """
    {
      services(func: has(service_name)) {
        service_name
        category
        service_description
        is_active
        provided_by_vendor {
          name
          rating
          email
          has_locations {
            city
            state
          }
        }
      }
    }
    """

    try:
        response = requests.post(
            f'{DGRAPH_ALPHA_URL}/query',
            json={'query': query},
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            logger.info("Service query successful")
            result = response.json()
            services = result.get('data', {}).get('services', [])
            logger.info(f"Found {len(services)} services")
            for service in services[:3]:  # Show first 3 services
                logger.info(f"- {service.get('service_name')} ({service.get('category')}) by {service.get('provided_by_vendor', {}).get('name', 'Unknown')}")
            return True
        else:
            logger.error(f"Query failed: {response.status_code}")
            logger.error(response.text)
            return False
    except Exception as e:
        logger.error(f"Error testing Dgraph query: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting Dgraph service data loading...")
    if wait_for_dgraph():
        if set_schema():
            if load_data():
                test_query()
    logger.info("Dgraph service data loading process finished.")

