# Dynamic Query System

## Overview

The Dynamic Query System allows users to ask complex, natural language questions about vendors and automatically generates optimized SQL and Dgraph queries to retrieve the data in tabular format.

## Features

### 🔍 **Query Types Supported**

1. **Cost Analysis Queries**
   - "List all vendors costing more than $10,000 a month"
   - "Show me vendors with hourly rates under $100"
   - "Find vendors with fixed pricing between $5,000 and $20,000"

2. **Location-Based Queries**
   - "Show me vendors in California"
   - "Find vendors in San Francisco with ratings above 4.0"
   - "List all vendors in Texas"

3. **Service Category Queries**
   - "Find technology vendors"
   - "Show me energy service providers"
   - "List vendors offering cloud services"

4. **Rating & Quality Queries**
   - "Show me vendors with ratings above 4.5"
   - "Find top-rated technology vendors"
   - "List vendors with ratings between 4.0 and 4.5"

5. **Time-Based Queries**
   - "Find vendors established after 2015"
   - "Show me recent vendors (founded since 2020)"
   - "List vendors established before 2010"

6. **Complex Multi-Criteria Queries**
   - "Vendors in California with technology services costing less than $5,000"
   - "Top-rated energy vendors established after 2018"
   - "Technology vendors in San Francisco with hourly rates under $150"

### 🧠 **Natural Language Processing**

The system uses advanced NLP to understand:

- **Operators**: "more than", "less than", "above", "below", "between", "equal to"
- **Entities**: vendor names, locations, services, costs, ratings, years
- **Relationships**: "in", "offering", "providing", "with", "and", "or"
- **Context**: pricing types (monthly, hourly, fixed, per unit)

### 📊 **Tabular Response Format**

All query results are formatted as clean, readable tables with:

- **Headers**: Relevant columns based on query type
- **Data Rows**: Formatted vendor information
- **Summary**: Result count and insights
- **Analysis**: Cost ranges, rating averages, etc.

## Example Queries and Results

### Query: "List all vendors costing more than $10,000 a month"

**Generated SQL:**
```sql
SELECT DISTINCT v.name, v.rating, v.email, v.phone, v.website, v.established_year,
       vs.service_name, vs.category, vs.description,
       sp.pricing_type, sp.base_price, sp.currency, sp.unit, sp.discount_percentage,
       vl.city, vl.state, vl.address
FROM vendors v
JOIN vendor_services vs ON v.id = vs.vendor_id
JOIN service_pricing sp ON vs.id = sp.vendor_service_id
LEFT JOIN vendor_locations vl ON v.id = vl.vendor_id
WHERE sp.is_active = true 
  AND sp.pricing_type = 'monthly' 
  AND sp.base_price > 10000
ORDER BY sp.base_price DESC
```

**Tabular Result:**
```
| Vendor              | Service                    | Category    | Pricing Type | Price      | Currency | Unit  | Discount | Rating |
|---------------------|----------------------------|-------------|--------------|------------|----------|-------|----------|--------|
| DataAnalytics Pro   | Business Intelligence      | Analytics   | monthly      | $500.00    | USD      | month | 20.0%    | 4.7/5.0|
| LogisticsMaster     | Warehouse Management       | Logistics   | monthly      | $2,000.00  | USD      | month | 10.0%    | 4.1/5.0|
```

### Query: "Show me vendors in California with ratings above 4.0"

**Generated SQL:**
```sql
SELECT DISTINCT v.name, v.rating, v.email, v.phone, v.website, v.established_year,
       vs.service_name, vs.category, vs.description,
       sp.pricing_type, sp.base_price, sp.currency, sp.unit, sp.discount_percentage,
       vl.city, vl.state, vl.address
FROM vendors v
JOIN vendor_services vs ON v.id = vs.vendor_id
JOIN service_pricing sp ON vs.id = sp.vendor_service_id
LEFT JOIN vendor_locations vl ON v.id = vl.vendor_id
WHERE sp.is_active = true 
  AND vl.city LIKE '%California%' 
  AND v.rating > 4.0
ORDER BY v.rating DESC, v.name ASC
```

## Architecture

### 🔧 **Components**

1. **Query Parser** (`query_parser.py`)
   - Natural language understanding
   - Intent classification
   - Criteria extraction
   - SQL/Dgraph query generation

2. **Advanced Vendor Agent** (`advanced_vendor_agent.py`)
   - Query execution
   - Result formatting
   - Tabular response generation
   - Hybrid PostgreSQL/Dgraph queries

3. **Agent Orchestrator** (`agent_orchestrator.py`)
   - Agent selection
   - Query routing
   - Response coordination

### 🗄️ **Database Integration**

- **PostgreSQL**: Detailed vendor data, pricing, locations
- **Dgraph**: Relationship analysis, complex graph queries
- **Hybrid Queries**: Combines both databases for comprehensive results

### 🎨 **UI Integration**

- **Modern Chat Interface**: Clean, responsive design
- **Conversation Tracking**: Persistent chat history
- **Tabular Display**: Side-by-side table view
- **Real-time Updates**: WebSocket-based communication

## Usage Examples

### Basic Queries
```
"List all vendors"
"Show me technology vendors"
"Find vendors in San Francisco"
```

### Cost Queries
```
"Vendors costing more than $5,000"
"Show me hourly rates under $100"
"Find fixed pricing between $10,000 and $50,000"
```

### Complex Queries
```
"Technology vendors in California with ratings above 4.0"
"Energy vendors established after 2018 with monthly costs under $2,000"
"Top-rated vendors offering cloud services in San Francisco"
```

### Comparison Queries
```
"Compare technology vendors by cost"
"Show me the best rated energy vendors"
"List vendors by establishment year"
```

## Performance Features

- **Query Optimization**: Automatic SQL optimization
- **Caching**: Redis-based response caching
- **Pagination**: Large result set handling
- **Indexing**: Optimized database indexes
- **Connection Pooling**: Efficient database connections

## Error Handling

- **Invalid Queries**: Graceful error messages
- **No Results**: Helpful suggestions
- **Database Errors**: Fallback responses
- **Network Issues**: Retry mechanisms

## Future Enhancements

- **Machine Learning**: Improved query understanding
- **Voice Queries**: Speech-to-text integration
- **Query Suggestions**: Auto-complete functionality
- **Advanced Analytics**: Trend analysis and insights
- **Export Features**: CSV/Excel export capabilities


