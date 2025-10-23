#!/usr/bin/env python3
"""
Test script for dynamic query parsing and execution
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from agents.query_parser import QueryParser
from agents.advanced_vendor_agent import AdvancedVendorAgent


async def test_dynamic_queries():
    """Test various dynamic queries"""
    print("🧪 Testing Dynamic Query System\n")
    
    # Initialize components
    parser = QueryParser()
    agent = AdvancedVendorAgent()
    
    # Test queries
    test_queries = [
        "List all vendors costing more than $10,000 a month",
        "Show me vendors in California with ratings above 4.0",
        "Find technology vendors established after 2015",
        "Vendors with hourly rates under $100",
        "Compare vendors offering cloud services",
        "Show me all vendors with discount more than 10%",
        "List vendors in San Francisco with fixed pricing over $15,000",
        "Find energy vendors with ratings between 4.0 and 4.5"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 Test {i}: {query}")
        print("-" * 60)
        
        # Parse the query
        parsed_query = parser.parse_query(query)
        print(f"Intent: {parsed_query.intent.value}")
        print(f"Criteria: {len(parsed_query.criteria)} filter(s)")
        
        for criterion in parsed_query.criteria:
            print(f"  • {criterion.field} {criterion.operator} {criterion.value}")
        
        print(f"Needs Relationships: {parsed_query.needs_relationships}")
        print(f"SQL Query: {parsed_query.sql_query[:100]}..." if parsed_query.sql_query else "No SQL Query")
        print()
        
        # Test agent confidence
        confidence = agent.can_handle(query)
        print(f"Agent Confidence: {confidence:.2f}")
        print("=" * 60)
        print()


def test_query_parsing():
    """Test query parsing without database connection"""
    print("🔍 Testing Query Parsing\n")
    
    parser = QueryParser()
    
    # Test various query patterns
    test_cases = [
        {
            "query": "List all vendors costing more than $10,000 a month",
            "expected_intent": "COST_ANALYSIS",
            "expected_criteria": ["sp.base_price > 10000", "sp.pricing_type = monthly"]
        },
        {
            "query": "Show me vendors in California with ratings above 4.0",
            "expected_intent": "LOCATION_SEARCH",
            "expected_criteria": ["vl.city LIKE %California%", "v.rating > 4.0"]
        },
        {
            "query": "Find technology vendors established after 2015",
            "expected_intent": "SERVICE_FILTER",
            "expected_criteria": ["vs.service_name LIKE %technology%", "v.established_year > 2015"]
        },
        {
            "query": "Vendors with hourly rates under $100",
            "expected_intent": "COST_ANALYSIS",
            "expected_criteria": ["sp.base_price < 100", "sp.pricing_type = hourly"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['query']}")
        parsed = parser.parse_query(test_case['query'])
        
        print(f"  Intent: {parsed.intent.value}")
        print(f"  Criteria: {len(parsed.criteria)}")
        for criterion in parsed.criteria:
            print(f"    • {criterion.field} {criterion.operator} {criterion.value}")
        
        print(f"  SQL: {parsed.sql_query[:80]}..." if parsed.sql_query else "  No SQL")
        print()


if __name__ == "__main__":
    print("🚀 Dynamic Query System Test Suite")
    print("=" * 50)
    
    # Test query parsing
    test_query_parsing()
    
    print("\n" + "=" * 50)
    print("📊 Advanced Query Testing")
    print("=" * 50)
    
    # Test advanced queries (requires database connection)
    try:
        asyncio.run(test_dynamic_queries())
    except Exception as e:
        print(f"❌ Database connection required for full testing: {e}")
        print("💡 Run with database connected to test full functionality")


