"""
Dgraph client for graph database operations using HTTP API
"""

import asyncio
import json
import logging
import aiohttp
from typing import Dict, List, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class DgraphClient:
    """Client for interacting with Dgraph database via HTTP API"""
    
    def __init__(self):
        self.base_url = f"http://{settings.DGRAPH_HOST}:{settings.DGRAPH_PORT}"
        self.client = None
        self._connect()
    
    def _connect(self):
        """Connect to Dgraph server"""
        try:
            logger.info(f"Connected to Dgraph at {self.base_url}")
            self.client = True  # HTTP client doesn't need persistent connection
            
        except Exception as e:
            logger.error(f"Failed to connect to Dgraph: {e}")
            self.client = None
    
    async def setup_schema(self):
        """Set up the Dgraph schema"""
        if not self.client:
            logger.error("Dgraph client not connected")
            return False
        
        try:
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
            
            # Vector search
            embedding: string .
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/admin/schema", data=schema) as response:
                    if response.status == 200:
                        logger.info("Schema set successfully")
                        return True
                    else:
                        logger.error(f"Schema setting failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error setting schema: {e}")
            return False
    
    async def query_all_vendors(self) -> List[Dict[str, Any]]:
        """Query all vendors from Dgraph"""
        if not self.client:
            logger.error("Dgraph client not connected")
            return []
        
        try:
            query = """
            {
                vendors(func: has(name)) {
                    uid
                    name
                    email
                    phone
                    website
                    rating
                    established_year
                    description
                    contract_start_date
                    contract_expiry_date
                    has_locations {
                        city
                        state
                        country
                        country_code
                        postal_code
                        address
                        latitude
                        longitude
                        is_primary
                    }
                    provides_services {
                        service_name
                        category
                        service_description
                        is_active
                    }
                }
            }
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/query",
                    json={"query": query},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data", {}).get("vendors", [])
                    else:
                        logger.error(f"Query failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error querying vendors: {e}")
            return []
    
    async def query_vendors_by_location(self, location: str) -> List[Dict[str, Any]]:
        """Query vendors by location"""
        if not self.client:
            logger.error("Dgraph client not connected")
            return []
        
        try:
            query = f"""
            {{
                vendors(func: has(name)) @filter(has(has_locations)) {{
                    uid
                    name
                    email
                    phone
                    website
                    rating
                    established_year
                    description
                    contract_start_date
                    contract_expiry_date
                    has_locations @filter(eq(city, "{location}") or eq(state, "{location}") or eq(country, "{location}")) {{
                        city
                        state
                        country
                        country_code
                        postal_code
                        address
                        latitude
                        longitude
                        is_primary
                    }}
                    provides_services {{
                        service_name
                        category
                        service_description
                        is_active
                    }}
                }}
            }}
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/query",
                    json={"query": query},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data", {}).get("vendors", [])
                    else:
                        logger.error(f"Location query failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error querying vendors by location: {e}")
            return []
    
    async def query_services_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Query services by category"""
        if not self.client:
            logger.error("Dgraph client not connected")
            return []
        
        try:
            query = f"""
            {{
                services(func: has(service_name)) @filter(eq(category, "{category}")) {{
                    uid
                    service_name
                    category
                    service_description
                    is_active
                    provided_by_vendor {{
                        name
                        email
                        phone
                        website
                        rating
                        established_year
                        description
                        contract_start_date
                        contract_expiry_date
                        has_locations {{
                            city
                            state
                            country
                            country_code
                            postal_code
                            address
                            latitude
                            longitude
                            is_primary
                        }}
                    }}
                }}
            }}
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/query",
                    json={"query": query},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data", {}).get("services", [])
                    else:
                        logger.error(f"Service query failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error querying services by category: {e}")
            return []
    
    async def query_all_services(self) -> List[Dict[str, Any]]:
        """Query all services from Dgraph"""
        if not self.client:
            logger.error("Dgraph client not connected")
            return []
        
        try:
            query = """
            {
                services(func: has(service_name)) {
                    uid
                    service_name
                    category
                    service_description
                    is_active
                    provided_by_vendor {
                        name
                        email
                        phone
                        website
                        rating
                        established_year
                        description
                        contract_start_date
                        contract_expiry_date
                        has_locations {
                            city
                            state
                            country
                            country_code
                            postal_code
                            address
                            latitude
                            longitude
                            is_primary
                        }
                    }
                }
            }
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/query",
                    json={"query": query},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data", {}).get("services", [])
                    else:
                        logger.error(f"Services query failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error querying all services: {e}")
            return []
    
    async def query_all_locations(self) -> List[Dict[str, Any]]:
        """Query all locations from Dgraph"""
        if not self.client:
            logger.error("Dgraph client not connected")
            return []
        
        try:
            query = """
            {
                locations(func: has(city)) {
                    uid
                    city
                    state
                    country
                    country_code
                    postal_code
                    address
                    latitude
                    longitude
                    is_primary
                    belongs_to_vendor {
                        name
                        email
                        phone
                        website
                        rating
                        established_year
                        description
                        contract_start_date
                        contract_expiry_date
                        provides_services {
                            service_name
                            category
                            service_description
                            is_active
                        }
                    }
                }
            }
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/query",
                    json={"query": query},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data", {}).get("locations", [])
                    else:
                        logger.error(f"Locations query failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error querying all locations: {e}")
            return []
    
    async def mutate_data(self, data: Dict[str, Any]) -> bool:
        """Mutate data in Dgraph"""
        if not self.client:
            logger.error("Dgraph client not connected")
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/mutate?commitNow=true",
                    json=data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        logger.info("Data mutated successfully")
                        return True
                    else:
                        logger.error(f"Mutation failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error mutating data: {e}")
            return False

    async def query_all_services(self) -> List[Dict[str, Any]]:
        """Query all services from Dgraph"""
        if not self.client:
            logger.error("Dgraph client not connected")
            return []
        
        try:
            query = """
            {
                services(func: has(service_name)) {
                    uid
                    service_name
                    category
                    service_description
                    is_active
                    provided_by_vendor {
                        name
                        email
                        phone
                        website
                        rating
                        established_year
                        description
                        contract_start_date
                        contract_expiry_date
                        has_locations {
                            city
                            state
                            country
                            country_code
                            postal_code
                            address
                            latitude
                            longitude
                            is_primary
                        }
                    }
                }
            }
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/query",
                    json={"query": query},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data", {}).get("services", [])
                    else:
                        logger.error(f"Services query failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error querying all services: {e}")
            return []


# Global instance
dgraph_client = DgraphClient()