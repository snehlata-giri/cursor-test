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

DGRAPH_URL = "http://localhost:8081"

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
            response.raise_for_status()
            data = await response.json()
            return {v['name']: v['uid'] for v in data.get('data', {}).get('vendors', [])}

async def get_dgraph_services() -> Dict[str, str]:
    """Get service name to UID mapping from Dgraph"""
    query = """
    {
        services(func: has(name)) {
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
            response.raise_for_status()
            data = await response.json()
            return {s['name']: s['uid'] for s in data.get('data', {}).get('services', [])}

async def update_pricing_table_with_uids():
    """
    Connects to PostgreSQL, fetches vendor and service UIDs from Dgraph,
    and updates the service_pricing_new table.
    """
    conn = None
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        logger.info("Connected to PostgreSQL database.")

        # Get Dgraph mappings
        vendor_name_to_uid = await get_dgraph_vendors()
        service_name_to_uid = await get_dgraph_services()
        logger.info(f"Fetched {len(vendor_name_to_uid)} vendors and {len(service_name_to_uid)} services from Dgraph.")

        # First, let's see what data we have in the pricing table
        pricing_records = await conn.fetch("SELECT id, vendor_name, service_name FROM service_pricing_new")
        logger.info(f"Found {len(pricing_records)} pricing records in PostgreSQL.")

        if not pricing_records:
            logger.info("No pricing records found. Creating sample data...")
            # Create sample pricing data with Dgraph UUIDs
            sample_data = [
                ("0x1", "0x2", "monthly", 2500.00, "USD", "month", 10.0),
                ("0x1", "0x3", "yearly", 25000.00, "USD", "year", 15.0),
                ("0x4", "0x5", "monthly", 1800.00, "USD", "month", 5.0),
                ("0x4", "0x6", "hourly", 150.00, "USD", "hour", 0.0),
                ("0x7", "0x8", "monthly", 3200.00, "USD", "month", 12.0),
            ]
            
            for vendor_uid, service_uid, pricing_type, base_price, currency, unit, discount in sample_data:
                await conn.execute("""
                    INSERT INTO service_pricing_new 
                    (vendor_dgraph_uid, service_dgraph_uid, pricing_type, base_price, currency, unit, discount_percentage)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, vendor_uid, service_uid, pricing_type, base_price, currency, unit, discount)
            
            logger.info("Created sample pricing data with Dgraph UUIDs.")
        else:
            # Update existing records with Dgraph UUIDs
            updated_count = 0
            for record in pricing_records:
                pricing_id = record['id']
                vendor_name = record['vendor_name']
                service_name = record['service_name']

                vendor_uid = vendor_name_to_uid.get(vendor_name)
                service_uid = service_name_to_uid.get(service_name)

                if vendor_uid or service_uid:
                    update_query = "UPDATE service_pricing_new SET "
                    params = []
                    if vendor_uid:
                        update_query += "vendor_dgraph_uid = $1"
                        params.append(vendor_uid)
                    if service_uid:
                        if vendor_uid:
                            update_query += ", "
                        update_query += "service_dgraph_uid = $2" if vendor_uid else "service_dgraph_uid = $1"
                        params.append(service_uid)
                    
                    update_query += f" WHERE id = ${len(params) + 1}"
                    params.append(pricing_id)

                    await conn.execute(update_query, *params)
                    updated_count += 1
                    logger.info(f"Updated pricing record {pricing_id} with Vendor UID: {vendor_uid}, Service UID: {service_uid}")
            
            logger.info(f"Successfully updated {updated_count} pricing records with Dgraph UUIDs.")

    except aiohttp.ClientError as e:
        logger.error(f"Dgraph connection error: {e}")
    except asyncpg.exceptions.PostgresError as e:
        logger.error(f"PostgreSQL database error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            await conn.close()
            logger.info("Disconnected from PostgreSQL database.")

if __name__ == "__main__":
    asyncio.run(update_pricing_table_with_uids())

