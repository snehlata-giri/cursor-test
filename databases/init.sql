-- Initialize PostgreSQL database for Vendor Management System
-- This script sets up the database schema and initial data

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create agents table
CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    capabilities JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create API endpoints table
CREATE TABLE IF NOT EXISTS api_endpoints (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    url VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL DEFAULT 'GET',
    headers JSONB,
    auth_type VARCHAR(50),
    auth_config JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER,
    timeout INTEGER DEFAULT 30,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create messages table with vector column for embeddings
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    agent_id INTEGER REFERENCES agents(id),
    metadata JSONB,
    embedding VECTOR(1536), -- OpenAI embedding dimension
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create agent capabilities table
CREATE TABLE IF NOT EXISTS agent_capabilities (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES agents(id) ON DELETE CASCADE,
    capability_name VARCHAR(100) NOT NULL,
    description TEXT,
    keywords JSONB
);

-- Create agent-API endpoint mapping table
CREATE TABLE IF NOT EXISTS agent_api_endpoints (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES agents(id) ON DELETE CASCADE,
    api_endpoint_id INTEGER REFERENCES api_endpoints(id) ON DELETE CASCADE,
    UNIQUE(agent_id, api_endpoint_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_agent_id ON messages(agent_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_capabilities_agent_id ON agent_capabilities(agent_id);

-- Create vector similarity search index
CREATE INDEX IF NOT EXISTS idx_messages_embedding ON messages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Insert initial agents
INSERT INTO agents (name, description, capabilities, config) VALUES
('conversation_agent', 'Conversation Agent', '["conversation", "chat", "general questions", "small talk", "explanations", "advice"]', '{"model": "gpt-3.5-turbo", "temperature": 0.7}'),
('data_retrieval_agent', 'Data Retrieval Agent', '["weather data", "news retrieval", "api calls", "data fetching", "external services", "real-time data"]', '{"timeout": 30, "retry_attempts": 3}'),
('computation_agent', 'Computation Agent', '["mathematical calculations", "data processing", "statistical analysis", "unit conversions", "formula evaluation", "computation"]', '{"precision": 4}')
ON CONFLICT (name) DO NOTHING;

-- Insert initial API endpoints
INSERT INTO api_endpoints (name, description, url, method, auth_type, auth_config) VALUES
('weather_api', 'OpenWeatherMap API', 'http://api.openweathermap.org/data/2.5/weather', 'GET', 'api_key', '{"key_param": "appid"}'),
('news_api', 'NewsAPI', 'https://newsapi.org/v2/top-headlines', 'GET', 'api_key', '{"key_param": "apiKey"}')
ON CONFLICT (name) DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_api_endpoints_updated_at BEFORE UPDATE ON api_endpoints FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add triggers for vendor management tables
CREATE TRIGGER update_vendors_updated_at BEFORE UPDATE ON vendors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_vendor_locations_updated_at BEFORE UPDATE ON vendor_locations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_vendor_services_updated_at BEFORE UPDATE ON vendor_services FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_service_pricing_updated_at BEFORE UPDATE ON service_pricing FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_service_reviews_updated_at BEFORE UPDATE ON service_reviews FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a function for vector similarity search
CREATE OR REPLACE FUNCTION search_similar_messages(query_embedding VECTOR(1536), similarity_threshold FLOAT DEFAULT 0.7, limit_count INTEGER DEFAULT 10)
RETURNS TABLE (
    id INTEGER,
    content TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.id,
        m.content,
        1 - (m.embedding <=> query_embedding) AS similarity
    FROM messages m
    WHERE m.embedding IS NOT NULL
    AND 1 - (m.embedding <=> query_embedding) > similarity_threshold
    ORDER BY m.embedding <=> query_embedding
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Vendor Management Tables

-- Create vendors table
CREATE TABLE IF NOT EXISTS vendors (
    id SERIAL PRIMARY KEY,
    dgraph_id VARCHAR(50) UNIQUE NOT NULL, -- Reference to Dgraph vendor node
    name VARCHAR(200) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    website VARCHAR(200),
    rating DECIMAL(3,2) DEFAULT 0.0,
    established_year INTEGER,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create vendor_locations table
CREATE TABLE IF NOT EXISTS vendor_locations (
    id SERIAL PRIMARY KEY,
    dgraph_id VARCHAR(50) UNIQUE NOT NULL, -- Reference to Dgraph location node
    vendor_id INTEGER REFERENCES vendors(id) ON DELETE CASCADE,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    country VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    is_primary BOOLEAN DEFAULT FALSE,
    phone VARCHAR(20),
    email VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create vendor_services table
CREATE TABLE IF NOT EXISTS vendor_services (
    id SERIAL PRIMARY KEY,
    dgraph_id VARCHAR(50) UNIQUE NOT NULL, -- Reference to Dgraph service node
    vendor_id INTEGER REFERENCES vendors(id) ON DELETE CASCADE,
    service_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create service_pricing table for cost tracking
CREATE TABLE IF NOT EXISTS service_pricing (
    id SERIAL PRIMARY KEY,
    vendor_service_id INTEGER REFERENCES vendor_services(id) ON DELETE CASCADE,
    pricing_type VARCHAR(50) NOT NULL, -- 'hourly', 'fixed', 'per_unit', 'monthly'
    base_price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    unit VARCHAR(50), -- 'hour', 'project', 'item', 'month'
    minimum_quantity INTEGER DEFAULT 1,
    maximum_quantity INTEGER,
    discount_percentage DECIMAL(5, 2) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    valid_from TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create service_reviews table
CREATE TABLE IF NOT EXISTS service_reviews (
    id SERIAL PRIMARY KEY,
    vendor_service_id INTEGER REFERENCES vendor_services(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    cost_rating INTEGER CHECK (cost_rating >= 1 AND cost_rating <= 5),
    quality_rating INTEGER CHECK (quality_rating >= 1 AND quality_rating <= 5),
    timeliness_rating INTEGER CHECK (timeliness_rating >= 1 AND timeliness_rating <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert mock data for vendors
INSERT INTO vendors (dgraph_id, name, email, phone, website, rating, established_year, description) VALUES
('vendor_001', 'TechSolutions Inc', 'contact@techsolutions.com', '+1-555-0101', 'https://techsolutions.com', 4.5, 2015, 'Leading technology solutions provider specializing in cloud infrastructure and software development.'),
('vendor_002', 'GreenEnergy Corp', 'info@greenenergy.com', '+1-555-0102', 'https://greenenergy.com', 4.2, 2018, 'Sustainable energy solutions and environmental consulting services.'),
('vendor_003', 'DataAnalytics Pro', 'hello@dataanalytics.com', '+1-555-0103', 'https://dataanalytics.com', 4.7, 2020, 'Advanced data analytics and business intelligence solutions.'),
('vendor_004', 'CreativeDesign Studio', 'studio@creativedesign.com', '+1-555-0104', 'https://creativedesign.com', 4.3, 2017, 'Full-service design agency specializing in branding, web design, and marketing materials.'),
('vendor_005', 'LogisticsMaster', 'support@logisticsmaster.com', '+1-555-0105', 'https://logisticsmaster.com', 4.1, 2012, 'Comprehensive logistics and supply chain management services.')
ON CONFLICT (dgraph_id) DO NOTHING;

-- Insert mock data for vendor locations
INSERT INTO vendor_locations (dgraph_id, vendor_id, address, city, state, country, postal_code, latitude, longitude, is_primary, phone, email) VALUES
('loc_001', 1, '123 Tech Street, Suite 100', 'San Francisco', 'California', 'USA', '94105', 37.7749, -122.4194, true, '+1-555-0101', 'sf@techsolutions.com'),
('loc_002', 1, '456 Innovation Drive', 'Austin', 'Texas', 'USA', '78701', 30.2672, -97.7431, false, '+1-555-0101', 'austin@techsolutions.com'),
('loc_003', 2, '789 Green Avenue', 'Portland', 'Oregon', 'USA', '97201', 45.5152, -122.6784, true, '+1-555-0102', 'portland@greenenergy.com'),
('loc_004', 3, '321 Data Center Blvd', 'Seattle', 'Washington', 'USA', '98101', 47.6062, -122.3321, true, '+1-555-0103', 'seattle@dataanalytics.com'),
('loc_005', 4, '654 Design District', 'New York', 'New York', 'USA', '10001', 40.7505, -73.9934, true, '+1-555-0104', 'nyc@creativedesign.com'),
('loc_006', 5, '987 Logistics Way', 'Chicago', 'Illinois', 'USA', '60601', 41.8781, -87.6298, true, '+1-555-0105', 'chicago@logisticsmaster.com')
ON CONFLICT (dgraph_id) DO NOTHING;

-- Insert mock data for vendor services
INSERT INTO vendor_services (dgraph_id, vendor_id, service_name, category, description, is_active) VALUES
('svc_001', 1, 'Cloud Infrastructure Setup', 'Technology', 'Complete cloud infrastructure setup and migration services including AWS, Azure, and GCP.', true),
('svc_002', 1, 'Software Development', 'Technology', 'Custom software development services including web applications, mobile apps, and APIs.', true),
('svc_003', 2, 'Solar Panel Installation', 'Energy', 'Residential and commercial solar panel installation and maintenance services.', true),
('svc_004', 2, 'Energy Audit', 'Energy', 'Comprehensive energy audit services to identify efficiency improvements and cost savings.', true),
('svc_005', 3, 'Data Analytics Consulting', 'Analytics', 'Advanced data analytics consulting including machine learning and predictive modeling.', true),
('svc_006', 3, 'Business Intelligence Dashboard', 'Analytics', 'Custom business intelligence dashboards and reporting solutions.', true),
('svc_007', 4, 'Brand Identity Design', 'Design', 'Complete brand identity design including logo, color palette, and brand guidelines.', true),
('svc_008', 4, 'Web Design & Development', 'Design', 'Custom website design and development services with responsive design.', true),
('svc_009', 5, 'Supply Chain Optimization', 'Logistics', 'Supply chain analysis and optimization services to improve efficiency and reduce costs.', true),
('svc_010', 5, 'Warehouse Management', 'Logistics', 'Complete warehouse management solutions including inventory tracking and optimization.', true)
ON CONFLICT (dgraph_id) DO NOTHING;

-- Insert mock data for service pricing
INSERT INTO service_pricing (vendor_service_id, pricing_type, base_price, currency, unit, minimum_quantity, maximum_quantity, discount_percentage, is_active) VALUES
(1, 'fixed', 15000.00, 'USD', 'project', 1, 1, 0.0, true),
(1, 'hourly', 150.00, 'USD', 'hour', 40, 200, 10.0, true),
(2, 'hourly', 120.00, 'USD', 'hour', 20, 1000, 5.0, true),
(2, 'fixed', 25000.00, 'USD', 'project', 1, 1, 0.0, true),
(3, 'per_unit', 500.00, 'USD', 'panel', 10, 100, 15.0, true),
(3, 'fixed', 8000.00, 'USD', 'installation', 1, 1, 0.0, true),
(4, 'fixed', 2500.00, 'USD', 'audit', 1, 1, 0.0, true),
(4, 'hourly', 200.00, 'USD', 'hour', 8, 40, 0.0, true),
(5, 'hourly', 180.00, 'USD', 'hour', 20, 500, 12.0, true),
(5, 'fixed', 12000.00, 'USD', 'project', 1, 1, 0.0, true),
(6, 'fixed', 8000.00, 'USD', 'dashboard', 1, 1, 0.0, true),
(6, 'monthly', 500.00, 'USD', 'month', 3, 24, 20.0, true),
(7, 'fixed', 5000.00, 'USD', 'package', 1, 1, 0.0, true),
(7, 'hourly', 100.00, 'USD', 'hour', 10, 100, 0.0, true),
(8, 'fixed', 12000.00, 'USD', 'website', 1, 1, 0.0, true),
(8, 'hourly', 80.00, 'USD', 'hour', 20, 200, 5.0, true),
(9, 'fixed', 20000.00, 'USD', 'analysis', 1, 1, 0.0, true),
(9, 'hourly', 250.00, 'USD', 'hour', 40, 200, 15.0, true),
(10, 'monthly', 2000.00, 'USD', 'month', 6, 36, 10.0, true),
(10, 'fixed', 15000.00, 'USD', 'setup', 1, 1, 0.0, true)
ON CONFLICT DO NOTHING;
