#!/usr/bin/env python3
"""
Dgraph initialization script
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.dgraph_client import dgraph_client


async def main():
    """Initialize Dgraph with schema and mock data"""
    print("🚀 Initializing Dgraph...")
    
    # Setup schema
    print("📋 Setting up Dgraph schema...")
    schema_success = await dgraph_client.setup_schema()
    if not schema_success:
        print("❌ Failed to setup Dgraph schema")
        return False
    
    print("✅ Dgraph schema setup completed")
    
    # Load mock data
    print("📊 Loading mock data...")
    data_success = await dgraph_client.load_mock_data()
    if not data_success:
        print("❌ Failed to load mock data")
        return False
    
    print("✅ Mock data loaded successfully")
    
    # Test queries
    print("🔍 Testing Dgraph queries...")
    
    # Test query all vendors
    vendors = await dgraph_client.query_all_vendors()
    print(f"📈 Found {len(vendors)} vendors in Dgraph")
    
    # Test query by location
    sf_vendors = await dgraph_client.query_vendors_by_location("San Francisco")
    print(f"📍 Found {len(sf_vendors)} vendors in San Francisco")
    
    # Test query by category
    tech_services = await dgraph_client.query_services_by_category("Technology")
    print(f"🔧 Found {len(tech_services)} Technology services")
    
    print("🎉 Dgraph initialization completed successfully!")
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)


