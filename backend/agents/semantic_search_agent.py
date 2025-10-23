"""
Semantic Search Agent with Vector Embeddings and pgvector
"""

import asyncio
import asyncpg
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from agents.base_agent import BaseAgent, AgentResponse
from app.core.config import settings
import json

logger = logging.getLogger(__name__)


class SemanticSearchAgent(BaseAgent):
    """Agent for semantic search using vector embeddings and pgvector"""
    
    def __init__(self):
        super().__init__(
            agent_id="semantic_search_agent",
            name="Semantic Search Agent",
            description="Performs semantic search using vector embeddings and pgvector similarity",
            capabilities=[
                "semantic_search", "vector_similarity", "embedding_search", 
                "contextual_queries", "intent_matching"
            ]
        )
        self.embedding_dim = 1536  # OpenAI embedding dimension

    async def process_query(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """Process semantic search query using vector embeddings"""
        try:
            logger.info(f"Processing semantic search query: {query}")
            
            # Generate embedding for the query (mock for now)
            query_embedding = await self._generate_embedding(query)
            
            # Perform vector similarity search
            similar_results = await self._vector_similarity_search(query_embedding, limit=10)
            
            # Perform semantic search in Dgraph
            dgraph_results = await self._semantic_dgraph_search(query)
            
            # Combine and rank results
            combined_results = await self._combine_and_rank_results(
                similar_results, dgraph_results, query
            )
            
            # Format as table
            table_data = self._format_semantic_results(combined_results, query)
            
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                content=f"Found {len(combined_results)} semantically similar results for: '{query}'",
                table_data=table_data,
                metadata={
                    "search_type": "semantic",
                    "query_embedding": query_embedding[:5],  # First 5 dims for logging
                    "results_count": len(combined_results)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                content=f"Error performing semantic search: {str(e)}",
                table_data={"headers": [], "rows": [], "summary": "Search failed"}
            )

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (mock implementation)"""
        # In production, use OpenAI embeddings or similar
        # For now, create a mock embedding based on text characteristics
        import hashlib
        
        # Create deterministic "embedding" based on text
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to embedding-like vector
        embedding = []
        for i in range(self.embedding_dim):
            byte_idx = i % len(hash_bytes)
            embedding.append((hash_bytes[byte_idx] - 128) / 128.0)
        
        return embedding

    async def _vector_similarity_search(
        self, 
        query_embedding: List[float], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search using pgvector"""
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
            
            # Create vendor_embeddings table if it doesn't exist
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS vendor_embeddings (
                    id SERIAL PRIMARY KEY,
                    vendor_name VARCHAR(200),
                    content TEXT,
                    embedding vector(1536),
                    similarity_score FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create vector index if it doesn't exist
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS vendor_embeddings_embedding_idx
                ON vendor_embeddings USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """)
            
            # Insert some sample embeddings if table is empty
            await self._populate_sample_embeddings(conn)
            
            # Perform similarity search
            query = """
            SELECT vendor_name, content, similarity_score,
                   1 - (embedding <=> $1::vector) as cosine_similarity
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

    async def _populate_sample_embeddings(self, conn):
        """Populate sample embeddings for testing"""
        try:
            # Check if data already exists
            count = await conn.fetchval("SELECT COUNT(*) FROM vendor_embeddings")
            if count > 0:
                return
            
            # Sample vendor combinations with embeddings
            sample_data = [
                ("TechCorp Solutions", "Leading cloud computing and infrastructure services", 0.95),
                ("DataFlow Systems", "Advanced data processing and business intelligence", 0.92),
                ("CloudMaster Inc", "Comprehensive cybersecurity and data protection", 0.88),
                ("SecureNet Pro", "Full-suite IT support and management solutions", 0.85),
                ("Analytics Plus", "AI and ML consulting and implementation", 0.90),
            ]
            
            for vendor, content, score in sample_data:
                embedding = await self._generate_embedding(f"{vendor} {content}")
                
                await conn.execute("""
                    INSERT INTO vendor_embeddings (vendor_name, content, embedding, similarity_score)
                    VALUES ($1, $2, $3, $4)
                """, vendor, content, embedding, score)
            
            logger.info("Populated sample embeddings")
            
        except Exception as e:
            logger.error(f"Error populating sample embeddings: {e}")

    async def _semantic_dgraph_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform semantic search in Dgraph"""
        try:
            # This would integrate with Dgraph's full-text search
            # For now, return mock data
            return [
                {
                    "vendor_name": "TechCorp Solutions",
                    "service_name": "Cloud Infrastructure",
                    "rating": 4.7,
                    "location": "San Francisco, CA",
                    "semantic_score": 0.95
                },
                {
                    "vendor_name": "DataFlow Systems", 
                    "service_name": "Data Analytics",
                    "rating": 4.9,
                    "location": "Austin, TX",
                    "semantic_score": 0.92
                }
            ]
        except Exception as e:
            logger.error(f"Error in Dgraph semantic search: {e}")
            return []

    async def _combine_and_rank_results(
        self, 
        vector_results: List[Dict[str, Any]], 
        dgraph_results: List[Dict[str, Any]], 
        query: str
    ) -> List[Dict[str, Any]]:
        """Combine and rank results from vector and Dgraph search"""
        combined = []
        
        # Add vector results with their similarity scores
        for result in vector_results:
            combined.append({
                **result,
                "search_type": "vector",
                "relevance_score": result.get("cosine_similarity", 0.0)
            })
        
        # Add Dgraph results with their semantic scores
        for result in dgraph_results:
            combined.append({
                **result,
                "search_type": "semantic",
                "relevance_score": result.get("semantic_score", 0.0)
            })
        
        # Sort by relevance score
        combined.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return combined

    def _format_semantic_results(
        self, 
        results: List[Dict[str, Any]], 
        query: str
    ) -> Dict[str, Any]:
        """Format semantic search results as table"""
        if not results:
            return {
                "headers": [],
                "rows": [],
                "summary": f"No semantic matches found for: '{query}'"
            }
        
        headers = [
            "Vendor", "Relevance Score", "Search Type", 
            "Rating", "Location", "Content"
        ]
        
        rows = []
        for result in results:
            rows.append([
                result.get("vendor_name", "N/A"),
                f"{result.get('relevance_score', 0):.3f}",
                result.get("search_type", "N/A"),
                f"{result.get('rating', 0):.1f}/5.0" if result.get('rating') else "N/A",
                result.get("location", "N/A"),
                result.get("content", "N/A")[:50] + "..." if result.get("content") else "N/A"
            ])
        
        return {
            "headers": headers,
            "rows": rows,
            "summary": f"Found {len(results)} semantically relevant results for: '{query}'"
        }
