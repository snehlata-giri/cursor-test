import React from 'react';
import { format } from 'date-fns';

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

interface MessageListProps {
  messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const formatTimestamp = (timestamp?: string) => {
    if (!timestamp) return '';
    try {
      return format(new Date(timestamp), 'HH:mm');
    } catch {
      return '';
    }
  };

  const renderTable = (tableData: { headers: string[]; rows: string[][] }) => {
    if (!tableData || !tableData.headers || !tableData.rows) return null;

    return (
      <div className="message-table-container" style={{ marginTop: '0.5rem', overflowX: 'auto' }}>
        <table className="message-table">
          <thead>
            <tr>
              {tableData.headers.map((header, index) => (
                <th key={index}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tableData.rows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderApiCalls = (apiCalls: any[]) => {
    if (!apiCalls || apiCalls.length === 0) return null;

    return (
      <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#6b7280' }}>
        <details>
          <summary style={{ cursor: 'pointer', marginBottom: '0.25rem' }}>
            API Calls ({apiCalls.length})
          </summary>
          {apiCalls.map((call, index) => (
            <div key={index} style={{ marginLeft: '1rem', marginTop: '0.25rem' }}>
              <strong>{call.api}:</strong> {call.query}
              {call.response && (
                <pre style={{ 
                  fontSize: '0.7rem', 
                  background: '#f3f4f6', 
                  padding: '0.25rem', 
                  borderRadius: '0.25rem',
                  marginTop: '0.25rem',
                  overflow: 'auto'
                }}>
                  {JSON.stringify(call.response, null, 2)}
                </pre>
              )}
            </div>
          ))}
        </details>
      </div>
    );
  };

  if (messages.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '100%',
        color: '#6b7280',
        fontSize: '1.125rem'
      }}>
        No messages yet. Start a conversation!
      </div>
    );
  }

  return (
    <>
      {messages.map((message, index) => {
        if (message.type === 'typing') {
          return (
            <div key={index} className="message assistant">
              <div className="message-content">
                <div className="typing-indicator">
                  <span>Agent is thinking</span>
                  <div className="typing-dots">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              </div>
            </div>
          );
        }

        if (message.type === 'system') {
          return (
            <div key={index} className="message system" style={{ justifyContent: 'center' }}>
              <div className="message-content" style={{ 
                backgroundColor: '#f3f4f6', 
                color: '#6b7280',
                fontSize: '0.875rem',
                textAlign: 'center'
              }}>
                {message.content}
              </div>
            </div>
          );
        }

        return (
          <div key={index} className={`message ${message.type}`}>
            <div className="message-content">
              {message.type === 'assistant' && message.agent_name && (
                <div className="message-header">
                  <span>{message.agent_name}</span>
                  {message.timestamp && (
                    <span>• {formatTimestamp(message.timestamp)}</span>
                  )}
                </div>
              )}
              
              {message.type === 'user' && message.timestamp && (
                <div className="message-header">
                  <span>You</span>
                  <span>• {formatTimestamp(message.timestamp)}</span>
                </div>
              )}

              <p className="message-text">{message.content}</p>
              
              {(message.table_data || message.metadata?.table_data) && renderTable(message.table_data || message.metadata?.table_data)}
              {message.api_calls && renderApiCalls(message.api_calls)}
            </div>
          </div>
        );
      })}
    </>
  );
};

export default MessageList;
