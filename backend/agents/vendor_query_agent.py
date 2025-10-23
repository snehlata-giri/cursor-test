"""
Vendor Query Agent for handling vendor-related queries
"""

from typing import Dict, List, Any, Optional
import re
import asyncio
import asyncpg
from agents.base_agent import BaseAgent, AgentResponse
from app.core.config import settings


class VendorQueryAgent(BaseAgent):
    """Agent for handling vendor-related queries and database operations"""
    
    def __init__(self):
        super().__init__(
            agent_id="vendor_query_agent",
            name="Vendor Query Agent",
            description="Handles vendor-related queries including location searches, cost inquiries, and service listings.",
            capabilities=["vendor_search", "location_query", "cost_analysis", "service_listing", "vendor_comparison"]
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
        
        if any(word in query_lower for word in ["location", "city", "where", "address"]):
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
        """Handle queries about vendor locations"""
        # Extract location from query
        location = self._extract_location(query)
        
        if not location:
            return AgentResponse(
                content="Please specify a location (city, state, or country) to search for vendors.",
                agent_id=self.agent_id,
                agent_name=self.name,
                type="assistant"
            )
        
        # Query database for vendors in the specified location
        vendors = await self._get_vendors_by_location(location)
        
        if not vendors:
            return AgentResponse(
                content=f"No vendors found in {location}.",
                agent_id=self.agent_id,
                agent_name=self.name,
                type="assistant"
            )
        
        # Format response
        response_content = f"Found {len(vendors)} vendor(s) in {location}:\n\n"
        for vendor in vendors:
            response_content += f"🏢 **{vendor['name']}**\n"
            response_content += f"📍 {vendor['address']}, {vendor['city']}, {vendor['state']}\n"
            response_content += f"⭐ Rating: {vendor['rating']}/5.0\n"
            response_content += f"📞 {vendor['phone']}\n"
            response_content += f"🌐 {vendor['website']}\n\n"
        
        return AgentResponse(
            content=response_content,
            agent_id=self.agent_id,
            agent_name=self.name,
            type="assistant",
            metadata={"query_type": "location_search", "location": location, "vendor_count": len(vendors)}
        )

    async def _handle_cost_inquiry(self, query: str) -> AgentResponse:
        """Handle queries about vendor costs and pricing"""
        # Extract vendor name from query
        vendor_name = self._extract_vendor_name(query)
        
        if not vendor_name:
            return AgentResponse(
                content="Please specify a vendor name to get pricing information.",
                agent_id=self.agent_id,
                agent_name=self.name,
                type="assistant"
            )
        
        # Query database for vendor pricing
        pricing_info = await self._get_vendor_pricing(vendor_name)
        
        if not pricing_info:
            return AgentResponse(
                content=f"No pricing information found for {vendor_name}.",
                agent_id=self.agent_id,
                agent_name=self.name,
                type="assistant"
            )
        
        # Format response
        response_content = f"💰 **Pricing Information for {vendor_name}**\n\n"
        for service in pricing_info:
            response_content += f"🔧 **{service['service_name']}**\n"
            response_content += f"📋 Category: {service['category']}\n"
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
        """Handle queries about vendor services"""
        # Extract vendor name or service category from query
        vendor_name = self._extract_vendor_name(query)
        category = self._extract_category(query)
        
        if vendor_name:
            services = await self._get_vendor_services(vendor_name)
            if not services:
                return AgentResponse(
                    content=f"No services found for {vendor_name}.",
                    agent_id=self.agent_id,
                    agent_name=self.name,
                    type="assistant"
                )
            
            response_content = f"🔧 **Services offered by {vendor_name}**\n\n"
            for service in services:
                response_content += f"• **{service['service_name']}** ({service['category']})\n"
                response_content += f"  {service['description']}\n\n"
        else:
            services = await self._get_services_by_category(category) if category else await self._get_all_services()
            if not services:
                return AgentResponse(
                    content="No services found.",
                    agent_id=self.agent_id,
                    agent_name=self.name,
                    type="assistant"
                )
            
            response_content = f"🔧 **Available Services**\n\n"
            for service in services:
                response_content += f"• **{service['service_name']}** by {service['vendor_name']} ({service['category']})\n"
                response_content += f"  {service['description']}\n\n"
        
        return AgentResponse(
            content=response_content,
            agent_id=self.agent_id,
            agent_name=self.name,
            type="assistant",
            metadata={"query_type": "service_listing", "vendor": vendor_name, "category": category}
        )

    async def _handle_vendor_info(self, query: str) -> AgentResponse:
        """Handle general vendor information queries"""
        vendor_name = self._extract_vendor_name(query)
        
        if not vendor_name:
            # List all vendors
            vendors = await self._get_all_vendors()
            response_content = "🏢 **Available Vendors**\n\n"
            for vendor in vendors:
                response_content += f"• **{vendor['name']}** (Rating: {vendor['rating']}/5.0)\n"
                response_content += f"  {vendor['description']}\n\n"
        else:
            # Get specific vendor info
            vendor_info = await self._get_vendor_details(vendor_name)
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
            if vendor_info['locations']:
                response_content += "📍 **Locations:**\n"
                for location in vendor_info['locations']:
                    response_content += f"• {location['address']}, {location['city']}, {location['state']}\n"
        
        return AgentResponse(
            content=response_content,
            agent_id=self.agent_id,
            agent_name=self.name,
            type="assistant",
            metadata={"query_type": "vendor_info", "vendor": vendor_name}
        )

    async def _handle_general_vendor_query(self, query: str) -> AgentResponse:
        """Handle general vendor-related queries"""
        return AgentResponse(
            content="I can help you with vendor information! Try asking:\n\n"
                   "• 'Show me vendors in [city/state]'\n"
                   "• 'What services does [vendor name] offer?'\n"
                   "• 'What is the cost for [vendor name]?'\n"
                   "• 'List all vendors'\n"
                   "• 'Tell me about [vendor name]'",
            agent_id=self.agent_id,
            agent_name=self.name,
            type="assistant"
        )

    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from query"""
        # Simple extraction - look for common location patterns
        location_patterns = [
            r"in\s+([A-Za-z\s]+)",
            r"from\s+([A-Za-z\s]+)",
            r"at\s+([A-Za-z\s]+)",
            r"location\s+([A-Za-z\s]+)",
            r"city\s+([A-Za-z\s]+)"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None

    def _extract_vendor_name(self, query: str) -> Optional[str]:
        """Extract vendor name from query"""
        # Look for vendor names in the mock data
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
        """Get database connection"""
        return await asyncpg.connect(
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )

    async def _get_vendors_by_location(self, location: str) -> List[Dict[str, Any]]:
        """Get vendors by location"""
        conn = await self._get_database_connection()
        try:
            query = """
                SELECT v.name, vl.address, vl.city, vl.state, v.rating, v.phone, v.website
                FROM vendors v
                JOIN vendor_locations vl ON v.id = vl.vendor_id
                WHERE LOWER(vl.city) LIKE LOWER($1) 
                   OR LOWER(vl.state) LIKE LOWER($1)
                   OR LOWER(vl.country) LIKE LOWER($1)
                ORDER BY v.rating DESC
            """
            rows = await conn.fetch(query, f"%{location}%")
            return [dict(row) for row in rows]
        finally:
            await conn.close()

    async def _get_vendor_pricing(self, vendor_name: str) -> List[Dict[str, Any]]:
        """Get vendor pricing information"""
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

    async def _get_vendor_services(self, vendor_name: str) -> List[Dict[str, Any]]:
        """Get services for a specific vendor"""
        conn = await self._get_database_connection()
        try:
            query = """
                SELECT vs.service_name, vs.category, vs.description
                FROM vendors v
                JOIN vendor_services vs ON v.id = vs.vendor_id
                WHERE LOWER(v.name) LIKE LOWER($1)
                ORDER BY vs.service_name
            """
            rows = await conn.fetch(query, f"%{vendor_name}%")
            return [dict(row) for row in rows]
        finally:
            await conn.close()

    async def _get_services_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get services by category"""
        conn = await self._get_database_connection()
        try:
            query = """
                SELECT vs.service_name, vs.category, vs.description, v.name as vendor_name
                FROM vendor_services vs
                JOIN vendors v ON vs.vendor_id = v.id
                WHERE LOWER(vs.category) LIKE LOWER($1)
                ORDER BY v.name, vs.service_name
            """
            rows = await conn.fetch(query, f"%{category}%")
            return [dict(row) for row in rows]
        finally:
            await conn.close()

    async def _get_all_services(self) -> List[Dict[str, Any]]:
        """Get all services"""
        conn = await self._get_database_connection()
        try:
            query = """
                SELECT vs.service_name, vs.category, vs.description, v.name as vendor_name
                FROM vendor_services vs
                JOIN vendors v ON vs.vendor_id = v.id
                ORDER BY v.name, vs.service_name
            """
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
        finally:
            await conn.close()

    async def _get_all_vendors(self) -> List[Dict[str, Any]]:
        """Get all vendors"""
        conn = await self._get_database_connection()
        try:
            query = """
                SELECT name, rating, description
                FROM vendors
                ORDER BY rating DESC, name
            """
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
        finally:
            await conn.close()

    async def _get_vendor_details(self, vendor_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed vendor information"""
        conn = await self._get_database_connection()
        try:
            # Get vendor info
            vendor_query = """
                SELECT name, email, phone, website, rating, established_year, description
                FROM vendors
                WHERE LOWER(name) LIKE LOWER($1)
            """
            vendor_row = await conn.fetchrow(vendor_query, f"%{vendor_name}%")
            
            if not vendor_row:
                return None
            
            vendor_info = dict(vendor_row)
            
            # Get locations
            locations_query = """
                SELECT address, city, state, country
                FROM vendor_locations
                WHERE vendor_id = (SELECT id FROM vendors WHERE LOWER(name) LIKE LOWER($1))
            """
            location_rows = await conn.fetch(locations_query, f"%{vendor_name}%")
            vendor_info['locations'] = [dict(row) for row in location_rows]
            
            return vendor_info
        finally:
            await conn.close()

    def can_handle(self, query: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Check if this agent can handle the query"""
        vendor_keywords = [
            "vendor", "vendors", "company", "companies", "service", "services",
            "location", "city", "where", "address", "cost", "price", "pricing", "rate", "rates"
        ]
        query_lower = query.lower()
        
        # Calculate confidence score based on keyword matches
        matches = sum(1 for keyword in vendor_keywords if keyword in query_lower)
        if matches > 0:
            return min(1.0, matches / len(vendor_keywords) + 0.5)  # Higher confidence for more matches
        return 0.0
