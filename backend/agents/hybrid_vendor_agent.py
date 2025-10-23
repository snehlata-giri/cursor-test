"""
Hybrid Vendor Query Agent that uses both PostgreSQL and Dgraph
"""

from typing import Dict, List, Any, Optional
import asyncio
import asyncpg
from agents.base_agent import BaseAgent, AgentResponse
from app.core.config import settings
from app.core.dgraph_client import dgraph_client


class HybridVendorAgent(BaseAgent):
    """Hybrid agent that uses both PostgreSQL for cost data and Dgraph for relationships"""
    
    def __init__(self):
        super().__init__(
            agent_id="hybrid_vendor_agent",
            name="Hybrid Vendor Agent",
            description="Advanced vendor queries using both PostgreSQL and Dgraph for comprehensive results.",
            capabilities=["vendor_search", "location_query", "cost_analysis", "service_listing", "relationship_analysis"]
        )

    async def process_query(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        try:
            # Parse the query to determine the type of request
            query_type = self._parse_query_type(query)
            
            if query_type == "location_search":
                return await self._handle_location_search(query)
            elif query_type == "cost_inquiry":
                return await self._handle_cost_inquiry(query)
            elif query_type == "service_listing":
                return await self._handle_service_listing(query)
            elif query_type == "vendor_info":
                return await self._handle_vendor_info(query)
            elif query_type == "relationship_query":
                return await self._handle_relationship_query(query)
            else:
                return await self._handle_general_vendor_query(query)
                
        except Exception as e:
            return AgentResponse(
                content=f"Error processing vendor query: {str(e)}",
                agent_id=self.agent_id,
                agent_name=self.name,
                type="error"
            )

    def _parse_query_type(self, query: str) -> str:
        """Parse the query to determine what type of vendor information is being requested"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["relationship", "connected", "related", "network"]):
            return "relationship_query"
        elif any(word in query_lower for word in ["location", "city", "where", "address"]):
            return "location_search"
        elif any(word in query_lower for word in ["cost", "price", "pricing", "how much", "rate"]):
            return "cost_inquiry"
        elif any(word in query_lower for word in ["service", "services", "what do they do", "offer"]):
            return "service_listing"
        elif any(word in query_lower for word in ["vendor", "company", "about", "info", "information"]):
            return "vendor_info"
        else:
            return "general"

    async def _handle_location_search(self, query: str) -> AgentResponse:
        """Handle queries about vendor locations using Dgraph"""
        location = self._extract_location(query)
        
        if not location:
            return AgentResponse(
                content="Please specify a location (city, state, or country) to search for vendors.",
                agent_id=self.agent_id,
                agent_name=self.name,
                type="assistant"
            )
        
        # Query Dgraph for vendors in the specified location
        vendors = await dgraph_client.query_vendors_by_location(location)
        
        if not vendors:
            return AgentResponse(
                content=f"No vendors found in {location}.",
                agent_id=self.agent_id,
                agent_name=self.name,
                type="assistant"
            )
        
        # Format response with rich data from Dgraph
        response_content = f"🏢 **Found {len(vendors)} vendor(s) in {location}:**\n\n"
        for vendor in vendors:
            response_content += f"**{vendor['name']}** ⭐ {vendor['rating']}/5.0\n"
            response_content += f"📧 {vendor['email']} | 📞 {vendor['phone']}\n"
            response_content += f"🌐 {vendor['website']}\n"
            response_content += f"📝 {vendor['description']}\n"
            
            # Show locations
            if vendor.get('has_locations'):
                response_content += "📍 **Locations:**\n"
                for loc in vendor['has_locations']:
                    response_content += f"  • {loc['address']}, {loc['city']}, {loc['state']}\n"
            
            # Show services
            if vendor.get('provides_services'):
                response_content += "🔧 **Services:**\n"
                for service in vendor['provides_services'][:3]:  # Show first 3 services
                    response_content += f"  • {service['service_name']} ({service['category']})\n"
                if len(vendor['provides_services']) > 3:
                    response_content += f"  • ... and {len(vendor['provides_services']) - 3} more services\n"
            
            response_content += "\n"
        
        return AgentResponse(
            content=response_content,
            agent_id=self.agent_id,
            agent_name=self.name,
            type="assistant",
            metadata={"query_type": "location_search", "location": location, "vendor_count": len(vendors)}
        )

    async def _handle_cost_inquiry(self, query: str) -> AgentResponse:
        """Handle queries about vendor costs using PostgreSQL"""
        vendor_name = self._extract_vendor_name(query)
        
        if not vendor_name:
            return AgentResponse(
                content="Please specify a vendor name to get pricing information.",
                agent_id=self.agent_id,
                agent_name=self.name,
                type="assistant"
            )
        
        # Get vendor info from Dgraph
        vendor_info = await dgraph_client.query_vendor_by_name(vendor_name)
        if not vendor_info:
            return AgentResponse(
                content=f"Vendor '{vendor_name}' not found.",
                agent_id=self.agent_id,
                agent_name=self.name,
                type="assistant"
            )
        
        # Get pricing info from PostgreSQL
        pricing_info = await self._get_vendor_pricing(vendor_name)
        
        if not pricing_info:
            return AgentResponse(
                content=f"No pricing information found for {vendor_name}.",
                agent_id=self.agent_id,
                agent_name=self.name,
                type="assistant"
            )
        
        # Format response
        response_content = f"💰 **Pricing Information for {vendor_name}**\n"
        response_content += f"⭐ Rating: {vendor_info['rating']}/5.0\n"
        response_content += f"📧 {vendor_info['email']} | 📞 {vendor_info['phone']}\n\n"
        
        for service in pricing_info:
            response_content += f"🔧 **{service['service_name']}** ({service['category']})\n"
            for pricing in service['pricing']:
                response_content += f"💵 {pricing['pricing_type'].title()}: ${pricing['base_price']:.2f} {pricing['currency']}"
                if pricing['unit']:
                    response_content += f" per {pricing['unit']}"
                if pricing['discount_percentage'] > 0:
                    response_content += f" (Discount: {pricing['discount_percentage']}%)"
                response_content += "\n"
            response_content += "\n"
        
        return AgentResponse(
            content=response_content,
            agent_id=self.agent_id,
            agent_name=self.name,
            type="assistant",
            metadata={"query_type": "cost_inquiry", "vendor": vendor_name}
        )

    async def _handle_service_listing(self, query: str) -> AgentResponse:
        """Handle queries about vendor services using Dgraph"""
        vendor_name = self._extract_vendor_name(query)
        category = self._extract_category(query)
        
        if vendor_name:
            vendor_info = await dgraph_client.query_vendor_by_name(vendor_name)
            if not vendor_info:
                return AgentResponse(
                    content=f"Vendor '{vendor_name}' not found.",
                    agent_id=self.agent_id,
                    agent_name=self.name,
                    type="assistant"
                )
            
            services = vendor_info.get('provides_services', [])
            response_content = f"🔧 **Services offered by {vendor_name}**\n"
            response_content += f"⭐ Rating: {vendor_info['rating']}/5.0\n\n"
            
            for service in services:
                response_content += f"• **{service['service_name']}** ({service['category']})\n"
                response_content += f"  {service['description']}\n"
                response_content += f"  Status: {'✅ Active' if service['is_active'] else '❌ Inactive'}\n\n"
        else:
            if category:
                services = await dgraph_client.query_services_by_category(category)
                response_content = f"🔧 **{category} Services Available**\n\n"
            else:
                # Get all services from all vendors
                vendors = await dgraph_client.query_all_vendors()
                services = []
                for vendor in vendors:
                    for service in vendor.get('provides_services', []):
                        service['vendor_name'] = vendor['name']
                        services.append(service)
                response_content = f"🔧 **All Available Services**\n\n"
            
            for service in services:
                vendor_name = service.get('vendor_name', 'Unknown')
                response_content += f"• **{service['service_name']}** by {vendor_name} ({service['category']})\n"
                response_content += f"  {service['description']}\n\n"
        
        return AgentResponse(
            content=response_content,
            agent_id=self.agent_id,
            agent_name=self.name,
            type="assistant",
            metadata={"query_type": "service_listing", "vendor": vendor_name, "category": category}
        )

    async def _handle_vendor_info(self, query: str) -> AgentResponse:
        """Handle general vendor information queries using Dgraph"""
        vendor_name = self._extract_vendor_name(query)
        
        if not vendor_name:
            # List all vendors
            vendors = await dgraph_client.query_all_vendors()
            response_content = "🏢 **Available Vendors**\n\n"
            for vendor in vendors:
                response_content += f"• **{vendor['name']}** (Rating: {vendor['rating']}/5.0)\n"
                response_content += f"  📧 {vendor['email']} | 📞 {vendor['phone']}\n"
                response_content += f"  📝 {vendor['description']}\n\n"
        else:
            # Get specific vendor info
            vendor_info = await dgraph_client.query_vendor_by_name(vendor_name)
            if not vendor_info:
                return AgentResponse(
                    content=f"Vendor '{vendor_name}' not found.",
                    agent_id=self.agent_id,
                    agent_name=self.name,
                    type="assistant"
                )
            
            response_content = f"🏢 **{vendor_info['name']}**\n\n"
            response_content += f"📧 Email: {vendor_info['email']}\n"
            response_content += f"📞 Phone: {vendor_info['phone']}\n"
            response_content += f"🌐 Website: {vendor_info['website']}\n"
            response_content += f"⭐ Rating: {vendor_info['rating']}/5.0\n"
            response_content += f"📅 Established: {vendor_info['established_year']}\n"
            response_content += f"📝 Description: {vendor_info['description']}\n\n"
            
            # Add locations
            if vendor_info.get('has_locations'):
                response_content += "📍 **Locations:**\n"
                for location in vendor_info['has_locations']:
                    response_content += f"• {location['address']}, {location['city']}, {location['state']}\n"
                    if location.get('is_primary'):
                        response_content += "  (Primary Location)\n"
                response_content += "\n"
            
            # Add services
            if vendor_info.get('provides_services'):
                response_content += "🔧 **Services:**\n"
                for service in vendor_info['provides_services']:
                    response_content += f"• {service['service_name']} ({service['category']})\n"
                response_content += "\n"
        
        return AgentResponse(
            content=response_content,
            agent_id=self.agent_id,
            agent_name=self.name,
            type="assistant",
            metadata={"query_type": "vendor_info", "vendor": vendor_name}
        )

    async def _handle_relationship_query(self, query: str) -> AgentResponse:
        """Handle relationship queries using Dgraph"""
        # This is where Dgraph shines - complex relationship queries
        vendors = await dgraph_client.query_all_vendors()
        
        response_content = "🔗 **Vendor Relationship Analysis**\n\n"
        
        # Analyze vendor-service relationships
        service_categories = {}
        for vendor in vendors:
            for service in vendor.get('provides_services', []):
                category = service['category']
                if category not in service_categories:
                    service_categories[category] = []
                service_categories[category].append(vendor['name'])
        
        response_content += "📊 **Service Category Distribution:**\n"
        for category, vendors_list in service_categories.items():
            response_content += f"• **{category}**: {len(vendors_list)} vendors\n"
            response_content += f"  Vendors: {', '.join(vendors_list)}\n\n"
        
        # Analyze geographic distribution
        locations = {}
        for vendor in vendors:
            for location in vendor.get('has_locations', []):
                city = location['city']
                if city not in locations:
                    locations[city] = []
                locations[city].append(vendor['name'])
        
        response_content += "🌍 **Geographic Distribution:**\n"
        for city, vendors_list in locations.items():
            response_content += f"• **{city}**: {len(vendors_list)} vendors\n"
            response_content += f"  Vendors: {', '.join(vendors_list)}\n\n"
        
        return AgentResponse(
            content=response_content,
            agent_id=self.agent_id,
            agent_name=self.name,
            type="assistant",
            metadata={"query_type": "relationship_query"}
        )

    async def _handle_general_vendor_query(self, query: str) -> AgentResponse:
        """Handle general vendor-related queries"""
        return AgentResponse(
            content="I can help you with vendor information! Try asking:\n\n"
                   "• 'Show me vendors in [city/state]'\n"
                   "• 'What services does [vendor name] offer?'\n"
                   "• 'What is the cost for [vendor name]?'\n"
                   "• 'List all vendors'\n"
                   "• 'Tell me about [vendor name]'\n"
                   "• 'Show vendor relationships and networks'",
            agent_id=self.agent_id,
            agent_name=self.name,
            type="assistant"
        )

    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from query"""
        location_patterns = [
            r"in\s+([A-Za-z\s]+)",
            r"from\s+([A-Za-z\s]+)",
            r"at\s+([A-Za-z\s]+)",
            r"location\s+([A-Za-z\s]+)",
            r"city\s+([A-Za-z\s]+)"
        ]
        
        import re
        for pattern in location_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None

    def _extract_vendor_name(self, query: str) -> Optional[str]:
        """Extract vendor name from query"""
        vendor_names = [
            "TechSolutions Inc", "GreenEnergy Corp", "DataAnalytics Pro", 
            "CreativeDesign Studio", "LogisticsMaster"
        ]
        
        query_lower = query.lower()
        for vendor in vendor_names:
            if vendor.lower() in query_lower:
                return vendor
        
        return None

    def _extract_category(self, query: str) -> Optional[str]:
        """Extract service category from query"""
        categories = ["Technology", "Energy", "Analytics", "Design", "Logistics"]
        query_lower = query.lower()
        
        for category in categories:
            if category.lower() in query_lower:
                return category
        
        return None

    async def _get_database_connection(self):
        """Get PostgreSQL database connection"""
        return await asyncpg.connect(
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )

    async def _get_vendor_pricing(self, vendor_name: str) -> List[Dict[str, Any]]:
        """Get vendor pricing information from PostgreSQL"""
        conn = await self._get_database_connection()
        try:
            query = """
                SELECT vs.service_name, vs.category, 
                       sp.pricing_type, sp.base_price, sp.currency, sp.unit, sp.discount_percentage
                FROM vendors v
                JOIN vendor_services vs ON v.id = vs.vendor_id
                JOIN service_pricing sp ON vs.id = sp.vendor_service_id
                WHERE LOWER(v.name) LIKE LOWER($1)
                ORDER BY vs.service_name, sp.pricing_type
            """
            rows = await conn.fetch(query, f"%{vendor_name}%")
            
            # Group by service
            services = {}
            for row in rows:
                service_name = row['service_name']
                if service_name not in services:
                    services[service_name] = {
                        'service_name': service_name,
                        'category': row['category'],
                        'pricing': []
                    }
                services[service_name]['pricing'].append(dict(row))
            
            return list(services.values())
        finally:
            await conn.close()

    def can_handle(self, query: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Check if this agent can handle the query"""
        vendor_keywords = [
            "vendor", "vendors", "company", "companies", "service", "services",
            "location", "city", "where", "address", "cost", "price", "pricing", 
            "rate", "rates", "relationship", "network", "connected"
        ]
        query_lower = query.lower()
        
        # Calculate confidence score based on keyword matches
        matches = sum(1 for keyword in vendor_keywords if keyword in query_lower)
        if matches > 0:
            return min(1.0, matches / len(vendor_keywords) + 0.6)  # Higher confidence for hybrid agent
        return 0.0


