#!/usr/bin/env python3
"""
Migration script to convert to hybrid Dgraph + PostgreSQL architecture
"""

import asyncio
import asyncpg
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "password",
    "database": "vendor_management"
}

async def migrate_database():
    """Migrate database to hybrid architecture"""
    try:
        # Connect to PostgreSQL
        conn = await asyncpg.connect(**DB_CONFIG)
        logger.info("Connected to PostgreSQL")
        
        # Create new pricing table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS service_pricing_new (
                id SERIAL PRIMARY KEY,
                vendor_name VARCHAR(200) NOT NULL,
                service_name VARCHAR(200) NOT NULL,
                pricing_type VARCHAR(50) NOT NULL,
                base_price DECIMAL(10, 2) NOT NULL,
                currency VARCHAR(3) DEFAULT 'USD',
                unit VARCHAR(50),
                discount_percentage DECIMAL(5, 2) DEFAULT 0.0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        logger.info("Created service_pricing_new table")
        
        # Create indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_vendor_service 
            ON service_pricing_new (vendor_name, service_name)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_pricing_type 
            ON service_pricing_new (pricing_type)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_range 
            ON service_pricing_new (base_price)
        """)
        logger.info("Created indexes")
        
        # Migrate existing pricing data
        await migrate_pricing_data(conn)
        
        # Enable pgvector extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        logger.info("Enabled pgvector extension")
        
        # Create vector embeddings table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS vendor_embeddings (
                id SERIAL PRIMARY KEY,
                vendor_name VARCHAR(200),
                service_name VARCHAR(200),
                embedding vector(1536),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        logger.info("Created vendor_embeddings table")
        
        await conn.close()
        logger.info("Migration completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

async def migrate_pricing_data(conn):
    """Migrate existing pricing data to new table"""
    try:
        # Get existing pricing data with vendor and service names
        rows = await conn.fetch("""
            SELECT 
                v.name as vendor_name,
                vs.service_name,
                sp.pricing_type,
                sp.base_price,
                sp.currency,
                sp.unit,
                sp.discount_percentage,
                sp.is_active
            FROM service_pricing sp
            JOIN vendor_services vs ON sp.vendor_service_id = vs.id
            JOIN vendors v ON vs.vendor_id = v.id
            WHERE sp.is_active = true
        """)
        
        # Insert into new table
        for row in rows:
            await conn.execute("""
                INSERT INTO service_pricing_new 
                (vendor_name, service_name, pricing_type, base_price, currency, unit, discount_percentage, is_active)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, 
            row['vendor_name'], row['service_name'], row['pricing_type'], 
            row['base_price'], row['currency'], row['unit'], 
            row['discount_percentage'], row['is_active'])
        
        logger.info(f"Migrated {len(rows)} pricing records")
        
    except Exception as e:
        logger.error(f"Error migrating pricing data: {e}")
        raise

