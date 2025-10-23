#!/usr/bin/env python3
"""
Simple setup script for hybrid architecture
"""
import asyncio
import asyncpg
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "password",
    "database": "vendor_management"
}

async def setup_hybrid():
    """Setup hybrid architecture with sample data"""
    try:
        logger.info("Setting up hybrid architecture...")
        
        # Connect to database
        conn = await asyncpg.connect(**DB_CONFIG)
        logger.info("Connected to PostgreSQL")
        
        # Create service_pricing_new table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS service_pricing_new (
                id SERIAL PRIMARY KEY,
                vendor_name VARCHAR(255) NOT NULL,
                service_name VARCHAR(255) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                currency VARCHAR(3) DEFAULT 'USD',
                unit VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create indexes
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_service_pricing_vendor ON service_pricing_new(vendor_name);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_service_pricing_service ON service_pricing_new(service_name);")
        
        # Insert sample pricing data
        sample_pricing = [
            ("TechCorp Solutions", "Cloud Infrastructure", "monthly", 1500.00, "USD", "per month", 0.0, True),
            ("TechCorp Solutions", "Data Analytics", "monthly", 2500.00, "USD", "per month", 0.0, True),
            ("TechCorp Solutions", "Security Services", "monthly", 1800.00, "USD", "per month", 0.0, True),
            ("DataFlow Systems", "Cloud Infrastructure", "monthly", 1200.00, "USD", "per month", 0.0, True),
            ("DataFlow Systems", "Data Analytics", "monthly", 2200.00, "USD", "per month", 0.0, True),
            ("DataFlow Systems", "Security Services", "monthly", 1600.00, "USD", "per month", 0.0, True),
            ("CloudMaster Inc", "Cloud Infrastructure", "monthly", 2000.00, "USD", "per month", 0.0, True),
            ("CloudMaster Inc", "Data Analytics", "monthly", 3000.00, "USD", "per month", 0.0, True),
            ("CloudMaster Inc", "Security Services", "monthly", 2100.00, "USD", "per month", 0.0, True),
            ("SecureNet Pro", "Security Services", "monthly", 1900.00, "USD", "per month", 0.0, True),
            ("SecureNet Pro", "Cloud Infrastructure", "monthly", 1400.00, "USD", "per month", 0.0, True),
            ("Analytics Plus", "Data Analytics", "monthly", 2800.00, "USD", "per month", 0.0, True),
            ("Analytics Plus", "Cloud Infrastructure", "monthly", 1300.00, "USD", "per month", 0.0, True),
            ("InfraTech Solutions", "Cloud Infrastructure", "monthly", 1700.00, "USD", "per month", 0.0, True),
            ("InfraTech Solutions", "Security Services", "monthly", 2000.00, "USD", "per month", 0.0, True),
            ("DataWise Corp", "Data Analytics", "monthly", 2600.00, "USD", "per month", 0.0, True),
            ("DataWise Corp", "Cloud Infrastructure", "monthly", 1100.00, "USD", "per month", 0.0, True),
            ("CloudSecure Ltd", "Security Services", "monthly", 1750.00, "USD", "per month", 0.0, True),
            ("CloudSecure Ltd", "Cloud Infrastructure", "monthly", 1600.00, "USD", "per month", 0.0, True),
            ("AnalyticsHub", "Data Analytics", "monthly", 2400.00, "USD", "per month", 0.0, True),
            ("AnalyticsHub", "Security Services", "monthly", 1850.00, "USD", "per month", 0.0, True),
            ("TechInfra Co", "Cloud Infrastructure", "monthly", 1350.00, "USD", "per month", 0.0, True),
            ("TechInfra Co", "Data Analytics", "monthly", 2700.00, "USD", "per month", 0.0, True),
            ("SecureCloud Inc", "Security Services", "monthly", 1950.00, "USD", "per month", 0.0, True)
        ]
        
        await conn.executemany("""
            INSERT INTO service_pricing_new (vendor_name, service_name, pricing_type, base_price, currency, unit, discount_percentage, is_active)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT DO NOTHING
        """, sample_pricing)
        
        logger.info("Inserted sample pricing data")
        
        # Create vendor_embeddings table for vector search
        await conn.execute("""
            CREATE EXTENSION IF NOT EXISTS vector;
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS vendor_embeddings (
                id SERIAL PRIMARY KEY,
                vendor_name VARCHAR(255) NOT NULL,
                embedding vector(384),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_vendor_embeddings_name ON vendor_embeddings(vendor_name);")
        
        logger.info("Created vendor_embeddings table")
        
        await conn.close()
        logger.info("Hybrid architecture setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(setup_hybrid())
