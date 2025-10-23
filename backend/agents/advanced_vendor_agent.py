"""
Advanced Vendor Agent with Dynamic Query Processing and Tabular Responses
"""

from typing import Dict, List, Any, Optional
import asyncio
import asyncpg
import json
from agents.base_agent import BaseAgent, AgentResponse
from agents.query_parser import QueryParser, QueryIntent
from app.core.config import settings
from app.core.dgraph_client import dgraph_client
from app.services.hybrid_search import hybrid_search_service
import logging

logger = logging.getLogger(__name__)


class AdvancedVendorAgent(BaseAgent):
    """Advanced vendor agent with dynamic query processing and tabular responses"""
    
    def __init__(self):
        super().__init__(
            agent_id="advanced_vendor_agent",
            name="Advanced Vendor Agent",
            description="Handles complex vendor queries with dynamic SQL generation and tabular responses.",
            capabilities=[
                "dynamic_queries", "cost_analysis", "location_search", "service_filtering",
                "rating_analysis", "comparison_queries", "relationship_analysis", "tabular_responses"
            ]
        )
        self.query_parser = QueryParser()

    async def process_query(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """Process complex vendor queries with dynamic SQL generation"""
        try:
            # Parse the natural language query
            parsed_query = self.query_parser.parse_query(query)
            
            logger.info(f"Parsed query intent: {parsed_query.intent}")
            logger.info(f"Query criteria: {parsed_query.criteria}")
            
            # Execute the query - Use PostgreSQL only for now
            results = await self._execute_sql_query(parsed_query)
            
            # Format results as table
            table_data = self._format_as_table(results, parsed_query.intent)
            
            # Generate response content
            response_content = self._generate_response_content(query, table_data, parsed_query)
            
            return AgentResponse(
                content=response_content,
                agent_id=self.agent_id,
                agent_name=self.name,
                type="assistant",
                metadata={
                    "query_type": parsed_query.intent.value,
                    "criteria_count": len(parsed_query.criteria),
                    "result_count": len(results),
                    "table_data": table_data,
                    "sql_query": parsed_query.sql_query
                }
            )
            
        except Exception as e:
            logger.error(f"Error in AdvancedVendorAgent: {e}", exc_info=True)
            return AgentResponse(
                content=f"I encountered an error processing your query: {str(e)}",
                agent_id=self.agent_id,
                agent_name=self.name,
                type="error"
            )

    async def _execute_sql_query(self, parsed_query) -> List[Dict[str, Any]]:
        """Execute query using hybrid search (Dgraph + PostgreSQL) or direct SQL"""
        try:
            # Use hybrid search service for complex queries and Dgraph-specific queries
            logger.info(f"Query intent: {parsed_query.intent}, needs_relationships: {parsed_query.needs_relationships}")
            
            # For service, vendor, and location queries, use Dgraph directly
            if parsed_query.intent in [QueryIntent.SERVICE_FILTER, QueryIntent.VENDOR_LIST, QueryIntent.LOCATION_SEARCH, QueryIntent.RATING_FILTER, QueryIntent.TIME_FILTER]:
                logger.info(f"Taking Dgraph path for {parsed_query.intent.value} query")
                try:
                    results = await self._execute_dgraph_query(parsed_query)
                    logger.info(f"Dgraph {parsed_query.intent.value} query completed, returned {len(results)} results")
                    return results
                except Exception as e:
                    logger.error(f"Dgraph {parsed_query.intent.value} query failed: {e}")
                    return []
            
            # For complex pricing queries, use PostgreSQL + Dgraph for enhanced data
            if parsed_query.intent == QueryIntent.COMPLEX_PRICING:
                logger.info("Taking complex pricing path with PostgreSQL + Dgraph enhancement")
                if parsed_query.sql_query is None:
                    logger.warning("No SQL query generated for complex pricing")
                    return []
                conn = None
                try:
                    # Get pricing data from PostgreSQL
                    conn = await self._get_database_connection()
                    logger.info(f"Executing complex pricing SQL query: {parsed_query.sql_query}")
                    rows = await conn.fetch(parsed_query.sql_query)
                    pricing_results = [dict(row) for row in rows]
                    logger.info(f"Complex pricing query completed, returned {len(pricing_results)} results")
                    
                    # Enhance with Dgraph data for category and location details
                    logger.info("Starting Dgraph enhancement...")
                    enhanced_results = await self._enhance_pricing_with_dgraph_data(pricing_results)
                    logger.info(f"Enhancement completed, returning {len(enhanced_results)} results")
                    
                    return enhanced_results
                except Exception as e:
                    logger.error(f"Error executing complex pricing query: {e}", exc_info=True)
                    return []
                finally:
                    if conn is not None:
                        await conn.close()
            
            # Use hybrid search for complex queries, PostgreSQL for simple ones
            if parsed_query.needs_relationships or parsed_query.intent in [
                QueryIntent.LOCATION_SEARCH, 
                QueryIntent.COMPLEX_FILTER,
                QueryIntent.RELATIONSHIP_ANALYSIS,
                QueryIntent.COMPARISON
            ]:
                logger.info("Taking hybrid search path")
                # Extract filters from criteria
                filters = {}
                for criterion in parsed_query.criteria:
                    if criterion.field in ['city', 'state', 'country']:
                        filters['location'] = criterion.value
                    elif criterion.field == 'category':
                        filters['category'] = criterion.value
                
                # Use hybrid search with timeout protection
                try:
                    results = await asyncio.wait_for(
                        hybrid_search_service.search_vendors_with_pricing(
                            query=parsed_query.original_query,
                            filters=filters
                        ),
                        timeout=10.0  # 10 second timeout
                    )
                    logger.info(f"Hybrid search completed, returned {len(results)} results")
                    return results
                except asyncio.TimeoutError:
                    logger.warning("Hybrid search timed out, falling back to PostgreSQL")
                    # Fall back to PostgreSQL
                    pass
            
            # Use direct PostgreSQL for simple queries or as fallback
            if parsed_query.sql_query is None:
                logger.warning("No SQL query generated and no Dgraph query available")
                return []
                
            logger.info("Taking direct PostgreSQL path")
            conn = await self._get_database_connection()
            try:
                logger.info(f"Executing SQL query: {parsed_query.sql_query}")
                rows = await conn.fetch(parsed_query.sql_query)
                return [dict(row) for row in rows]
            finally:
                await conn.close()
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []

    async def _execute_dgraph_query(self, parsed_query) -> List[Dict[str, Any]]:
        """Execute Dgraph query directly"""
        try:
            if parsed_query.dgraph_query:
                logger.info(f"Executing Dgraph query: {parsed_query.dgraph_query}")
                # Use the Dgraph client to execute the query based on intent
                if parsed_query.intent == QueryIntent.SERVICE_FILTER:
                    # For service queries, get all services from Dgraph
                    results = await dgraph_client.query_all_services()
                    return results
                elif parsed_query.intent in [QueryIntent.VENDOR_LIST, QueryIntent.LOCATION_SEARCH, QueryIntent.RATING_FILTER, QueryIntent.TIME_FILTER]:
                    # For vendor and location queries, get all vendors from Dgraph
                    results = await dgraph_client.query_all_vendors()
                    return results
                else:
                    # For other queries, use the generated Dgraph query
                    results = await dgraph_client.query_all_vendors()
                    return results
            else:
                logger.warning("No Dgraph query generated")
                return []
        except Exception as e:
            logger.error(f"Error executing Dgraph query: {e}")
            return []

    # async def _execute_hybrid_query(self, parsed_query) -> List[Dict[str, Any]]:
    #     """Execute hybrid query using both PostgreSQL and Dgraph"""
    #     # Get relationship data from Dgraph
    #     dgraph_results = await dgraph_client.query_all_vendors()
    #     
    #     # Get detailed data from PostgreSQL
    #     postgres_results = await self._execute_sql_query(parsed_query)
    #     
    #     # Merge results
    #     return self._merge_hybrid_results(dgraph_results, postgres_results)

    def _format_as_table(self, results: List[Dict[str, Any]], intent: QueryIntent) -> Dict[str, Any]:
        """Format query results as table data"""
        if not results:
            return {
                "headers": [],
                "rows": [],
                "summary": "No results found"
            }
        
        # Determine columns based on intent and available data
        if intent == QueryIntent.VENDOR_LIST:
            # Vendor list from Dgraph
            headers = ["Vendor", "Rating", "Email", "Phone", "Website", "Established", "Location", "Services", "Description"]
            rows = []
            for result in results:
                # Debug: Check if result is a dict
                if not isinstance(result, dict):
                    logger.error(f"Result is not a dict: {type(result)} - {result}")
                    continue
                    
                # Handle Dgraph vendor data structure
                locations = result.get('has_locations', [])
                location = locations[0] if locations and isinstance(locations[0], dict) else {}
                
                services = result.get('provides_services', [])
                service_names = [s.get('service_name', 'N/A') for s in services if isinstance(s, dict)] if services else []
                services_str = ', '.join(service_names[:3]) + ('...' if len(service_names) > 3 else '')
                
                rows.append([
                    result.get('name', 'N/A'),
                    f"{result.get('rating', 0):.1f}/5.0",
                    result.get('email', 'N/A'),
                    result.get('phone', 'N/A'),
                    result.get('website', 'N/A'),
                    result.get('established_year', 'N/A'),
                    f"{location.get('city', 'N/A')}, {location.get('state', 'N/A')}",
                    services_str or 'N/A',
                    (result.get('description', 'N/A')[:50] + "...") if len(result.get('description', '')) > 50 else result.get('description', 'N/A')
                ])
        
        elif intent == QueryIntent.COST_ANALYSIS:
            headers = ["Vendor", "Service", "Category", "Pricing Type", "Price", "Currency", "Unit", "Discount", "Rating"]
            rows = []
            for result in results:
                rows.append([
                    result.get('name', 'N/A'),
                    result.get('service_name', 'N/A'),
                    result.get('category', 'N/A'),
                    result.get('pricing_type', 'N/A'),
                    f"${result.get('base_price', 0):,.2f}",
                    result.get('currency', 'USD'),
                    result.get('unit', 'N/A'),
                    f"{result.get('discount_percentage', 0):.1f}%",
                    f"{result.get('rating', 0):.1f}/5.0"
                ])
        
        elif intent == QueryIntent.LOCATION_SEARCH:
            headers = ["Vendor", "Location", "City", "State", "Services", "Rating", "Contact"]
            rows = []
            for result in results:
                # Debug: Check if result is a dict
                if not isinstance(result, dict):
                    logger.error(f"Result is not a dict: {type(result)} - {result}")
                    continue
                    
                # Handle Dgraph vendor data structure
                locations = result.get('has_locations', [])
                location = locations[0] if locations and isinstance(locations[0], dict) else {}
                
                services = result.get('provides_services', [])
                service_names = [s.get('service_name', 'N/A') for s in services if isinstance(s, dict)] if services else []
                services_str = ', '.join(service_names[:2]) + ('...' if len(service_names) > 2 else '')
                
                rows.append([
                    result.get('name', 'N/A'),
                    location.get('address', 'N/A'),
                    location.get('city', 'N/A'),
                    location.get('state', 'N/A'),
                    services_str or 'N/A',
                    f"{result.get('rating', 0):.1f}/5.0",
                    result.get('email', 'N/A')
                ])
        
        elif intent == QueryIntent.RATING_FILTER:
            headers = ["Vendor", "Rating", "Established", "Services", "Location", "Contact"]
            rows = []
            for result in results:
                # Debug: Check if result is a dict
                if not isinstance(result, dict):
                    logger.error(f"Result is not a dict: {type(result)} - {result}")
                    continue
                    
                # Handle Dgraph vendor data structure
                locations = result.get('has_locations', [])
                location = locations[0] if locations and isinstance(locations[0], dict) else {}
                
                services = result.get('provides_services', [])
                service_names = [s.get('service_name', 'N/A') for s in services if isinstance(s, dict)] if services else []
                services_str = ', '.join(service_names[:2]) + ('...' if len(service_names) > 2 else '')
                
                rows.append([
                    result.get('name', 'N/A'),
                    f"{result.get('rating', 0):.1f}/5.0",
                    result.get('established_year', 'N/A'),
                    services_str or 'N/A',
                    f"{location.get('city', 'N/A')}, {location.get('state', 'N/A')}",
                    result.get('email', 'N/A')
                ])
        
        elif intent == QueryIntent.SERVICE_FILTER:
            headers = ["Service", "Category", "Description", "Vendor", "Rating", "Location", "Contact"]
            rows = []
            for result in results:
                # Debug: Check if result is a dict
                if not isinstance(result, dict):
                    logger.error(f"Result is not a dict: {type(result)} - {result}")
                    continue
                    
                # Handle Dgraph service data structure
                vendor = result.get('provided_by_vendor', {})
                if not isinstance(vendor, dict):
                    vendor = {}
                    
                locations = vendor.get('has_locations', [])
                location = locations[0] if locations and isinstance(locations[0], dict) else {}
                
                rows.append([
                    result.get('service_name', 'N/A'),
                    result.get('category', 'N/A'),
                    result.get('service_description', 'N/A')[:50] + "..." if len(result.get('service_description', '')) > 50 else result.get('service_description', 'N/A'),
                    vendor.get('name', 'N/A'),
                    f"{vendor.get('rating', 0):.1f}/5.0",
                    f"{location.get('city', 'N/A')}, {location.get('state', 'N/A')}",
                    vendor.get('email', 'N/A')
                ])
        
        elif intent == QueryIntent.COMPLEX_PRICING:
            headers = ["Vendor", "Service", "Category", "Pricing Type", "Price", "Currency", "Unit", "Discount", "Location", "City", "Country Code"]
            rows = []
            for result in results:
                rows.append([
                    result.get('vendor_name', 'N/A'),
                    result.get('service_name', 'N/A'),
                    result.get('category', 'Technology'),
                    result.get('pricing_type', 'N/A'),
                    f"${result.get('base_price', 0):,.2f}",
                    result.get('currency', 'USD'),
                    result.get('unit', 'N/A'),
                    f"{result.get('discount_percentage', 0):.1f}%",
                    result.get('location', 'Main Office'),
                    result.get('city', 'San Francisco'),
                    result.get('country_code', 'US')
                ])
        
        else:  # Default table format
            headers = ["Vendor", "Rating", "Service", "Category", "Price", "Location", "Contact"]
            rows = []
            for result in results:
                rows.append([
                    result.get('name', 'N/A'),
                    f"{result.get('rating', 0):.1f}/5.0",
                    result.get('service_name', 'N/A'),
                    result.get('category', 'N/A'),
                    f"${result.get('base_price', 0):,.2f}",
                    f"{result.get('city', 'N/A')}, {result.get('state', 'N/A')}",
                    result.get('email', 'N/A')
                ])
        
        return {
            "headers": headers,
            "rows": rows,
            "summary": f"Found {len(results)} result(s)",
            "total_results": len(results)
        }

    def _generate_response_content(self, original_query: str, table_data: Dict[str, Any], parsed_query) -> str:
        """Generate response content with table formatting"""
        if not table_data["rows"]:
            return f"❌ **No results found** for your query: \"{original_query}\"\n\nTry adjusting your search criteria or ask for help with different parameters."
        
        # Start building response
        response = f"📊 **Query Results** for: \"{original_query}\"\n\n"
        response += f"**{table_data['summary']}**\n\n"
        
        # Add table
        response += "```\n"
        
        # Calculate column widths
        headers = table_data["headers"]
        col_widths = [len(header) for header in headers]
        
        for row in table_data["rows"]:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Add padding
        col_widths = [width + 2 for width in col_widths]
        
        # Print header
        header_row = "|"
        for i, header in enumerate(headers):
            header_row += f" {header:<{col_widths[i]-1}}|"
        response += header_row + "\n"
        
        # Print separator
        separator = "|"
        for width in col_widths:
            separator += "-" * width + "|"
        response += separator + "\n"
        
        # Print rows
        for row in table_data["rows"]:
            row_str = "|"
            for i, cell in enumerate(row):
                row_str += f" {str(cell):<{col_widths[i]-1}}|"
            response += row_str + "\n"
        
        response += "```\n\n"
        
        # Add insights based on query type
        if parsed_query.intent == QueryIntent.COST_ANALYSIS:
            prices = [float(row[4].replace('$', '').replace(',', '')) for row in table_data["rows"] if row[4] != 'N/A']
            if prices:
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                response += f"💰 **Cost Analysis:**\n"
                response += f"• Average Price: ${avg_price:,.2f}\n"
                response += f"• Price Range: ${min_price:,.2f} - ${max_price:,.2f}\n\n"
        
        elif parsed_query.intent == QueryIntent.RATING_FILTER:
            ratings = [float(row[1].split('/')[0]) for row in table_data["rows"] if row[1] != 'N/A']
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                response += f"⭐ **Rating Analysis:**\n"
                response += f"• Average Rating: {avg_rating:.1f}/5.0\n"
                response += f"• Top Rated: {max(ratings):.1f}/5.0\n\n"
        
        # Add query details
        response += f"🔍 **Query Details:**\n"
        response += f"• Intent: {parsed_query.intent.value.replace('_', ' ').title()}\n"
        response += f"• Criteria: {len(parsed_query.criteria)} filter(s) applied\n"
        if parsed_query.sql_query:
            response += f"• Database: PostgreSQL + Dgraph (Hybrid)\n"
        
        return response

    def _merge_hybrid_results(self, dgraph_results: List[Dict], postgres_results: List[Dict]) -> List[Dict]:
        """Merge results from Dgraph and PostgreSQL"""
        # Create a mapping of vendor names to Dgraph data
        dgraph_map = {vendor['name']: vendor for vendor in dgraph_results}
        
        # Enhance PostgreSQL results with Dgraph relationship data
        enhanced_results = []
        for postgres_result in postgres_results:
            vendor_name = postgres_result.get('name')
            if vendor_name in dgraph_map:
                dgraph_vendor = dgraph_map[vendor_name]
                # Merge the data
                enhanced_result = {**postgres_result}
                enhanced_result['dgraph_locations'] = dgraph_vendor.get('has_locations', [])
                enhanced_result['dgraph_services'] = dgraph_vendor.get('provides_services', [])
                enhanced_results.append(enhanced_result)
            else:
                enhanced_results.append(postgres_result)
        
        return enhanced_results

    async def _enhance_pricing_with_dgraph_data(self, pricing_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance pricing results with Dgraph data for category and location details"""
        try:
            logger.info(f"Enhancing {len(pricing_results)} pricing results with Dgraph data")
            # Get all vendors and services from Dgraph
            dgraph_vendors = await dgraph_client.query_all_vendors()
            dgraph_services = await dgraph_client.query_all_services()
            logger.info(f"Got {len(dgraph_vendors)} vendors and {len(dgraph_services)} services from Dgraph")
            
            # Create lookup maps
            vendor_map = {}
            for vendor in dgraph_vendors:
                vendor_map[vendor.get('name', '')] = vendor
            
            service_map = {}
            for service in dgraph_services:
                service_map[service.get('service_name', '')] = service
            
            # Enhance pricing results
            enhanced_results = []
            for pricing_result in pricing_results:
                vendor_dgraph_uid = pricing_result.get('vendor_dgraph_uid', '')
                service_dgraph_uid = pricing_result.get('service_dgraph_uid', '')
                
                # Find vendor by Dgraph UID
                vendor_data = {}
                for vendor in dgraph_vendors:
                    if vendor.get('uid') == vendor_dgraph_uid:
                        vendor_data = vendor
                        break
                
                # Find service by Dgraph UID
                service_data = {}
                for service in dgraph_services:
                    if service.get('uid') == service_dgraph_uid:
                        service_data = service
                        break
                
                locations = vendor_data.get('has_locations', [])
                # Check if location is a dict (expanded) or string (reference)
                location = {}
                if locations and isinstance(locations[0], dict):
                    location = locations[0]
                
                # Create enhanced result
                enhanced_result = pricing_result.copy()
                enhanced_result['vendor_name'] = vendor_data.get('name', 'N/A')
                enhanced_result['service_name'] = service_data.get('service_name', 'N/A')
                enhanced_result['category'] = service_data.get('category', 'Technology')
                enhanced_result['location'] = location.get('address', 'Main Office') if location else 'Main Office'
                enhanced_result['city'] = location.get('city', 'San Francisco') if location else 'San Francisco'
                enhanced_result['country_code'] = location.get('country', 'US') if location else 'US'
                
                enhanced_results.append(enhanced_result)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error enhancing pricing data with Dgraph: {e}")
            # Return original results with placeholder values
            for result in pricing_results:
                result['category'] = 'Technology'
                result['location'] = 'Main Office'
                result['city'] = 'San Francisco'
                result['country_code'] = 'US'
            return pricing_results

    async def _get_database_connection(self):
        """Get PostgreSQL database connection"""
        return await asyncpg.connect(
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )

    def can_handle(self, query: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Check if this agent can handle the query"""
        vendor_keywords = [
            "vendor", "vendors", "company", "companies", "service", "services",
            "location", "city", "where", "address", "cost", "price", "pricing", 
            "rate", "rates", "rating", "score", "established", "year", "compare",
            "list", "show", "find", "get", "more than", "less than", "above", "below"
        ]
        query_lower = query.lower()
        
        # Calculate confidence score based on keyword matches
        matches = sum(1 for keyword in vendor_keywords if keyword in query_lower)
        if matches > 0:
            return min(1.0, matches / len(vendor_keywords) + 0.8)  # High confidence for advanced agent
        return 0.0
