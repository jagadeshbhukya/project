import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { conversationAPI } from '../../lib/api';
import { Conversation } from '../../types';
import { Plus, MessageSquare, Trash2, LogOut, Settings, Brain } from 'lucide-react';
import { formatRelativeTime, truncateText } from '../../lib/utils';

interface SidebarProps {
  conversations: Conversation[];
  activeConversation: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  activeConversation,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
}) => {
  const { user, logout } = useAuth();
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div className={`${isCollapsed ? 'w-16' : 'w-80'} bg-gray-900 text-white flex flex-col transition-all duration-300`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <div className="flex items-center gap-2">
              <Brain className="w-6 h-6 text-blue-400" />
              <h1 className="font-semibold text-lg">AI Assistant</h1>
            </div>
          )}
          <button
            onClick={onNewConversation}
            className="p-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
            title="New Conversation"
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {conversations.map((conversation) => (
          <div
            key={conversation.id}
            className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
              activeConversation === conversation.id
                ? 'bg-blue-600'
                : 'bg-gray-800 hover:bg-gray-700'
            }`}
            onClick={() => onSelectConversation(conversation.id)}
          >
            <div className="flex items-center gap-3 flex-1 min-w-0">
              <MessageSquare className="w-4 h-4 flex-shrink-0" />
              {!isCollapsed && (
                <div className="min-w-0 flex-1">
                  <div className="font-medium text-sm">
                    {truncateText(conversation.title || 'New Conversation', 25)}
                  </div>
                  <div className="text-xs text-gray-400">
                    {formatRelativeTime(conversation.updatedAt)}
                  </div>
                </div>
              )}
            </div>
            {!isCollapsed && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteConversation(conversation.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-600 rounded transition-all"
                title="Delete Conversation"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        ))}
      </div>

      {/* User Profile */}
      <div className="border-t border-gray-700 p-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <span className="text-sm font-semibold">
              {user?.name?.charAt(0).toUpperCase()}
            </span>
          </div>
          {!isCollapsed && (
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{user?.name}</div>
              <div className="text-xs text-gray-400 truncate">{user?.email}</div>
            </div>
          )}
        </div>
        
        {!isCollapsed && (
          <div className="mt-3 flex gap-2">
            <button
              className="flex-1 p-2 bg-gray-800 hover:bg-gray-700 rounded-lg flex items-center justify-center gap-2 text-sm transition-colors"
              title="Settings"
            >
              <Settings className="w-4 h-4" />
              Settings
            </button>
            <button
              onClick={logout}
              className="flex-1 p-2 bg-red-600 hover:bg-red-700 rounded-lg flex items-center justify-center gap-2 text-sm transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        )}
      </div>
    </div>
  );
};