import React, { useState, useEffect, useRef } from 'react';
import { PlusIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';
import MessageList from './MessageList';
import { useWebSocket } from '../hooks/useWebSocket';

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  timestamp: string;
}

interface Message {
  type: 'user' | 'assistant' | 'system' | 'typing' | 'error';
  content: string;
  agent_id?: string;
  agent_name?: string;
  metadata?: any;
  api_calls?: any[];
  table_data?: {
    headers: string[];
    rows: string[][];
  };
  timestamp?: string;
}

const ChatGPTInterface: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [agentCount, setAgentCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { sendMessage, lastMessage, connectionStatus } = useWebSocket();

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversations, currentConversationId]);

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        const message = JSON.parse(lastMessage);
        console.log('Parsed message:', message);
      
      if (message.type === 'system' && message.content.includes('Connected')) {
        setIsConnected(true);
      } else if (message.type === 'agents_info') {
        setAgentCount(message.agents?.length || 0);
      } else if (message.type === 'all_conversations') {
        setConversations(message.conversations || []);
        if (message.conversations?.length > 0 && !currentConversationId) {
          setCurrentConversationId(message.conversations[0].id);
        }
      } else if (message.type === 'new_conversation') {
        const newConversation: Conversation = {
          id: message.id,
          title: message.title,
          messages: [],
          timestamp: message.timestamp
        };
        setConversations(prev => [newConversation, ...prev]);
        setCurrentConversationId(message.id);
      } else if (message.type === 'user' || message.type === 'assistant' || message.type === 'typing' || message.type === 'error') {
        console.log('Processing message:', message.type, 'conversation_id:', message.conversation_id, 'currentConversationId:', currentConversationId);
        
        // Update the current conversation with the new message
        setConversations(prev => {
          const updatedConversations = prev.map(conv => {
            if (conv.id === message.conversation_id || conv.id === currentConversationId) {
              console.log('Updating conversation:', conv.id);
              const updatedMessages = [...conv.messages];
              
              // Remove any existing typing indicator
              const typingIndex = updatedMessages.findIndex(msg => msg.type === 'typing');
              if (typingIndex !== -1) {
                updatedMessages.splice(typingIndex, 1);
              }
              
              // Add the new message
              updatedMessages.push({
                type: message.type,
                content: message.content,
                agent_id: message.agent_id,
                agent_name: message.agent_name,
                metadata: message.metadata,
                api_calls: message.api_calls,
                table_data: message.table_data || message.metadata?.table_data,
                timestamp: message.timestamp
              });
              
              return {
                ...conv,
                messages: updatedMessages,
                timestamp: message.timestamp
              };
            }
            return conv;
          });
          
          // If no conversation was updated and we have a conversation_id, create a new conversation
          if (message.conversation_id && !updatedConversations.some(conv => conv.id === message.conversation_id)) {
            console.log('Creating new conversation:', message.conversation_id);
            const newConversation: Conversation = {
              id: message.conversation_id,
              title: message.content.substring(0, 50) + (message.content.length > 50 ? '...' : ''),
              messages: [{
                type: message.type,
                content: message.content,
                agent_id: message.agent_id,
                agent_name: message.agent_name,
                metadata: message.metadata,
                api_calls: message.api_calls,
                table_data: message.table_data || message.metadata?.table_data,
                timestamp: message.timestamp
              }],
              timestamp: message.timestamp
            };
            updatedConversations.unshift(newConversation);
            setCurrentConversationId(message.conversation_id);
          }
          
          return updatedConversations;
        });
      }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error, 'Raw message:', lastMessage);
      }
    }
  }, [lastMessage, currentConversationId]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !isConnected) return;

    const messageData = {
      content: inputValue,
      conversation_id: currentConversationId
    };

    sendMessage(JSON.stringify(messageData));
    setInputValue('');
  };

  const handleNewConversation = () => {
    // Simply clear the current conversation to start fresh
    setCurrentConversationId(null);
    setInputValue('');
  };

  const currentConversation = conversations.find(conv => conv.id === currentConversationId);
  
  // Debug logging
  console.log('Current conversations:', conversations);
  console.log('Current conversation ID:', currentConversationId);
  console.log('Current conversation:', currentConversation);

  return (
    <div className="chat-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h2 className="sidebar-title">Conversations</h2>
          <button 
            className="new-chat-button"
            onClick={handleNewConversation}
            title="New conversation"
          >
            <PlusIcon />
          </button>
        </div>
        
        <div className="sidebar-content">
          {conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`conversation-item ${conversation.id === currentConversationId ? 'active' : ''}`}
              onClick={() => setCurrentConversationId(conversation.id)}
            >
              <h3 className="conversation-title">{conversation.title}</h3>
              <p className="conversation-meta">
                {new Date(conversation.timestamp).toLocaleString()} • {conversation.messages.length} messages
              </p>
            </div>
          ))}
        </div>
        
        <div className="sidebar-footer">
          <div className="status-indicator">
            <div className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></div>
            <span className="status-text">{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
          <div className="agent-count">{agentCount} agents available</div>
        </div>
      </div>

      {/* Main Area */}
      <div className="main-area">
        <div className="header">
          <div className="header-left">
            <button className="header-button" title="Menu">
              <ChatBubbleLeftRightIcon />
            </button>
            <div>
              <h1 className="header-title">Vendor Management System</h1>
              <p className="header-subtitle">Ask complex questions about vendors, costs, and services</p>
            </div>
          </div>
        </div>

        <div className="chat-area">
          <div className="chat-container-main">
            <div className="messages-area">
              {currentConversation ? (
                <MessageList messages={currentConversation.messages} />
              ) : (
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  height: '100%',
                  color: '#6b7280',
                  fontSize: '1.125rem'
                }}>
                  {isConnected ? 'Select a conversation or start a new one' : 'Connecting...'}
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="input-area">
              <form className="input-form" onSubmit={handleSendMessage}>
                <div className="input-container">
                  <textarea
                    className="input-textarea"
                    placeholder={isConnected ? "Ask about vendors, costs, locations... (Shift+Enter for new line)" : "Connecting..."}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage(e);
                      }
                    }}
                    disabled={!isConnected}
                    rows={1}
                  />
                </div>
                <button
                  type="submit"
                  className="send-button"
                  disabled={!inputValue.trim() || !isConnected}
                >
                  <PaperAirplaneIcon />
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatGPTInterface;