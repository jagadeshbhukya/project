import React, { useState, useEffect, useRef } from 'react';
import { useSocket } from '../../contexts/SocketContext';
import { conversationAPI } from '../../lib/api';
import { Message, Conversation } from '../../types';
import { Sidebar } from './Sidebar';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';
import { v4 as uuidv4 } from 'uuid';

export const ChatInterface: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { sendMessage, onMessageReceived, onTypingIndicator } = useSocket();

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Set up socket listeners
  useEffect(() => {
    onMessageReceived((message: Message) => {
      setMessages(prev => [...prev, message]);
      setIsTyping(false);
    });

    onTypingIndicator((data) => {
      if (data.conversationId === activeConversation) {
        setIsTyping(data.isTyping);
      }
    });
  }, [activeConversation, onMessageReceived, onTypingIndicator]);

  // Auto scroll to bottom
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const loadConversations = async () => {
    try {
      const data = await conversationAPI.getConversations();
      setConversations(data);
      if (data.length > 0) {
        setActiveConversation(data[0].id);
        loadMessages(data[0].id);
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async (conversationId: string) => {
    try {
      const data = await conversationAPI.getMessages(conversationId);
      setMessages(data);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const createNewConversation = async () => {
    try {
      const newConversation = await conversationAPI.createConversation();
      setConversations(prev => [newConversation, ...prev]);
      setActiveConversation(newConversation.id);
      setMessages([]);
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const selectConversation = async (conversationId: string) => {
    setActiveConversation(conversationId);
    await loadMessages(conversationId);
  };

  const deleteConversation = async (conversationId: string) => {
    try {
      await conversationAPI.deleteConversation(conversationId);
      setConversations(prev => prev.filter(c => c.id !== conversationId));
      
      if (activeConversation === conversationId) {
        const remaining = conversations.filter(c => c.id !== conversationId);
        if (remaining.length > 0) {
          setActiveConversation(remaining[0].id);
          loadMessages(remaining[0].id);
        } else {
          setActiveConversation(null);
          setMessages([]);
        }
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!activeConversation) {
      await createNewConversation();
      return;
    }

    // Add user message immediately
    const userMessage: Message = {
      id: uuidv4(),
      content,
      role: 'user',
      timestamp: new Date().toISOString(),
      conversationId: activeConversation,
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    
    // Send via WebSocket
    sendMessage(activeConversation, content);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="h-screen flex bg-gray-50">
      <Sidebar
        conversations={conversations}
        activeConversation={activeConversation}
        onSelectConversation={selectConversation}
        onNewConversation={createNewConversation}
        onDeleteConversation={deleteConversation}
      />
      
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-900">
            {activeConversation
              ? conversations.find(c => c.id === activeConversation)?.title || 'New Conversation'
              : 'Select a conversation'
            }
          </h2>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && activeConversation && (
            <div className="text-center py-12">
              <div className="text-gray-500 text-lg mb-2">Start a conversation</div>
              <div className="text-gray-400">Ask me anything, and I'll help you with context-aware responses.</div>
            </div>
          )}
          
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          
          <TypingIndicator show={isTyping} />
          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input */}
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={!activeConversation && conversations.length > 0}
          placeholder={
            !activeConversation && conversations.length === 0
              ? "Start your first conversation..."
              : "Type your message here..."
          }
        />
      </div>
    </div>
  );
};