#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.insert(0, '/home/srinu/cursor-test-repo/cursor-test/backend')

from agents.advanced_vendor_agent import AdvancedVendorAgent

async def test_direct_pricing():
    print("Testing pricing query directly...")
    
    agent = AdvancedVendorAgent()
    
    # Test the pricing query
    response = await agent.process_query("show me pricing details", {})
    
    print(f"Response content: {response.content[:200]}...")
    print(f"Metadata: {response.metadata}")
    
    if 'table_data' in response.metadata:
        table_data = response.metadata['table_data']
        rows = table_data.get('rows', [])
        print(f"Found {len(rows)} rows")
        if rows:
            print("First row:", rows[0])
    else:
        print("No table data found")

if __name__ == "__main__":
    asyncio.run(test_direct_pricing())

