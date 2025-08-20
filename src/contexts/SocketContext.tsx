import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { io, Socket } from 'socket.io-client';
import { useAuth } from './AuthContext';
import type { Message } from '../types';

interface SocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  sendMessage: (conversationId: string, content: string) => void;
  onMessageReceived: (callback: (message: Message) => void) => void;
  onTypingIndicator: (callback: (data: { conversationId: string; isTyping: boolean }) => void) => void;
}

const SocketContext = createContext<SocketContextType | undefined>(undefined);

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (context === undefined) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};

interface SocketProviderProps {
  children: ReactNode;
}

export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      const token = localStorage.getItem('access_token');
      const newSocket = io('http://localhost:8000', {
        auth: {
          token,
        },
      });

      newSocket.on('connect', () => {
        setIsConnected(true);
        console.log('Connected to WebSocket');
      });

      newSocket.on('disconnect', () => {
        setIsConnected(false);
        console.log('Disconnected from WebSocket');
      });

      setSocket(newSocket);

      return () => {
        newSocket.close();
      };
    } else {
      setSocket(null);
      setIsConnected(false);
    }
  }, [user]);

  const sendMessage = (conversationId: string, content: string) => {
    if (socket) {
      socket.emit('send_message', {
        conversation_id: conversationId,
        content,
      });
    }
  };

  const onMessageReceived = (callback: (message: Message) => void) => {
    if (socket) {
      socket.on('message_received', callback);
    }
  };

  const onTypingIndicator = (callback: (data: { conversationId: string; isTyping: boolean }) => void) => {
    if (socket) {
      socket.on('typing_indicator', callback);
    }
  };

  const value = {
    socket,
    isConnected,
    sendMessage,
    onMessageReceived,
    onTypingIndicator,
  };

  return <SocketContext.Provider value={value}>{children}</SocketContext.Provider>;
};