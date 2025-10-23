"""
Dynamic Query Parser for Natural Language to SQL/Dgraph Translation
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class QueryIntent(Enum):
    VENDOR_LIST = "vendor_list"
    COST_ANALYSIS = "cost_analysis"
    LOCATION_SEARCH = "location_search"
    SERVICE_FILTER = "service_filter"
    COMPARISON = "comparison"
    RELATIONSHIP_ANALYSIS = "relationship_analysis"
    COMPLEX_FILTER = "complex_filter"
    RATING_FILTER = "rating_filter"
    TIME_FILTER = "time_filter"
    COMPLEX_PRICING = "complex_pricing"


@dataclass
class QueryCriteria:
    """Represents a single query criterion"""
    field: str
    operator: str
    value: Any
    data_type: str  # 'string', 'number', 'date', 'boolean'


@dataclass
class ParsedQuery:
    """Represents a parsed natural language query"""
    intent: QueryIntent
    criteria: List[QueryCriteria]
    original_query: str = ""
    order_by: Optional[str] = None
    order_direction: str = "ASC"
    limit: Optional[int] = None
    needs_relationships: bool = False
    sql_query: Optional[str] = None
    dgraph_query: Optional[str] = None


class QueryParser:
    """Parses natural language queries into structured database queries"""
    
    def __init__(self):
        self.operator_mapping = {
            "more than": ">",
            "greater than": ">",
            "above": ">",
            "less than": "<",
            "below": "<",
            "under": "<",
            "equal to": "=",
            "equals": "=",
            "between": "BETWEEN",
            "in": "IN",
            "like": "LIKE",
            "contains": "LIKE"
        }
        
        self.field_mapping = {
            "cost": "spn.base_price",
            "price": "spn.base_price",
            "pricing": "spn.base_price",
            "rate": "spn.base_price",
            "rating": "v.rating",
            "score": "v.rating",
            "year": "v.established_year",
            "established": "v.established_year",
            "city": "vl.city",
            "state": "vl.state",
            "location": "vl.city",
            "service": "vs.service_name",
            "category": "vs.category",
            "vendor": "v.name",
            "company": "v.name",
            "name": "v.name"
        }
        
        self.pricing_type_mapping = {
            "monthly": "monthly",
            "per month": "monthly",
            "hourly": "hourly",
            "per hour": "hourly",
            "fixed": "fixed",
            "per project": "fixed",
            "per unit": "per_unit",
            "per item": "per_unit"
        }

    def parse_query(self, query: str) -> ParsedQuery:
        """Parse a natural language query into structured components"""
        query_lower = query.lower()
        
        # Determine intent
        intent = self._classify_intent(query_lower)
        
        # Extract criteria
        criteria = self._extract_criteria(query_lower)
        
        # Determine if relationships are needed
        needs_relationships = self._needs_relationships(query_lower)
        
        # Generate SQL and Dgraph queries
        sql_query = self._generate_sql_query(intent, criteria)
        dgraph_query = self._generate_dgraph_query(intent, criteria) if needs_relationships else None
        
        return ParsedQuery(
            intent=intent,
            criteria=criteria,
            original_query=query,
            needs_relationships=needs_relationships,
            sql_query=sql_query,
            dgraph_query=dgraph_query
        )

    def _classify_intent(self, query: str) -> QueryIntent:
        """Classify the intent of the query"""
        query_lower = query.lower()
        print(f"DEBUG: Classifying query: '{query_lower}'")
        
        # Check for complex pricing queries first (highest priority)
        if any(word in query_lower for word in ["service", "services"]) and any(word in query_lower for word in ["pricing", "price", "cost", "monthly", "greater than", "less than", "above", "below"]):
            print("DEBUG: Classified as COMPLEX_PRICING")
            return QueryIntent.COMPLEX_PRICING
        # Check for simple pricing queries
        elif any(word in query_lower for word in ["pricing details", "pricing information", "show me pricing", "pricing table"]):
            print("DEBUG: Classified as COMPLEX_PRICING (simple pricing)")
            return QueryIntent.COMPLEX_PRICING
        # Check for location queries
        elif any(word in query_lower for word in ["location", "city", "state", "where", "address", "in ", "from "]):
            print("DEBUG: Classified as LOCATION_SEARCH")
            return QueryIntent.LOCATION_SEARCH
        # Check for service queries
        elif any(word in query_lower for word in ["service", "services", "offering", "provide"]):
            print("DEBUG: Classified as SERVICE_FILTER")
            return QueryIntent.SERVICE_FILTER
        # Check for pricing/cost queries
        elif any(word in query for word in ["cost", "price", "pricing", "rate", "expensive", "cheap", "pricing details", "with pricing"]):
            return QueryIntent.COST_ANALYSIS
        # Check for rating queries
        elif any(word in query for word in ["rating", "score", "best", "top", "worst"]):
            return QueryIntent.RATING_FILTER
        # Check for time queries
        elif any(word in query for word in ["established", "year", "founded", "since"]):
            return QueryIntent.TIME_FILTER
        # Check for comparison queries
        elif any(word in query for word in ["compare", "versus", "vs", "difference"]):
            return QueryIntent.COMPARISON
        # Check for relationship queries
        elif any(word in query for word in ["relationship", "network", "connected", "similar"]):
            return QueryIntent.RELATIONSHIP_ANALYSIS
        # Check for simple vendor list queries
        elif any(word in query for word in ["list", "show", "find", "get", "all"]) and not any(word in query for word in ["cost", "price", "pricing", "service", "services"]):
            return QueryIntent.VENDOR_LIST
        else:
            return QueryIntent.COMPLEX_FILTER

    def _extract_criteria(self, query: str) -> List[QueryCriteria]:
        """Extract query criteria from natural language"""
        criteria = []
        
        # Extract cost/price criteria
        cost_patterns = [
            r"(?:cost|price|pricing|rate)s?\s+(?:more than|greater than|above)\s+(\$?[\d,]+)",
            r"(?:cost|price|pricing|rate)s?\s+(?:less than|below|under)\s+(\$?[\d,]+)",
            r"(?:cost|price|pricing|rate)s?\s+(?:between)\s+(\$?[\d,]+)\s+(?:and|to)\s+(\$?[\d,]+)",
            r"(?:cost|price|pricing|rate)s?\s+(?:equal to|equals)\s+(\$?[\d,]+)"
        ]
        
        for pattern in cost_patterns:
            matches = re.finditer(pattern, query)
            for match in matches:
                if "more than" in match.group(0) or "greater than" in match.group(0) or "above" in match.group(0):
                    value = self._parse_number(match.group(1))
                    criteria.append(QueryCriteria("spn.base_price", ">", value, "number"))
                elif "less than" in match.group(0) or "below" in match.group(0) or "under" in match.group(0):
                    value = self._parse_number(match.group(1))
                    criteria.append(QueryCriteria("spn.base_price", "<", value, "number"))
                elif "between" in match.group(0):
                    value1 = self._parse_number(match.group(1))
                    value2 = self._parse_number(match.group(2))
                    criteria.append(QueryCriteria("spn.base_price", "BETWEEN", (value1, value2), "number"))
                elif "equal" in match.group(0):
                    value = self._parse_number(match.group(1))
                    criteria.append(QueryCriteria("spn.base_price", "=", value, "number"))
        
        # Extract pricing type
        for pricing_type, db_type in self.pricing_type_mapping.items():
            if pricing_type in query:
                criteria.append(QueryCriteria("spn.pricing_type", "=", db_type, "string"))
        
        # Extract location criteria
        location_patterns = [
            r"(?:in|from|at)\s+([A-Za-z\s]+?)(?:\s|$)",
            r"(?:city|state|location)\s+(?:is|of)\s+([A-Za-z\s]+?)(?:\s|$)"
        ]
        
        for pattern in location_patterns:
            matches = re.finditer(pattern, query)
            for match in matches:
                location = match.group(1).strip()
                if len(location) > 2:  # Avoid very short matches
                    criteria.append(QueryCriteria("vl.city", "LIKE", f"%{location}%", "string"))
        
        # Extract rating criteria
        rating_patterns = [
            r"(?:rating|score)s?\s+(?:more than|greater than|above)\s+([\d.]+)",
            r"(?:rating|score)s?\s+(?:less than|below|under)\s+([\d.]+)",
            r"(?:rating|score)s?\s+(?:equal to|equals)\s+([\d.]+)"
        ]
        
        for pattern in rating_patterns:
            matches = re.finditer(pattern, query)
            for match in matches:
                rating = float(match.group(1))
                if "more than" in match.group(0) or "greater than" in match.group(0) or "above" in match.group(0):
                    criteria.append(QueryCriteria("v.rating", ">", rating, "number"))
                elif "less than" in match.group(0) or "below" in match.group(0) or "under" in match.group(0):
                    criteria.append(QueryCriteria("v.rating", "<", rating, "number"))
                elif "equal" in match.group(0):
                    criteria.append(QueryCriteria("v.rating", "=", rating, "number"))
        
        # Extract service/category criteria
        service_patterns = [
            r"(?:service|services)\s+(?:is|are|like|including)\s+([A-Za-z\s]+?)(?:\s|$)",
            r"(?:category|categories)\s+(?:is|are|like|including)\s+([A-Za-z\s]+?)(?:\s|$)"
        ]
        
        for pattern in service_patterns:
            matches = re.finditer(pattern, query)
            for match in matches:
                service = match.group(1).strip()
                if len(service) > 2:
                    criteria.append(QueryCriteria("vs.service_name", "LIKE", f"%{service}%", "string"))
        
        # Extract year criteria
        year_patterns = [
            r"(?:established|founded|since)\s+(?:after|before|in)\s+(\d{4})",
            r"(?:year|years)\s+(?:after|before|since)\s+(\d{4})"
        ]
        
        for pattern in year_patterns:
            matches = re.finditer(pattern, query)
            for match in matches:
                year = int(match.group(1))
                if "after" in match.group(0) or "since" in match.group(0):
                    criteria.append(QueryCriteria("v.established_year", ">", year, "number"))
                elif "before" in match.group(0):
                    criteria.append(QueryCriteria("v.established_year", "<", year, "number"))
        
        return criteria

    def _needs_relationships(self, query: str) -> bool:
        """Determine if the query needs Dgraph relationships"""
        relationship_keywords = [
            "relationship", "network", "connected", "similar", "overlap",
            "same", "related", "associated", "linked", "service", "services",
            "vendor", "vendors", "location", "locations", "city", "state"
        ]
        return any(keyword in query for keyword in relationship_keywords)

    def _generate_sql_query(self, intent: QueryIntent, criteria: List[QueryCriteria]) -> str:
        """Generate SQL query based on intent and criteria"""
        
        # For service, vendor, and location queries, return None to force Dgraph usage
        if intent in [QueryIntent.SERVICE_FILTER, QueryIntent.VENDOR_LIST, QueryIntent.LOCATION_SEARCH, QueryIntent.RATING_FILTER, QueryIntent.TIME_FILTER]:
            return None
        
        # For complex pricing queries, use hybrid approach with Dgraph UUIDs
        if intent == QueryIntent.COMPLEX_PRICING:
            base_query = """
            SELECT DISTINCT spn.vendor_dgraph_uid, spn.service_dgraph_uid, spn.pricing_type, spn.base_price, 
                   spn.currency, spn.unit, spn.discount_percentage
            FROM service_pricing_new spn
            WHERE spn.is_active = true
            """
        # For simple vendor list queries or rating filters, use a simpler query
        elif (intent == QueryIntent.VENDOR_LIST or intent == QueryIntent.RATING_FILTER) and not any(c.field.startswith('sp.') or c.field.startswith('vs.') for c in criteria):
            base_query = """
            SELECT DISTINCT v.name, v.rating, v.email, v.phone, v.website, v.established_year,
                   v.description, vl.city, vl.state, vl.address,
                   '2023-01-15' as contract_start_date, '2025-01-15' as contract_expiry_date
            FROM vendors v
            LEFT JOIN vendor_locations vl ON v.id = vl.vendor_id
            WHERE 1=1
            """
        else:
            # For queries involving pricing (but not services), use pricing table
            base_query = """
            SELECT DISTINCT spn.vendor_dgraph_uid, spn.service_dgraph_uid, spn.pricing_type, spn.base_price, 
                   spn.currency, spn.unit, spn.discount_percentage
            FROM service_pricing_new spn
            WHERE spn.is_active = true
            """
        
        # Add WHERE conditions
        where_conditions = []
        for criterion in criteria:
            if criterion.operator == "BETWEEN":
                where_conditions.append(f"{criterion.field} BETWEEN {criterion.value[0]} AND {criterion.value[1]}")
            elif criterion.operator == "LIKE":
                where_conditions.append(f"{criterion.field} LIKE '{criterion.value}'")
            else:
                if criterion.data_type == "string":
                    where_conditions.append(f"{criterion.field} {criterion.operator} '{criterion.value}'")
                else:
                    where_conditions.append(f"{criterion.field} {criterion.operator} {criterion.value}")
        
        if where_conditions:
            base_query += " AND " + " AND ".join(where_conditions)
        
        # Add ORDER BY based on intent
        if intent == QueryIntent.COST_ANALYSIS or intent == QueryIntent.COMPLEX_PRICING:
            base_query += " ORDER BY spn.base_price DESC"
        elif intent == QueryIntent.RATING_FILTER:
            base_query += " ORDER BY v.rating DESC"
        elif intent == QueryIntent.TIME_FILTER:
            base_query += " ORDER BY v.established_year DESC"
        else:
            base_query += " ORDER BY v.rating DESC, v.name ASC"
        
        return base_query

    def _generate_dgraph_query(self, intent: QueryIntent, criteria: List[QueryCriteria]) -> str:
        """Generate Dgraph query for relationship analysis and service queries"""
        if intent == QueryIntent.RELATIONSHIP_ANALYSIS:
            return """
            query vendor_relationships {
                vendors(func: has(name)) {
                    name
                    rating
                    established_year
                    has_locations {
                        city
                        state
                        address
                    }
                    provides_services {
                        service_name
                        category
                        description
                    }
                }
            }
            """
        elif intent == QueryIntent.SERVICE_FILTER:
            return """
            query all_services {
                services(func: has(service_name)) {
                    service_name
                    category
                    service_description
                    is_active
                    provided_by_vendor {
                        name
                        rating
                        email
                        phone
                        website
                        established_year
                        description
                        has_locations {
                            city
                            state
                            country
                        }
                    }
                }
            }
            """
        elif intent == QueryIntent.VENDOR_LIST:
            return """
            query all_vendors {
                vendors(func: has(name)) {
                    name
                    rating
                    email
                    phone
                    website
                    established_year
                    description
                    contract_start_date
                    contract_expiry_date
                    has_locations {
                        city
                        state
                        country
                        address
                    }
                    provides_services {
                        service_name
                        category
                    }
                }
            }
            """
        elif intent == QueryIntent.LOCATION_SEARCH:
            return """
            query vendors_by_location {
                vendors(func: has(name)) {
                    name
                    rating
                    email
                    phone
                    website
                    established_year
                    description
                    has_locations {
                        city
                        state
                        country
                        address
                    }
                    provides_services {
                        service_name
                        category
                    }
                }
            }
            """
        elif intent == QueryIntent.RATING_FILTER:
            return """
            query vendors_by_rating {
                vendors(func: has(name)) {
                    name
                    rating
                    email
                    phone
                    website
                    established_year
                    description
                    has_locations {
                        city
                        state
                        country
                        address
                    }
                    provides_services {
                        service_name
                        category
                    }
                }
            }
            """
        elif intent == QueryIntent.TIME_FILTER:
            return """
            query vendors_by_time {
                vendors(func: has(name)) {
                    name
                    rating
                    email
                    phone
                    website
                    established_year
                    description
                    has_locations {
                        city
                        state
                        country
                        address
                    }
                    provides_services {
                        service_name
                        category
                    }
                }
            }
            """
        else:
            return None

    def _parse_number(self, number_str: str) -> float:
        """Parse number string, handling currency symbols and commas"""
        # Remove currency symbols and commas
        cleaned = re.sub(r'[\$,]', '', number_str)
        try:
            return float(cleaned)
        except ValueError:
            return 0.0


# Example usage and testing
if __name__ == "__main__":
    parser = QueryParser()
    
    test_queries = [
        "List all vendors costing more than $10,000 a month",
        "Show me vendors in California with ratings above 4.0",
        "Find technology vendors established after 2015",
        "Vendors with hourly rates under $100",
        "Compare vendors offering cloud services"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        parsed = parser.parse_query(query)
        print(f"Intent: {parsed.intent}")
        print(f"Criteria: {parsed.criteria}")
        print(f"SQL: {parsed.sql_query}")
        if parsed.dgraph_query:
            print(f"Dgraph: {parsed.dgraph_query}")
