"""
Conversation Agent for general chat and conversation
"""

from typing import Dict, List, Any, Optional
import openai
from agents.base_agent import BaseAgent, AgentResponse
from app.core.config import settings


class ConversationAgent(BaseAgent):
    """Agent for general conversation and chat"""
    
    def __init__(self):
        super().__init__(
            agent_id="conversation_agent",
            name="Conversation Agent",
            description="Handles general conversation, questions, and casual chat",
            capabilities=[
                "conversation",
                "chat",
                "general questions",
                "small talk",
                "explanations",
                "advice"
            ]
        )
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process general conversation queries"""
        try:
            # Build conversation context
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant. Provide friendly, informative responses to user questions and engage in natural conversation."
                }
            ]
            
            # Add conversation history if available
            if context and "conversation_history" in context:
                messages.extend(context["conversation_history"][-5:])  # Last 5 messages
            
            # Add current query
            messages.append({
                "role": "user",
                "content": query
            })
            
            # Get response from OpenAI
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            return AgentResponse(
                content=content,
                agent_id=self.agent_id,
                agent_name=self.name,
                metadata={
                    "model": "gpt-3.5-turbo",
                    "tokens_used": response.usage.total_tokens if response.usage else 0
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error processing conversation query: {e}")
            return AgentResponse(
                content="I'm sorry, I'm having trouble processing your request right now. Please try again.",
                agent_id=self.agent_id,
                agent_name=self.name,
                metadata={"error": str(e)}
            )
    
    def can_handle(self, query: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Determine if this agent can handle the query"""
        # This agent can handle most general queries
        general_keywords = [
            "hello", "hi", "how are you", "what", "who", "when", "where", "why", "how",
            "explain", "tell me", "help", "advice", "suggestion", "opinion"
        ]
        
        query_lower = query.lower()
        score = 0.0
        
        for keyword in general_keywords:
            if keyword in query_lower:
                score += 0.2
        
        # Check for specific capabilities
        for capability in self.capabilities:
            if capability.lower() in query_lower:
                score += 0.3
        
        # This agent has a baseline capability for general queries
        if score == 0:
            score = 0.1  # Default confidence for general queries
        
        return min(score, 1.0)
