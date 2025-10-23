"""
Hybrid search service combining Dgraph and PostgreSQL results
"""

import asyncio
import asyncpg
import polars as pl
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from app.core.dgraph_client import dgraph_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class HybridSearchService:
    """Service for hybrid search combining Dgraph nodes and PostgreSQL data"""
    
    def __init__(self):
        self.dgraph_client = dgraph_client
    
    async def search_vendors_with_pricing(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search vendors combining Dgraph vendor data with PostgreSQL pricing data
        """
        try:
            logger.info(f"Hybrid search called with query: '{query}', filters: {filters}")
            
            # Get vendor data from Dgraph
            dgraph_results = await self._search_dgraph_vendors(query, filters)
            logger.info(f"Dgraph results: {len(dgraph_results)} items")
            
            # Get pricing data from PostgreSQL
            pricing_results = await self._get_pricing_data()
            logger.info(f"Pricing results: {len(pricing_results)} items")
            
            # Combine results using Polars for efficient data manipulation
            combined_results = await self._combine_results_with_polars(
                dgraph_results, pricing_results
            )
            logger.info(f"Combined results: {len(combined_results)} items")
            
            return combined_results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    async def _search_dgraph_vendors(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search vendors in Dgraph"""
        try:
            # Build Dgraph query based on search parameters
            if filters and filters.get('location'):
                return await self.dgraph_client.query_vendors_by_location(filters['location'])
            elif filters and filters.get('category'):
                return await self.dgraph_client.query_services_by_category(filters['category'])
            else:
                return await self.dgraph_client.query_all_vendors()
                
        except Exception as e:
            logger.error(f"Error searching Dgraph: {e}")
            return []
    
    async def _get_pricing_data(self) -> List[Dict[str, Any]]:
        """Get pricing data from PostgreSQL"""
        try:
            conn = await asyncpg.connect(
                host=settings.POSTGRES_SERVER,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB
            )
            
            query = """
            SELECT vendor_name, service_name, pricing_type, base_price, 
                   currency, unit, discount_percentage, is_active
            FROM service_pricing_new
            WHERE is_active = true
            ORDER BY base_price DESC
            """
            
            rows = await conn.fetch(query)
            await conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting pricing data: {e}")
            return []
    
    async def _combine_results_with_polars(
        self, 
        dgraph_results: List[Dict[str, Any]], 
        pricing_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combine Dgraph and PostgreSQL results using Polars"""
        try:
            # Convert to Polars DataFrames
            dgraph_df = pl.DataFrame(dgraph_results) if dgraph_results else pl.DataFrame()
            pricing_df = pl.DataFrame(pricing_results) if pricing_results else pl.DataFrame()
            
            if dgraph_df.is_empty() or pricing_df.is_empty():
                return []
            
            # Flatten Dgraph results to get vendor-service combinations
            vendor_services = []
            for vendor in dgraph_results:
                vendor_name = vendor.get('name', '')
                for service in vendor.get('provides_services', []):
                    vendor_services.append({
                        'vendor_name': vendor_name,
                        'service_name': service.get('service_name', ''),
                        'category': service.get('category', ''),
                        'vendor_rating': vendor.get('rating', 0.0),
                        'vendor_email': vendor.get('email', ''),
                        'vendor_phone': vendor.get('phone', ''),
                        'vendor_website': vendor.get('website', ''),
                        'contract_start_date': vendor.get('contract_start_date', ''),
                        'contract_expiry_date': vendor.get('contract_expiry_date', ''),
                        'location_city': vendor.get('has_locations', [{}])[0].get('city', ''),
                        'location_state': vendor.get('has_locations', [{}])[0].get('state', ''),
                        'location_country': vendor.get('has_locations', [{}])[0].get('country', ''),
                        'location_country_code': vendor.get('has_locations', [{}])[0].get('country_code', ''),
                        'location_postal_code': vendor.get('has_locations', [{}])[0].get('postal_code', ''),
                    })
            
            vendor_services_df = pl.DataFrame(vendor_services)
            
            # Join with pricing data
            if not vendor_services_df.is_empty() and not pricing_df.is_empty():
                combined_df = vendor_services_df.join(
                    pricing_df,
                    on=['vendor_name', 'service_name'],
                    how='inner'
                )
                
                # Convert back to list of dictionaries
                return combined_df.to_dicts()
            
            return []
            
        except Exception as e:
            logger.error(f"Error combining results with Polars: {e}")
            return []
    
    async def search_by_vector_similarity(
        self, 
        query_embedding: List[float], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search using vector similarity (pgvector)"""
        try:
            conn = await asyncpg.connect(
                host=settings.POSTGRES_SERVER,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB
            )
            
            # Enable pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # Create vector table if it doesn't exist
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS vendor_embeddings (
                    id SERIAL PRIMARY KEY,
                    vendor_name VARCHAR(200),
                    service_name VARCHAR(200),
                    embedding vector(1536),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create vector index if it doesn't exist
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS vendor_embeddings_embedding_idx 
                ON vendor_embeddings USING ivfflat (embedding vector_cosine_ops)
            """)
            
            # Search for similar vectors
            query = """
            SELECT vendor_name, service_name, 
                   1 - (embedding <=> $1::vector) as similarity
            FROM vendor_embeddings
            ORDER BY embedding <=> $1::vector
            LIMIT $2
            """
            
            rows = await conn.fetch(query, query_embedding, limit)
            await conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error in vector similarity search: {e}")
            return []
    
    async def get_contract_expiring_vendors(
        self, 
        days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """Get vendors with contracts expiring soon"""
        try:
            # Query Dgraph for vendors with expiring contracts
            query = f"""
            query expiring_contracts {{
                vendors(func: le(contract_expiry_date, "{datetime.now().isoformat()}")) {{
                    uid
                    name
                    email
                    phone
                    contract_start_date
                    contract_expiry_date
                    has_locations {{
                        city
                        state
                        country
                    }}
                }}
            }}
            """
            
            # This would need to be implemented in the Dgraph client
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting expiring contracts: {e}")
            return []


# Global instance
hybrid_search_service = HybridSearchService()

