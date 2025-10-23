# Multi-Agent Chat Application

A sophisticated chat-based application where AI agents automatically select and call the appropriate APIs to respond to user queries. Built with a multi-agent system that intelligently routes requests to specialized agents based on user intent.

## 🚀 Features

- **Multi-Agent System**: Three specialized AI agents for different types of queries
- **Automatic API Routing**: Agents automatically determine which external APIs to call
- **Real-time Chat Interface**: WebSocket-based chat with live agent responses
- **Intelligent Agent Selection**: Vector-based semantic search for optimal agent routing
- **External API Integration**: Weather, news, and other external service integrations
- **Conversation History**: Persistent storage of all chat conversations
- **Containerized Deployment**: Full Docker containerization with orchestration

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.12+
- Node.js (v18 or higher)
- Git

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/multi-agent-chat.git
cd multi-agent-chat
```

2. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your API keys and configuration
```

3. Start all services with Docker Compose:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📖 Usage

### Starting a Conversation

1. Open the application in your browser at http://localhost:3000
2. The system will automatically connect to the multi-agent backend
3. Start typing your message in the chat input
4. The system will automatically route your query to the appropriate agent

### Available Agents

- **Conversation Agent**: Handles general chat, questions, and casual conversation
- **Data Retrieval Agent**: Fetches data from external APIs (weather, news, etc.)
- **Computation Agent**: Performs mathematical calculations and data processing

### Example Queries

- **General Chat**: "Hello, how are you today?"
- **Weather**: "What's the weather like in London?"
- **News**: "What are the latest headlines?"
- **Math**: "Calculate 15 * 23 + 45"
- **Unit Conversion**: "Convert 100 degrees Celsius to Fahrenheit"

## 🏗️ Project Structure

```
multi-agent-chat/
├── frontend/               # React/Next.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Application pages
│   │   ├── hooks/         # Custom React hooks
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   └── package.json
├── backend/               # Python FastAPI backend
│   ├── app/
│   │   ├── core/         # Core configuration
│   │   ├── api/          # API routes
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── websocket/    # WebSocket handlers
│   └── requirements.txt
├── agents/               # Multi-agent system
│   ├── base_agent.py     # Base agent class
│   ├── conversation_agent.py
│   ├── data_retrieval_agent.py
│   ├── computation_agent.py
│   └── agent_orchestrator.py
├── databases/            # Database schemas
│   └── init.sql
├── docker/              # Docker configurations
│   ├── Dockerfile.frontend
│   └── Dockerfile.backend
├── docker-compose.yml   # Container orchestration
└── README.md
```

## 🧪 Testing

### Backend Testing

```bash
cd backend
python -m pytest
```

### Frontend Testing

```bash
cd frontend
npm test
```

## 🚀 Deployment

### Development Mode

```bash
# Start all services in development mode
docker-compose up -d

# View logs
docker-compose logs -f
```

### Production Deployment

```bash
# Build and start production containers
docker-compose -f docker-compose.yml up -d --build

# Scale services if needed
docker-compose up -d --scale backend=3
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting
- Test with Docker containers before submitting

## 🔧 Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

- **OPENAI_API_KEY**: Your OpenAI API key for LLM integration
- **WEATHER_API_KEY**: OpenWeatherMap API key for weather data
- **NEWS_API_KEY**: NewsAPI key for news retrieval
- **Database credentials**: PostgreSQL connection settings
- **Redis settings**: Cache and session storage configuration

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with React, TypeScript, and Python FastAPI
- Styled with Tailwind CSS
- Icons from Heroicons
- Multi-agent orchestration system
- Vector database integration with Pgvector

## 📞 Support

If you have any questions or need help:

- Open an issue on GitHub
- Check the [documentation](docs/)
- Join our community discussions

## 🔮 Roadmap

- [ ] Advanced agent learning and adaptation
- [ ] Multi-agent collaboration for complex queries
- [ ] Integration with more external APIs
- [ ] Advanced analytics and agent performance metrics
- [ ] Mobile application
- [ ] Voice interface integration
- [ ] Custom agent creation interface

## 🏗️ Architecture

### System Components

1. **Frontend**: React/Next.js chat interface with real-time WebSocket communication
2. **Backend**: Python FastAPI with async support and WebSocket handling
3. **Agent System**: Custom multi-agent orchestration with intelligent routing
4. **Databases**: PostgreSQL with Pgvector, Dgraph, and Redis
5. **Containerization**: Full Docker containerization with orchestration

### Data Flow

1. User sends message via WebSocket
2. Agent orchestrator analyzes query intent
3. Appropriate agent is selected based on capabilities
4. Agent processes query and calls external APIs if needed
5. Response is sent back to user via WebSocket
6. Conversation is stored in PostgreSQL with vector embeddings

---

**Happy chatting with AI agents! 🤖💬**
