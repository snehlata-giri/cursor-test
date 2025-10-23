import asyncio
import sys
sys.path.insert(0, '/home/srinu/cursor-test-repo/cursor-test/backend')

from agents.advanced_vendor_agent import AdvancedVendorAgent
from agents.query_parser import QueryParser

async def test_pricing_query():
    agent = AdvancedVendorAgent()
    parser = QueryParser()
    
    query = "show me pricing details"
    print(f"Testing query: {query}")
    
    parsed = parser.parse_query(query)
    print(f"Intent: {parsed.intent}")
    print(f"SQL Query: {parsed.sql_query}")
    
    response = await agent.process_query(query, {})
    print(f"\nResponse:")
    print(f"Content: {response.content[:200]}")
    print(f"Metadata: {response.metadata}")
    
    if 'table_data' in response.metadata:
        table_data = response.metadata['table_data']
        print(f"\nTable data:")
        print(f"Headers: {table_data.get('headers', [])}")
        print(f"Rows: {len(table_data.get('rows', []))}")
        if table_data.get('rows'):
            print(f"Sample row: {table_data['rows'][0]}")

asyncio.run(test_pricing_query())