async def create_dgraph_mock_data():
    """Create mock data for Dgraph with contract dates and location details"""
    mock_data = {
        "set": [
            {
                "vendor_id": "vendor_1",
                "name": "TechSolutions Inc",
                "email": "contact@techsolutions.com",
                "phone": "+1-555-0101",
                "website": "https://techsolutions.com",
                "rating": 4.5,
                "established_year": 2015,
                "description": "Leading technology solutions provider specializing in cloud infrastructure and software development.",
                "contract_start_date": "2023-01-15T00:00:00Z",
                "contract_expiry_date": "2025-01-15T00:00:00Z",
                "has_locations": [
                    {
                        "address": "123 Tech Street",
                        "city": "Austin",
                        "state": "Texas",
                        "country": "United States",
                        "country_code": "US",
                        "postal_code": "78701",
                        "latitude": 30.2672,
                        "longitude": -97.7431,
                        "is_primary": True
                    },
                    {
                        "address": "456 Innovation Drive",
                        "city": "San Francisco",
                        "state": "California",
                        "country": "United States",
                        "country_code": "US",
                        "postal_code": "94105",
                        "latitude": 37.7749,
                        "longitude": -122.4194,
                        "is_primary": False
                    }
                ],
                "provides_services": [
                    {
                        "service_name": "Cloud Infrastructure Setup",
                        "category": "Technology",
                        "service_description": "Complete cloud infrastructure setup and migration services including AWS, Azure, and GCP.",
                        "is_active": True
                    },
                    {
                        "service_name": "Software Development",
                        "category": "Technology",
                        "service_description": "Custom software development services including web applications, mobile apps, and APIs.",
                        "is_active": True
                    }
                ]
            },
            {
                "vendor_id": "vendor_2",
                "name": "GreenEnergy Corp",
                "email": "info@greenenergy.com",
                "phone": "+1-555-0102",
                "website": "https://greenenergy.com",
                "rating": 4.2,
                "established_year": 2018,
                "description": "Sustainable energy solutions and environmental consulting services.",
                "contract_start_date": "2023-03-01T00:00:00Z",
                "contract_expiry_date": "2025-03-01T00:00:00Z",
                "has_locations": [
                    {
                        "address": "789 Green Avenue",
                        "city": "Portland",
                        "state": "Oregon",
                        "country": "United States",
                        "country_code": "US",
                        "postal_code": "97201",
                        "latitude": 45.5152,
                        "longitude": -122.6784,
                        "is_primary": True
                    }
                ],
                "provides_services": [
                    {
                        "service_name": "Solar Panel Installation",
                        "category": "Energy",
                        "service_description": "Residential and commercial solar panel installation and maintenance services.",
                        "is_active": True
                    },
                    {
                        "service_name": "Energy Audit",
                        "category": "Energy",
                        "service_description": "Comprehensive energy audit services to identify efficiency improvements and cost savings.",
                        "is_active": True
                    }
                ]
            },
            {
                "vendor_id": "vendor_3",
                "name": "DataAnalytics Pro",
                "email": "hello@dataanalytics.com",
                "phone": "+1-555-0103",
                "website": "https://dataanalytics.com",
                "rating": 4.7,
                "established_year": 2020,
                "description": "Advanced data analytics and business intelligence solutions.",
                "contract_start_date": "2023-06-01T00:00:00Z",
                "contract_expiry_date": "2025-06-01T00:00:00Z",
                "has_locations": [
                    {
                        "address": "321 Data Street",
                        "city": "Seattle",
                        "state": "Washington",
                        "country": "United States",
                        "country_code": "US",
                        "postal_code": "98101",
                        "latitude": 47.6062,
                        "longitude": -122.3321,
                        "is_primary": True
                    }
                ],
                "provides_services": [
                    {
                        "service_name": "Data Analytics Consulting",
                        "category": "Analytics",
                        "service_description": "Advanced data analytics consulting including machine learning and predictive modeling.",
                        "is_active": True
                    },
                    {
                        "service_name": "Business Intelligence Dashboard",
                        "category": "Analytics",
                        "service_description": "Custom business intelligence dashboards and reporting solutions.",
                        "is_active": True
                    }
                ]
            },
            {
                "vendor_id": "vendor_4",
                "name": "CreativeDesign Studio",
                "email": "studio@creativedesign.com",
                "phone": "+1-555-0104",
                "website": "https://creativedesign.com",
                "rating": 4.3,
                "established_year": 2017,
                "description": "Full-service design agency specializing in branding and web development.",
                "contract_start_date": "2023-02-15T00:00:00Z",
                "contract_expiry_date": "2025-02-15T00:00:00Z",
                "has_locations": [
                    {
                        "address": "654 Design Boulevard",
                        "city": "New York",
                        "state": "New York",
                        "country": "United States",
                        "country_code": "US",
                        "postal_code": "10001",
                        "latitude": 40.7589,
                        "longitude": -73.9851,
                        "is_primary": True
                    }
                ],
                "provides_services": [
                    {
                        "service_name": "Brand Identity Design",
                        "category": "Design",
                        "service_description": "Complete brand identity design including logo, color palette, and brand guidelines.",
                        "is_active": True
                    },
                    {
                        "service_name": "Web Design & Development",
                        "category": "Design",
                        "service_description": "Custom website design and development services with responsive design.",
                        "is_active": True
                    }
                ]
            },
            {
                "vendor_id": "vendor_5",
                "name": "LogisticsMaster",
                "email": "support@logisticsmaster.com",
                "phone": "+1-555-0105",
                "website": "https://logisticsmaster.com",
                "rating": 4.1,
                "established_year": 2012,
                "description": "Comprehensive logistics and supply chain management solutions.",
                "contract_start_date": "2023-04-01T00:00:00Z",
                "contract_expiry_date": "2025-04-01T00:00:00Z",
                "has_locations": [
                    {
                        "address": "987 Logistics Lane",
                        "city": "Chicago",
                        "state": "Illinois",
                        "country": "United States",
                        "country_code": "US",
                        "postal_code": "60601",
                        "latitude": 41.8781,
                        "longitude": -87.6298,
                        "is_primary": True
                    }
                ],
                "provides_services": [
                    {
                        "service_name": "Supply Chain Optimization",
                        "category": "Logistics",
                        "service_description": "Supply chain analysis and optimization services to improve efficiency and reduce costs.",
                        "is_active": True
                    },
                    {
                        "service_name": "Warehouse Management",
                        "category": "Logistics",
                        "service_description": "Complete warehouse management solutions including inventory tracking and optimization.",
                        "is_active": True
                    }
                ]
            }
        ]
    }
    
    # Save to file
    with open("dgraph_mock_data_new.json", "w") as f:
        json.dump(mock_data, f, indent=2)
    
    logger.info("Created Dgraph mock data with contract dates and location details")

async def main():
    """Main migration function"""
    logger.info("Starting hybrid architecture migration...")
    
    # Migrate database
    await migrate_database()
    
    # Create Dgraph mock data
    await create_dgraph_mock_data()
    
    logger.info("Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())


