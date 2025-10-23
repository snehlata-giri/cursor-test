#!/usr/bin/env python3
"""
Fix Dgraph vendor-service relationships with proper data structure
"""

import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DGRAPH_ALPHA_URL = 'http://localhost:8080'

def clear_existing_data():
    """Clear existing data to start fresh"""
    logger.info("Clearing existing data...")
    
    # Delete all data
    delete_query = """
    {
        delete {
            <*> * * .
        }
    }
    """
    
    try:
        response = requests.post(
            f'{DGRAPH_ALPHA_URL}/mutate?commitNow=true',
            json={"delete": {"query": delete_query}},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            logger.info("Existing data cleared successfully")
            return True
        else:
            logger.error(f"Failed to clear data: {response.status_code}")
            logger.error(response.text)
            return False
    except Exception as e:
        logger.error(f"Error clearing data: {e}")
        return False

def create_proper_vendor_service_data():
    """Create data with proper vendor-service relationships"""
    logger.info("Creating proper vendor-service relationships...")
    
    data = {
        "set": [
            # TechCorp Solutions
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
                "description": "Leading provider of technology services with excellent customer satisfaction.",
                "contract_start_date": "2023-01-01T00:00:00Z",
                "contract_expiry_date": "2025-12-31T00:00:00Z",
                "has_locations": [
                    {
                        "uid": "_:techcorp_loc",
                        "dgraph.type": "Location",
                        "address": "123 Tech Ave",
                        "city": "San Francisco",
                        "state": "CA",
                        "country": "USA",
                        "country_code": "US",
                        "postal_code": "94105",
                        "latitude": 37.7749,
                        "longitude": -122.4194,
                        "is_primary": True,
                        "belongs_to_vendor": "_:techcorp"
                    }
                ],
                "provides_services": [
                    {
                        "uid": "_:techcorp_cloud",
                        "dgraph.type": "Service",
                        "service_name": "Cloud Infrastructure",
                        "category": "Technology",
                        "service_description": "Scalable cloud computing resources and infrastructure management.",
                        "is_active": True,
                        "provided_by_vendor": "_:techcorp"
                    },
                    {
                        "uid": "_:techcorp_analytics",
                        "dgraph.type": "Service",
                        "service_name": "Data Analytics",
                        "category": "Analytics",
                        "service_description": "Advanced data processing, analysis, and business intelligence solutions.",
                        "is_active": True,
                        "provided_by_vendor": "_:techcorp"
                    },
                    {
                        "uid": "_:techcorp_security",
                        "dgraph.type": "Service",
                        "service_name": "Security Services",
                        "category": "Security",
                        "service_description": "Comprehensive cybersecurity and data protection services.",
                        "is_active": True,
                        "provided_by_vendor": "_:techcorp"
                    }
                ]
            },
            # DataFlow Systems
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
                "description": "Specializing in data management and business intelligence solutions.",
                "contract_start_date": "2022-06-01T00:00:00Z",
                "contract_expiry_date": "2024-05-31T00:00:00Z",
                "has_locations": [
                    {
                        "uid": "_:dataflow_loc",
                        "dgraph.type": "Location",
                        "address": "456 Data Blvd",
                        "city": "Austin",
                        "state": "TX",
                        "country": "USA",
                        "country_code": "US",
                        "postal_code": "78701",
                        "latitude": 30.2672,
                        "longitude": -97.7431,
                        "is_primary": True,
                        "belongs_to_vendor": "_:dataflow"
                    }
                ],
                "provides_services": [
                    {
                        "uid": "_:dataflow_analytics",
                        "dgraph.type": "Service",
                        "service_name": "Data Analytics",
                        "category": "Analytics",
                        "service_description": "Comprehensive data analysis, reporting, and visualization services.",
                        "is_active": True,
                        "provided_by_vendor": "_:dataflow"
                    },
                    {
                        "uid": "_:dataflow_it",
                        "dgraph.type": "Service",
                        "service_name": "Managed IT Services",
                        "category": "Technology",
                        "service_description": "Full-suite IT support, maintenance, and management solutions.",
                        "is_active": True,
                        "provided_by_vendor": "_:dataflow"
                    }
                ]
            },
            # CloudMaster Inc
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
                "description": "Cloud-first solutions provider with cutting-edge technology.",
                "contract_start_date": "2023-03-01T00:00:00Z",
                "contract_expiry_date": "2026-02-28T00:00:00Z",
                "has_locations": [
                    {
                        "uid": "_:cloudmaster_loc",
                        "dgraph.type": "Location",
                        "address": "789 Cloud Street",
                        "city": "Seattle",
                        "state": "WA",
                        "country": "USA",
                        "country_code": "US",
                        "postal_code": "98101",
                        "latitude": 47.6062,
                        "longitude": -122.3321,
                        "is_primary": True,
                        "belongs_to_vendor": "_:cloudmaster"
                    }
                ],
                "provides_services": [
                    {
                        "uid": "_:cloudmaster_cloud",
                        "dgraph.type": "Service",
                        "service_name": "Cloud Infrastructure",
                        "category": "Technology",
                        "service_description": "Enterprise-grade cloud infrastructure and migration services.",
                        "is_active": True,
                        "provided_by_vendor": "_:cloudmaster"
                    },
                    {
                        "uid": "_:cloudmaster_security",
                        "dgraph.type": "Service",
                        "service_name": "Security Services",
                        "category": "Security",
                        "service_description": "Advanced security monitoring and threat protection.",
                        "is_active": True,
                        "provided_by_vendor": "_:cloudmaster"
                    }
                ]
            },
            # SecureNet Pro
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
                "description": "Cybersecurity specialists with 24/7 monitoring and response.",
                "contract_start_date": "2023-07-01T00:00:00Z",
                "contract_expiry_date": "2025-06-30T00:00:00Z",
                "has_locations": [
                    {
                        "uid": "_:securenet_loc",
                        "dgraph.type": "Location",
                        "address": "321 Security Plaza",
                        "city": "New York",
                        "state": "NY",
                        "country": "USA",
                        "country_code": "US",
                        "postal_code": "10001",
                        "latitude": 40.7505,
                        "longitude": -73.9934,
                        "is_primary": True,
                        "belongs_to_vendor": "_:securenet"
                    }
                ],
                "provides_services": [
                    {
                        "uid": "_:securenet_security",
                        "dgraph.type": "Service",
                        "service_name": "Security Services",
                        "category": "Security",
                        "service_description": "Comprehensive cybersecurity services including monitoring, incident response, and compliance.",
                        "is_active": True,
                        "provided_by_vendor": "_:securenet"
                    },
                    {
                        "uid": "_:securenet_cloud",
                        "dgraph.type": "Service",
                        "service_name": "Cloud Infrastructure",
                        "category": "Technology",
                        "service_description": "Secure cloud infrastructure with built-in security controls.",
                        "is_active": True,
                        "provided_by_vendor": "_:securenet"
                    }
                ]
            },
            # Analytics Plus
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
                "description": "Data science and analytics experts delivering actionable insights.",
                "contract_start_date": "2023-02-01T00:00:00Z",
                "contract_expiry_date": "2025-01-31T00:00:00Z",
                "has_locations": [
                    {
                        "uid": "_:analyticsplus_loc",
                        "dgraph.type": "Location",
                        "address": "654 Analytics Way",
                        "city": "Boston",
                        "state": "MA",
                        "country": "USA",
                        "country_code": "US",
                        "postal_code": "02101",
                        "latitude": 42.3601,
                        "longitude": -71.0589,
                        "is_primary": True,
                        "belongs_to_vendor": "_:analyticsplus"
                    }
                ],
                "provides_services": [
                    {
                        "uid": "_:analyticsplus_analytics",
                        "dgraph.type": "Service",
                        "service_name": "Data Analytics",
                        "category": "Analytics",
                        "service_description": "Advanced analytics, machine learning, and predictive modeling services.",
                        "is_active": True,
                        "provided_by_vendor": "_:analyticsplus"
                    },
                    {
                        "uid": "_:analyticsplus_ml",
                        "dgraph.type": "Service",
                        "service_name": "Machine Learning",
                        "category": "AI/ML",
                        "service_description": "Custom machine learning models and AI solutions for business optimization.",
                        "is_active": True,
                        "provided_by_vendor": "_:analyticsplus"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            f'{DGRAPH_ALPHA_URL}/mutate?commitNow=true',
            json=data,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            logger.info("Data with proper vendor-service relationships loaded successfully")
            logger.info(f"Dgraph UIDs: {response.json().get('uids')}")
            return True
        else:
            logger.error(f"Data loading failed: {response.status_code}")
            logger.error(response.text)
            return False
    except Exception as e:
        logger.error(f"Error loading Dgraph data: {e}")
        return False

def test_vendor_service_relationships():
    """Test vendor-service relationships"""
    logger.info("Testing vendor-service relationships...")
    
    # Test service query with vendor info
    query = """
    {
      services(func: has(service_name)) {
        service_name
        category
        service_description
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
            logger.info("Vendor-service relationship test successful")
            result = response.json()
            services = result.get('data', {}).get('services', [])
            logger.info(f"Found {len(services)} services with vendor relationships")
            
            for service in services[:5]:  # Show first 5 services
                vendor = service.get('provided_by_vendor', {})
                locations = vendor.get('has_locations', [])
                location = locations[0] if locations else {}
                
                logger.info(f"- {service.get('service_name')} ({service.get('category')})")
                logger.info(f"  Vendor: {vendor.get('name', 'N/A')} (Rating: {vendor.get('rating', 'N/A')})")
                logger.info(f"  Location: {location.get('city', 'N/A')}, {location.get('state', 'N/A')}")
            
            return True
        else:
            logger.error(f"Relationship test failed: {response.status_code}")
            logger.error(response.text)
            return False
    except Exception as e:
        logger.error(f"Error testing relationships: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting Dgraph vendor-service relationship fix...")
    if clear_existing_data():
        if create_proper_vendor_service_data():
            test_vendor_service_relationships()
    logger.info("Dgraph vendor-service relationship fix process finished.")

