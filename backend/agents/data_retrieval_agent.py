"""
Data Retrieval Agent for external API calls and data fetching
"""

from typing import Dict, List, Any, Optional
import httpx
import json
from agents.base_agent import BaseAgent, AgentResponse
from app.core.config import settings


class DataRetrievalAgent(BaseAgent):
    """Agent for retrieving data from external APIs"""
    
    def __init__(self):
        super().__init__(
            agent_id="data_retrieval_agent",
            name="Data Retrieval Agent",
            description="Fetches data from external APIs like weather, news, and other services",
            capabilities=[
                "weather data",
                "news retrieval",
                "api calls",
                "data fetching",
                "external services",
                "real-time data"
            ]
        )
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process data retrieval queries"""
        try:
            query_lower = query.lower()
            api_calls = []
            
            # Determine which API to call based on query
            if any(keyword in query_lower for keyword in ["weather", "temperature", "forecast", "rain", "sunny"]):
                response_data = await self._get_weather_data(query)
                api_calls.append({"api": "weather", "query": query})
            elif any(keyword in query_lower for keyword in ["news", "headlines", "latest", "current events"]):
                response_data = await self._get_news_data(query)
                api_calls.append({"api": "news", "query": query})
            else:
                # Generic data retrieval response
                response_data = "I can help you retrieve data from various sources. Please specify what type of data you need (weather, news, etc.)."
            
            return AgentResponse(
                content=response_data,
                agent_id=self.agent_id,
                agent_name=self.name,
                metadata={"query_type": "data_retrieval"},
                api_calls=api_calls
            )
            
        except Exception as e:
            self.logger.error(f"Error processing data retrieval query: {e}")
            return AgentResponse(
                content="I'm sorry, I'm having trouble retrieving the data you requested. Please try again later.",
                agent_id=self.agent_id,
                agent_name=self.name,
                metadata={"error": str(e)}
            )
    
    async def _get_weather_data(self, query: str) -> str:
        """Get weather data from OpenWeatherMap API"""
        try:
            if not settings.WEATHER_API_KEY:
                return "Weather API is not configured. Please contact the administrator."
            
            # Extract location from query (simplified)
            location = "London"  # Default location, could be enhanced with NLP
            if "in " in query.lower():
                location = query.lower().split("in ")[-1].split()[0]
            
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": settings.WEATHER_API_KEY,
                "units": "metric"
            }
            
            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return f"""Current weather in {data['name']}:
- Temperature: {data['main']['temp']}°C
- Description: {data['weather'][0]['description']}
- Humidity: {data['main']['humidity']}%
- Wind Speed: {data['wind']['speed']} m/s"""
            
        except httpx.HTTPStatusError as e:
            return f"Error fetching weather data: {e.response.status_code}"
        except Exception as e:
            return f"Error fetching weather data: {str(e)}"
    
    async def _get_news_data(self, query: str) -> str:
        """Get news data from NewsAPI"""
        try:
            if not settings.NEWS_API_KEY:
                return "News API is not configured. Please contact the administrator."
            
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "apiKey": settings.NEWS_API_KEY,
                "country": "us",
                "pageSize": 5
            }
            
            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("articles"):
                return "No news articles found."
            
            news_summary = "Here are the latest headlines:\n\n"
            for article in data["articles"][:3]:
                news_summary += f"• {article['title']}\n"
                if article.get("description"):
                    news_summary += f"  {article['description'][:100]}...\n\n"
            
            return news_summary
            
        except httpx.HTTPStatusError as e:
            return f"Error fetching news data: {e.response.status_code}"
        except Exception as e:
            return f"Error fetching news data: {str(e)}"
    
    def can_handle(self, query: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Determine if this agent can handle the query"""
        query_lower = query.lower()
        score = 0.0
        
        # Check for data retrieval keywords
        data_keywords = [
            "weather", "temperature", "forecast", "rain", "sunny", "cloudy",
            "news", "headlines", "latest", "current events", "breaking",
            "data", "information", "fetch", "get", "retrieve", "api"
        ]
        
        for keyword in data_keywords:
            if keyword in query_lower:
                score += 0.3
        
        # Check for specific capabilities
        for capability in self.capabilities:
            if capability.lower() in query_lower:
                score += 0.2
        
        return min(score, 1.0)
