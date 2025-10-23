#!/usr/bin/env python3
"""
Script to update service_pricing_new table with Dgraph UUIDs
"""

import asyncio
import asyncpg
import aiohttp
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "password",
    "database": "vendor_management",
}

DGRAPH_URL = "http://localhost:8080"

async def get_dgraph_vendors() -> Dict[str, str]:
    """Get vendor name to UID mapping from Dgraph"""
    query = """
    {
        vendors(func: has(name)) {
            uid
            name
        }
    }
    """
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{DGRAPH_URL}/query",
            json={"query": query},
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                result = await response.json()
                vendors = result.get("data", {}).get("vendors", [])
                return {vendor["name"]: vendor["uid"] for vendor in vendors}
            else:
                logger.error(f"Failed to get vendors from Dgraph: {response.status}")
                return {}

async def get_dgraph_services() -> Dict[str, str]:
    """Get service name to UID mapping from Dgraph"""
    query = """
    {
        services(func: has(service_name)) {
            uid
            service_name
        }
    }
    """
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{DGRAPH_URL}/query",
            json={"query": query},
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                result = await response.json()
                services = result.get("data", {}).get("services", [])
                return {service["service_name"]: service["uid"] for service in services}
            else:
                logger.error(f"Failed to get services from Dgraph: {response.status}")
                return {}

async def update_pricing_with_uids():
    """Update pricing table with Dgraph UUIDs"""
    try:
        # Get mappings from Dgraph
        logger.info("Fetching vendor and service mappings from Dgraph...")
        vendor_uids = await get_dgraph_vendors()
        service_uids = await get_dgraph_services()
        
        logger.info(f"Found {len(vendor_uids)} vendors and {len(service_uids)} services in Dgraph")
        
        # Connect to PostgreSQL
        conn = await asyncpg.connect(**DB_CONFIG)
        
        # Get all pricing records
        pricing_records = await conn.fetch("""
            SELECT id, vendor_name, service_name 
            FROM service_pricing_new 
            WHERE vendor_dgraph_uid IS NULL OR service_dgraph_uid IS NULL
        """)
        
        logger.info(f"Found {len(pricing_records)} pricing records to update")
        
        updated_count = 0
        for record in pricing_records:
            vendor_uid = vendor_uids.get(record['vendor_name'])
            service_uid = service_uids.get(record['service_name'])
            
            if vendor_uid and service_uid:
                await conn.execute("""
                    UPDATE service_pricing_new 
                    SET vendor_dgraph_uid = $1, service_dgraph_uid = $2 
                    WHERE id = $3
                """, vendor_uid, service_uid, record['id'])
                updated_count += 1
                logger.info(f"Updated record {record['id']}: {record['vendor_name']} -> {vendor_uid}, {record['service_name']} -> {service_uid}")
            else:
                logger.warning(f"Could not find UIDs for record {record['id']}: vendor={record['vendor_name']}, service={record['service_name']}")
        
        logger.info(f"Successfully updated {updated_count} pricing records with Dgraph UUIDs")
        
        # Verify the updates
        verification = await conn.fetch("""
            SELECT COUNT(*) as total,
                   COUNT(vendor_dgraph_uid) as with_vendor_uid,
                   COUNT(service_dgraph_uid) as with_service_uid
            FROM service_pricing_new
        """)
        
        result = verification[0]
        logger.info(f"Verification: {result['total']} total records, {result['with_vendor_uid']} with vendor UIDs, {result['with_service_uid']} with service UIDs")
        
        await conn.close()
        
    except Exception as e:
        logger.error(f"Error updating pricing with UIDs: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(update_pricing_with_uids())

