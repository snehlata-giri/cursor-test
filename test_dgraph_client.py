#!/usr/bin/env python3
"""
Test Dgraph client connection
"""
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append('/home/srinu/cursor-test-repo/cursor-test/backend')

from app.core.dgraph_client import dgraph_client

async def test_dgraph_client():
    """Test Dgraph client connection"""
    print("Testing Dgraph client connection...")
    
    try:
        # Test connection
        print(f"Dgraph client: {dgraph_client}")
        print(f"Dgraph client.client: {dgraph_client.client}")
        
        if dgraph_client.client is None:
            print("❌ Dgraph client is None - connection failed")
            return False
        
        # Test query
        print("Testing Dgraph query...")
        results = await dgraph_client.query_all_vendors()
        print(f"✅ Query successful! Found {len(results)} vendors")
        
        for vendor in results:
            print(f"  - {vendor.get('name', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Dgraph client: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_dgraph_client())

