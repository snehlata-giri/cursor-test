#!/usr/bin/env python3
"""
Script to populate service_pricing_new table with sample data using Dgraph UUIDs
"""

import asyncio
import asyncpg
import logging

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

async def populate_pricing_data():
    """Populate pricing table with sample data using Dgraph UUIDs"""
    conn = None
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        logger.info("Connected to PostgreSQL database.")

        # Clear existing data
        await conn.execute("DELETE FROM service_pricing_new")
        logger.info("Cleared existing pricing data.")

        # Sample pricing data with Dgraph UUIDs
        # Vendors: 0x8, 0xd, 0x10, 0x13, 0x16
        # Services: 0x2, 0x4, 0x5, 0x7, 0x9, 0xa, 0xb, 0xc, 0xf, 0x11, 0x12, 0x15, 0x17
        sample_data = [
            # DataFlow Systems (0x8) services
            ("0x8", "0x2", "monthly", 2500.00, "USD", "month", 10.0),
            ("0x8", "0x4", "yearly", 25000.00, "USD", "year", 15.0),
            ("0x8", "0x5", "hourly", 150.00, "USD", "hour", 0.0),
            
            # CloudMaster Inc (0xd) services
            ("0xd", "0x7", "monthly", 1800.00, "USD", "month", 5.0),
            ("0xd", "0x9", "yearly", 18000.00, "USD", "year", 12.0),
            ("0xd", "0xa", "monthly", 2200.00, "USD", "month", 8.0),
            
            # SecureNet Pro (0x10) services
            ("0x10", "0xb", "monthly", 3200.00, "USD", "month", 12.0),
            ("0x10", "0xc", "yearly", 30000.00, "USD", "year", 20.0),
            ("0x10", "0xf", "hourly", 200.00, "USD", "hour", 0.0),
            
            # Analytics Plus (0x13) services
            ("0x13", "0x11", "monthly", 2800.00, "USD", "month", 15.0),
            ("0x13", "0x12", "yearly", 28000.00, "USD", "year", 18.0),
            ("0x13", "0x15", "monthly", 1900.00, "USD", "month", 10.0),
            
            # TechCorp Solutions (0x16) services
            ("0x16", "0x17", "monthly", 2100.00, "USD", "month", 8.0),
            ("0x16", "0x2", "yearly", 20000.00, "USD", "year", 15.0),
            ("0x16", "0x4", "hourly", 120.00, "USD", "hour", 0.0),
        ]
        
        for vendor_uid, service_uid, pricing_type, base_price, currency, unit, discount in sample_data:
            await conn.execute("""
                INSERT INTO service_pricing_new 
                (vendor_dgraph_uid, service_dgraph_uid, pricing_type, base_price, currency, unit, discount_percentage)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, vendor_uid, service_uid, pricing_type, base_price, currency, unit, discount)
        
        logger.info(f"Successfully inserted {len(sample_data)} pricing records with Dgraph UUIDs.")

    except asyncpg.exceptions.PostgresError as e:
        logger.error(f"PostgreSQL database error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            await conn.close()
            logger.info("Disconnected from PostgreSQL database.")

if __name__ == "__main__":
    asyncio.run(populate_pricing_data())

