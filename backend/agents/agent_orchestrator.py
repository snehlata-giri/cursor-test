"""
Agent Orchestrator for routing queries to appropriate agents
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from enum import Enum
from agents.base_agent import BaseAgent, AgentResponse
from agents.semantic_search_agent import SemanticSearchAgent
from agents.advanced_vendor_agent import AdvancedVendorAgent
from agents.conversation_agent import ConversationAgent

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries that can be routed to different agents"""
    SEMANTIC_SEARCH = "semantic_search"
    VENDOR_QUERY = "vendor_query"
    CONVERSATION = "conversation"
    VECTOR_SEARCH = "vector_search"
    HYBRID_SEARCH = "hybrid_search"


class AgentOrchestrator:
    """Orchestrates queries to appropriate agents based on intent and context"""
    
    def __init__(self):
        self.agents = {
            "semantic_search": SemanticSearchAgent(),
            "vendor_agent": AdvancedVendorAgent(),
            "conversation": ConversationAgent()
        }
        self.query_classifier = QueryClassifier()
    
    async def process_query(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """Route query to appropriate agent and return response"""
        try:
            logger.info(f"Orchestrating query: {query}")
            
            # Classify the query type
            query_type = await self.query_classifier.classify_query(query, context)
            logger.info(f"Classified query as: {query_type}")
            
            # Route to appropriate agent
            if query_type == QueryType.SEMANTIC_SEARCH:
                return await self.agents["semantic_search"].process_query(query, context)
            elif query_type == QueryType.VENDOR_QUERY:
                return await self.agents["vendor_agent"].process_query(query, context)
            elif query_type == QueryType.CONVERSATION:
                return await self.agents["conversation"].process_query(query, context)
            elif query_type == QueryType.HYBRID_SEARCH:
                return await self._hybrid_processing(query, context)
            else:
                # Default to semantic search for unknown queries
                return await self.agents["semantic_search"].process_query(query, context)
                
        except Exception as e:
            logger.error(f"Error in agent orchestration: {e}")
            return AgentResponse(
                agent_id="orchestrator",
                agent_name="Agent Orchestrator",
                content=f"Error processing query: {str(e)}",
                table_data={"headers": [], "rows": [], "summary": "Processing failed"}
            )
    
    async def _hybrid_processing(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """Process query using multiple agents and combine results"""
        try:
            logger.info("Performing hybrid processing")
            
            # Get results from multiple agents
            semantic_result = await self.agents["semantic_search"].process_query(query, context)
            vendor_result = await self.agents["vendor_agent"].process_query(query, context)
            
            # Combine results
            combined_table = self._combine_agent_results(semantic_result, vendor_result)
            
            return AgentResponse(
                agent_id="orchestrator",
                agent_name="Agent Orchestrator",
                content=f"Hybrid search results combining semantic and vendor data for: '{query}'",
                table_data=combined_table,
                metadata={
                    "processing_type": "hybrid",
                    "agents_used": ["semantic_search", "vendor_agent"],
                    "semantic_results": len(semantic_result.table_data.get("rows", [])),
                    "vendor_results": len(vendor_result.table_data.get("rows", []))
                }
            )
            
        except Exception as e:
            logger.error(f"Error in hybrid processing: {e}")
            return AgentResponse(
                agent_id="orchestrator",
                agent_name="Agent Orchestrator",
                content=f"Error in hybrid processing: {str(e)}",
                table_data={"headers": [], "rows": [], "summary": "Hybrid processing failed"}
            )
    
    def _combine_agent_results(
        self, 
        semantic_result: AgentResponse, 
        vendor_result: AgentResponse
    ) -> Dict[str, Any]:
        """Combine results from multiple agents"""
        combined_rows = []
        
        # Add semantic search results
        if semantic_result.table_data and semantic_result.table_data.get("rows"):
            for row in semantic_result.table_data["rows"]:
                combined_rows.append(["SEMANTIC"] + row)
        
        # Add vendor query results
        if vendor_result.table_data and vendor_result.table_data.get("rows"):
            for row in vendor_result.table_data["rows"]:
                combined_rows.append(["VENDOR"] + row)
        
        # Create combined headers
        headers = ["Source"] + (semantic_result.table_data.get("headers", []) if semantic_result.table_data else [])
        
        return {
            "headers": headers,
            "rows": combined_rows,
            "summary": f"Combined results: {len(combined_rows)} total items"
        }
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available agents for WebSocket connections"""
        return self.query_classifier.get_available_agents()


class QueryClassifier:
    """Classifies queries to determine which agent should handle them"""
    
    def __init__(self):
        self.semantic_keywords = [
            "similar", "like", "related", "semantic", "context", "meaning",
            "find similar", "recommend", "suggest", "match", "alike"
        ]
        self.vendor_keywords = [
            "vendor", "vendors", "company", "companies", "provider", "providers",
            "list", "show", "find", "search", "rating", "price", "cost", "location",
            "service", "services", "pricing", "monthly", "greater than", "less than"
        ]
        self.conversation_keywords = [
            "hello", "hi", "help", "what", "how", "explain", "tell me about",
            "conversation", "chat", "talk"
        ]
    
    async def classify_query(self, query: str, context: Dict[str, Any]) -> QueryType:
        """Classify query based on content and context"""
        query_lower = query.lower()
        
        # Check for vendor-specific queries first (highest priority for pricing/service queries)
        if any(keyword in query_lower for keyword in self.vendor_keywords):
            return QueryType.VENDOR_QUERY
        
        # Check for semantic search indicators
        if any(keyword in query_lower for keyword in self.semantic_keywords):
            return QueryType.SEMANTIC_SEARCH
        
        # Check for conversation queries
        if any(keyword in query_lower for keyword in self.conversation_keywords):
            return QueryType.CONVERSATION
        
        # Check context for hybrid search
        if context.get("require_hybrid", False):
            return QueryType.HYBRID_SEARCH
        
        # Default to semantic search for complex queries
        if len(query.split()) > 3:
            return QueryType.SEMANTIC_SEARCH
        
        # Default to vendor query for simple queries
        return QueryType.VENDOR_QUERY
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available agents for WebSocket connections"""
        return [
            {
                "id": "semantic_search",
                "name": "Semantic Search Agent",
                "description": "Handles semantic similarity searches",
                "status": "available"
            },
            {
                "id": "vendor_agent", 
                "name": "Advanced Vendor Agent",
                "description": "Handles vendor, service, and pricing queries",
                "status": "available"
            },
            {
                "id": "conversation",
                "name": "Conversation Agent", 
                "description": "Handles general conversation and help queries",
                "status": "available"
            }
        ]