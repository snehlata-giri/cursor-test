# Troubleshooting Guide - Multi-Agent Chat Application

## Critical Issues Encountered and Solutions

### 1. WebSocket Message Field Mismatch

**Problem:**
- React frontend sends: `{content: "user message", conversation_id: null}`
- Backend expects: `{message: "user message", conversation_id: null}`
- Result: Backend receives empty messages, no responses sent

**Solution:**
```python
# In backend/app/websocket/connection_manager.py
# Changed from:
user_message = message_data.get("message", "")

# To:
user_message = message_data.get("content", "")
```

**Impact:** This was the root cause of the "New Conversation" button not working and no responses appearing.

### 2. Missing conversation_id in WebSocket Responses

**Problem:**
- Backend sends responses without `conversation_id` field
- React app looks for `message.conversation_id` to match messages to conversations
- Result: Messages appear in browser console but not in UI

**Solution:**
```python
# Add conversation_id to all response messages:
await self.send_personal_message({
    "type": "assistant",
    "content": response.content,
    "conversation_id": message_data.get("conversation_id"),  # Added this
    "timestamp": self._get_timestamp()
}, client_id)
```

**Impact:** Messages now display properly in the chat UI.

### 3. CSS Loading Issues in Next.js Production Builds

**Problem:**
- Next.js not loading CSS files in production builds
- Head component and _document.tsx not working properly
- CSS classes present in HTML but styles not applied

**Solution:**
- Switched from Next.js to pure React with Create React App
- CSS now loads automatically via webpack
- No complex configuration needed

**Impact:** Modern, properly styled UI with ChatGPT-like interface.

### 4. WebSocket Connection Lifecycle Issues

**Problem:**
- WebSocket connections establish but immediately close
- No error messages in logs
- Silent failures in message processing

**Debugging Steps:**
1. Check backend logs for WebSocket connection attempts
2. Verify message parsing in connection manager
3. Add comprehensive logging to WebSocket handlers
4. Test WebSocket connection manually

**Solution:**
```python
# Add error handling and logging:
try:
    message_data = json.loads(message_text)
    user_message = message_data.get("content", "")
except json.JSONDecodeError:
    logger.error(f"Failed to parse message: {message_text}")
    return
```

### 5. Database Schema Initialization

**Problem:**
- PostgreSQL errors: "relation does not exist"
- Database tables not created properly
- Backend fails during startup

**Solution:**
- Ensure proper database initialization in FastAPI lifespan
- Check Docker volume mounting for database persistence
- Verify SQLAlchemy model imports

### 6. Docker Container Networking

**Problem:**
- Frontend trying to connect to `localhost:8000` from within container
- CORS issues between containers
- WebSocket connections failing

**Solution:**
- Use service names in docker-compose for internal communication
- Configure CORS properly in FastAPI
- Ensure proper port mapping

## Best Practices Learned

### WebSocket Communication
1. **Always include conversation_id** in response messages
2. **Match field names** between frontend and backend
3. **Add comprehensive error handling** and logging
4. **Test WebSocket connections** manually during development

### Frontend Development
1. **Use React over Next.js** for simpler CSS management
2. **Add debugging logs** to WebSocket message handlers
3. **Handle connection states** properly (connecting, connected, disconnected)
4. **Implement proper error boundaries** for WebSocket failures

### Backend Development
1. **Log all WebSocket events** (connect, disconnect, message)
2. **Validate message structure** before processing
3. **Include all necessary fields** in response messages
4. **Handle database connection issues** gracefully

### Docker Development
1. **Check container logs** regularly during development
2. **Verify network connectivity** between containers
3. **Use proper volume mounting** for data persistence
4. **Test services individually** before integration

## Debugging Commands

```bash
# Check WebSocket connections
docker logs cursor-test-backend-1 | grep -E "(WebSocket|connection)"

# Check database tables
docker exec cursor-test-postgres-1 psql -U postgres -d multi_agent_chat -c "\dt"

# Check frontend build
docker logs cursor-test-frontend-1 --tail 20

# Test WebSocket manually
curl -s http://localhost:8000/health
```

## Common Error Patterns

1. **"No responses in UI"** → Check conversation_id field
2. **"New conversation not working"** → Check message field names
3. **"CSS not loading"** → Switch to React from Next.js
4. **"WebSocket disconnects immediately"** → Check message parsing
5. **"Database errors"** → Check table initialization

This troubleshooting guide should help avoid these issues in future projects.


