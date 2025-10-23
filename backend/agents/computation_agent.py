"""
Computation Agent for processing and calculation tasks
"""

from typing import Dict, List, Any, Optional
import re
import math
import json
from agents.base_agent import BaseAgent, AgentResponse


class ComputationAgent(BaseAgent):
    """Agent for processing and computation tasks"""
    
    def __init__(self):
        super().__init__(
            agent_id="computation_agent",
            name="Computation Agent",
            description="Handles mathematical calculations, data processing, and computational tasks",
            capabilities=[
                "mathematical calculations",
                "data processing",
                "statistical analysis",
                "unit conversions",
                "formula evaluation",
                "computation"
            ]
        )
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process computation queries"""
        try:
            query_lower = query.lower()
            
            # Determine computation type
            if any(keyword in query_lower for keyword in ["calculate", "compute", "math", "solve"]):
                result = await self._handle_math_calculation(query)
            elif any(keyword in query_lower for keyword in ["convert", "conversion"]):
                result = await self._handle_unit_conversion(query)
            elif any(keyword in query_lower for keyword in ["statistics", "statistical", "analyze"]):
                result = await self._handle_statistical_analysis(query)
            else:
                result = "I can help with mathematical calculations, unit conversions, and data analysis. Please specify what you'd like me to compute."
            
            return AgentResponse(
                content=result,
                agent_id=self.agent_id,
                agent_name=self.name,
                metadata={"query_type": "computation"}
            )
            
        except Exception as e:
            self.logger.error(f"Error processing computation query: {e}")
            return AgentResponse(
                content="I'm sorry, I encountered an error while processing your computation request. Please try again.",
                agent_id=self.agent_id,
                agent_name=self.name,
                metadata={"error": str(e)}
            )
    
    async def _handle_math_calculation(self, query: str) -> str:
        """Handle mathematical calculations"""
        try:
            # Extract mathematical expression from query
            # This is a simplified implementation - could be enhanced with more sophisticated parsing
            
            # Look for common mathematical patterns
            patterns = [
                r'(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)',  # Basic operations
                r'(\d+(?:\.\d+)?)\s*\*\*\s*(\d+(?:\.\d+)?)',  # Exponentiation
                r'sqrt\((\d+(?:\.\d+)?)\)',  # Square root
                r'sin\((\d+(?:\.\d+)?)\)',  # Sine
                r'cos\((\d+(?:\.\d+)?)\)',  # Cosine
                r'tan\((\d+(?:\.\d+)?)\)',  # Tangent
            ]
            
            for pattern in patterns:
                match = re.search(pattern, query)
                if match:
                    if 'sqrt' in pattern:
                        num = float(match.group(1))
                        result = math.sqrt(num)
                        return f"√{num} = {result:.4f}"
                    elif 'sin' in pattern:
                        num = float(match.group(1))
                        result = math.sin(math.radians(num))
                        return f"sin({num}°) = {result:.4f}"
                    elif 'cos' in pattern:
                        num = float(match.group(1))
                        result = math.cos(math.radians(num))
                        return f"cos({num}°) = {result:.4f}"
                    elif 'tan' in pattern:
                        num = float(match.group(1))
                        result = math.tan(math.radians(num))
                        return f"tan({num}°) = {result:.4f}"
                    elif '**' in pattern:
                        base = float(match.group(1))
                        exp = float(match.group(2))
                        result = base ** exp
                        return f"{base}^{exp} = {result:.4f}"
                    else:
                        # Basic arithmetic
                        num1 = float(match.group(1))
                        operator = match.group(2)
                        num2 = float(match.group(3))
                        
                        if operator == '+':
                            result = num1 + num2
                        elif operator == '-':
                            result = num1 - num2
                        elif operator == '*':
                            result = num1 * num2
                        elif operator == '/':
                            if num2 == 0:
                                return "Error: Division by zero is not allowed."
                            result = num1 / num2
                        
                        return f"{num1} {operator} {num2} = {result:.4f}"
            
            # If no pattern matches, try to evaluate as a simple expression
            try:
                # Remove common words and keep only mathematical expressions
                clean_query = re.sub(r'[a-zA-Z\s]', '', query)
                if clean_query:
                    result = eval(clean_query)
                    return f"{clean_query} = {result:.4f}"
            except:
                pass
            
            return "I couldn't parse the mathematical expression. Please provide a clearer calculation request."
            
        except Exception as e:
            return f"Error in calculation: {str(e)}"
    
    async def _handle_unit_conversion(self, query: str) -> str:
        """Handle unit conversions"""
        try:
            # Common conversion factors
            conversions = {
                # Length
                'meter_to_feet': 3.28084,
                'feet_to_meter': 0.3048,
                'kilometer_to_mile': 0.621371,
                'mile_to_kilometer': 1.60934,
                
                # Temperature
                'celsius_to_fahrenheit': lambda c: (c * 9/5) + 32,
                'fahrenheit_to_celsius': lambda f: (f - 32) * 5/9,
                
                # Weight
                'kilogram_to_pound': 2.20462,
                'pound_to_kilogram': 0.453592,
                
                # Volume
                'liter_to_gallon': 0.264172,
                'gallon_to_liter': 3.78541,
            }
            
            # Extract numbers and units from query
            numbers = re.findall(r'\d+(?:\.\d+)?', query)
            if not numbers:
                return "Please provide a number to convert."
            
            value = float(numbers[0])
            query_lower = query.lower()
            
            # Temperature conversions
            if 'celsius' in query_lower or '°c' in query_lower:
                fahrenheit = conversions['celsius_to_fahrenheit'](value)
                return f"{value}°C = {fahrenheit:.2f}°F"
            elif 'fahrenheit' in query_lower or '°f' in query_lower:
                celsius = conversions['fahrenheit_to_celsius'](value)
                return f"{value}°F = {celsius:.2f}°C"
            
            # Length conversions
            elif 'meter' in query_lower and 'feet' in query_lower:
                feet = value * conversions['meter_to_feet']
                return f"{value} meters = {feet:.2f} feet"
            elif 'feet' in query_lower and 'meter' in query_lower:
                meters = value * conversions['feet_to_meter']
                return f"{value} feet = {meters:.2f} meters"
            
            # Weight conversions
            elif 'kilogram' in query_lower and 'pound' in query_lower:
                pounds = value * conversions['kilogram_to_pound']
                return f"{value} kg = {pounds:.2f} lbs"
            elif 'pound' in query_lower and 'kilogram' in query_lower:
                kg = value * conversions['pound_to_kilogram']
                return f"{value} lbs = {kg:.2f} kg"
            
            else:
                return "I can convert between common units like temperature (°C/°F), length (meters/feet), and weight (kg/lbs). Please specify the units."
            
        except Exception as e:
            return f"Error in unit conversion: {str(e)}"
    
    async def _handle_statistical_analysis(self, query: str) -> str:
        """Handle statistical analysis"""
        try:
            # Extract numbers from query
            numbers = re.findall(r'\d+(?:\.\d+)?', query)
            if len(numbers) < 2:
                return "Please provide at least 2 numbers for statistical analysis."
            
            values = [float(num) for num in numbers]
            
            # Calculate basic statistics
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std_dev = math.sqrt(variance)
            min_val = min(values)
            max_val = max(values)
            
            return f"""Statistical Analysis of {values}:
- Count: {len(values)}
- Mean: {mean:.4f}
- Standard Deviation: {std_dev:.4f}
- Minimum: {min_val}
- Maximum: {max_val}
- Range: {max_val - min_val:.4f}"""
            
        except Exception as e:
            return f"Error in statistical analysis: {str(e)}"
    
    def can_handle(self, query: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Determine if this agent can handle the query"""
        query_lower = query.lower()
        score = 0.0
        
        # Check for computation keywords
        computation_keywords = [
            "calculate", "compute", "math", "solve", "equation",
            "convert", "conversion", "statistics", "statistical",
            "analyze", "analysis", "formula", "expression",
            "+", "-", "*", "/", "=", "sqrt", "sin", "cos", "tan"
        ]
        
        for keyword in computation_keywords:
            if keyword in query_lower:
                score += 0.2
        
        # Check for specific capabilities
        for capability in self.capabilities:
            if capability.lower() in query_lower:
                score += 0.3
        
        return min(score, 1.0)
