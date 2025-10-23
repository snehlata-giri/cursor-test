#!/usr/bin/env python3
"""
Create working Dgraph data with proper vendor-service relationships
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

def create_working_data():
    """Create data that will work with proper relationships"""
    logger.info("Creating working vendor-service data...")
    
    # First, create vendors
    vendor_data = {
        "set": [
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
                "contract_expiry_date": "2025-12-31T00:00:00Z"
            },
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
                "contract_expiry_date": "2024-05-31T00:00:00Z"
            },
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
                "contract_expiry_date": "2026-02-28T00:00:00Z"
            }
        ]
    }
    
    try:
        response = requests.post(
            f'{DGRAPH_ALPHA_URL}/mutate?commitNow=true',
            json=vendor_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            logger.info("Vendors created successfully")
            uids = response.json().get('uids', {})
            logger.info(f"Vendor UIDs: {uids}")
            
            # Now create services with proper vendor references
            service_data = {
                "set": [
                    {
                        "uid": "_:service1",
                        "dgraph.type": "Service",
                        "service_name": "Cloud Infrastructure",
                        "category": "Technology",
                        "service_description": "Scalable cloud computing resources and infrastructure management.",
                        "is_active": True,
                        "provided_by_vendor": uids.get('_:techcorp', '_:techcorp')
                    },
                    {
                        "uid": "_:service2",
                        "dgraph.type": "Service",
                        "service_name": "Data Analytics",
                        "category": "Analytics",
                        "service_description": "Advanced data processing, analysis, and business intelligence solutions.",
                        "is_active": True,
                        "provided_by_vendor": uids.get('_:techcorp', '_:techcorp')
                    },
                    {
                        "uid": "_:service3",
                        "dgraph.type": "Service",
                        "service_name": "Security Services",
                        "category": "Security",
                        "service_description": "Comprehensive cybersecurity and data protection services.",
                        "is_active": True,
                        "provided_by_vendor": uids.get('_:techcorp', '_:techcorp')
                    },
                    {
                        "uid": "_:service4",
                        "dgraph.type": "Service",
                        "service_name": "Data Analytics",
                        "category": "Analytics",
                        "service_description": "Comprehensive data analysis, reporting, and visualization services.",
                        "is_active": True,
                        "provided_by_vendor": uids.get('_:dataflow', '_:dataflow')
                    },
                    {
                        "uid": "_:service5",
                        "dgraph.type": "Service",
                        "service_name": "Managed IT Services",
                        "category": "Technology",
                        "service_description": "Full-suite IT support, maintenance, and management solutions.",
                        "is_active": True,
                        "provided_by_vendor": uids.get('_:dataflow', '_:dataflow')
                    },
                    {
                        "uid": "_:service6",
                        "dgraph.type": "Service",
                        "service_name": "Cloud Infrastructure",
                        "category": "Technology",
                        "service_description": "Enterprise-grade cloud infrastructure and migration services.",
                        "is_active": True,
                        "provided_by_vendor": uids.get('_:cloudmaster', '_:cloudmaster')
                    },
                    {
                        "uid": "_:service7",
                        "dgraph.type": "Service",
                        "service_name": "Security Services",
                        "category": "Security",
                        "service_description": "Advanced security monitoring and threat protection.",
                        "is_active": True,
                        "provided_by_vendor": uids.get('_:cloudmaster', '_:cloudmaster')
                    }
                ]
            }
            
            response = requests.post(
                f'{DGRAPH_ALPHA_URL}/mutate?commitNow=true',
                json=service_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info("Services created successfully")
                return True
            else:
                logger.error(f"Service creation failed: {response.status_code}")
                logger.error(response.text)
                return False
                
        else:
            logger.error(f"Vendor creation failed: {response.status_code}")
            logger.error(response.text)
            return False
            
    except Exception as e:
        logger.error(f"Error creating data: {e}")
        return False

def test_relationships():
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
                logger.info(f"- {service.get('service_name')} ({service.get('category')})")
                logger.info(f"  Vendor: {vendor.get('name', 'N/A')} (Rating: {vendor.get('rating', 'N/A')})")
            
            return True
        else:
            logger.error(f"Relationship test failed: {response.status_code}")
            logger.error(response.text)
            return False
    except Exception as e:
        logger.error(f"Error testing relationships: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting working Dgraph data creation...")
    if clear_existing_data():
        if create_working_data():
            test_relationships()
    logger.info("Working Dgraph data creation process finished.")

