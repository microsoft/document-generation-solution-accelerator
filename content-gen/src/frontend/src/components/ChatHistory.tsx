import { useState, useEffect, useCallback } from 'react';
import {
  Button,
  Text,
  Spinner,
  tokens,
  Link,
} from '@fluentui/react-components';
import {
  Chat24Regular,
  Delete24Regular,
  Add24Regular,
  ChevronRight20Regular,
} from '@fluentui/react-icons';

interface ConversationSummary {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
  messageCount: number;
}

interface ChatHistoryProps {
  currentConversationId: string;
  currentMessages?: { role: string; content: string }[]; // Current session messages
  onSelectConversation: (conversationId: string) => void;
  onNewConversation: () => void;
  refreshTrigger?: number; // Increment to trigger refresh
}

export function ChatHistory({ 
  currentConversationId, 
  currentMessages = [],
  onSelectConversation,
  onNewConversation,
  refreshTrigger = 0
}: ChatHistoryProps) {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAll, setShowAll] = useState(false);
  const INITIAL_COUNT = 5;

  const loadConversations = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Backend gets user from auth headers, no need to pass user_id
      const response = await fetch('/api/conversations');
      if (response.ok) {
        const data = await response.json();
        setConversations(data.conversations || []);
      } else {
        // If no conversations endpoint, use empty list
        setConversations([]);
      }
    } catch (err) {
      console.error('Error loading conversations:', err);
      setError('Unable to load conversation history');
      setConversations([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadConversations();
  }, [loadConversations, refreshTrigger]);

  // Reset showAll when conversations change significantly
  useEffect(() => {
    setShowAll(false);
  }, [refreshTrigger]);

  // Build the current session conversation summary if it has messages
  const currentSessionConversation: ConversationSummary | null = currentMessages.length > 0 ? {
    id: currentConversationId,
    title: currentMessages.find(m => m.role === 'user')?.content?.substring(0, 50) || 'Current Conversation',
    lastMessage: currentMessages[currentMessages.length - 1]?.content?.substring(0, 100) || '',
    timestamp: new Date().toISOString(),
    messageCount: currentMessages.length,
  } : null;

  // Merge current session with saved conversations, updating the current one with live data
  const displayConversations = (() => {
    // Find if current conversation exists in saved list
    const existingIndex = conversations.findIndex(c => c.id === currentConversationId);
    
    if (existingIndex >= 0 && currentSessionConversation) {
      // Update the saved conversation with current session data (live message count)
      const updated = [...conversations];
      updated[existingIndex] = {
        ...updated[existingIndex],
        messageCount: currentMessages.length,
        lastMessage: currentMessages[currentMessages.length - 1]?.content?.substring(0, 100) || updated[existingIndex].lastMessage,
      };
      return updated;
    } else if (currentSessionConversation) {
      // Add current session at the top if it has messages and isn't saved yet
      return [currentSessionConversation, ...conversations];
    }
    return conversations;
  })();

  const handleDeleteConversation = async (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      // Backend gets user from auth headers
      const response = await fetch(`/api/conversations/${conversationId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setConversations(prev => prev.filter(c => c.id !== conversationId));
        // If deleting current conversation, start a new one
        if (conversationId === currentConversationId) {
          onNewConversation();
        }
      }
    } catch (err) {
      console.error('Error deleting conversation:', err);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = diffMs / (1000 * 60 * 60);
    const diffDays = diffHours / 24;

    if (diffHours < 1) {
      return 'Just now';
    } else if (diffHours < 24) {
      return `${Math.floor(diffHours)}h ago`;
    } else if (diffDays < 7) {
      return `${Math.floor(diffDays)}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const visibleConversations = showAll ? displayConversations : displayConversations.slice(0, INITIAL_COUNT);
  const hasMore = displayConversations.length > INITIAL_COUNT;

  return (
    <div style={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      padding: '16px',
      backgroundColor: tokens.colorNeutralBackground2,
      borderRadius: '8px',
    }}>
      {/* Header */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        marginBottom: '16px',
      }}>
        <Text weight="semibold" size={400}>Chat History</Text>
      </div>

      {/* Conversation List */}
      <div style={{ 
        flex: 1, 
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
      }}>
        {isLoading ? (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center',
            padding: '32px' 
          }}>
            <Spinner size="small" label="Loading..." />
          </div>
        ) : error ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '32px',
            color: tokens.colorNeutralForeground3 
          }}>
            <Text size={200}>{error}</Text>
            <Link 
              onClick={loadConversations}
              style={{ display: 'block', marginTop: '8px' }}
            >
              Retry
            </Link>
          </div>
        ) : displayConversations.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '32px',
            color: tokens.colorNeutralForeground3 
          }}>
            <Chat24Regular style={{ fontSize: '24px', marginBottom: '8px', opacity: 0.5 }} />
            <Text size={200} block>No conversations yet</Text>
          </div>
        ) : (
          <>
            {visibleConversations.map((conversation) => (
              <ConversationItem
                key={conversation.id}
                conversation={conversation}
                isActive={conversation.id === currentConversationId}
                onSelect={() => onSelectConversation(conversation.id)}
                onDelete={(e) => handleDeleteConversation(conversation.id, e)}
                formatTimestamp={formatTimestamp}
              />
            ))}
          </>
        )}
      </div>

      {/* Footer Links */}
      <div style={{ 
        marginTop: '16px',
        paddingTop: '16px',
        borderTop: `1px solid ${tokens.colorNeutralStroke2}`,
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
      }}>
        {hasMore && (
          <Link
            onClick={() => setShowAll(!showAll)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '13px',
            }}
          >
            {showAll ? 'Show less' : 'See all'}
            <ChevronRight20Regular style={{ 
              transform: showAll ? 'rotate(90deg)' : 'none',
              transition: 'transform 0.2s',
            }} />
          </Link>
        )}
        
        <Link
          onClick={onNewConversation}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '13px',
          }}
        >
          <Add24Regular style={{ fontSize: '16px' }} />
          Start new chat
        </Link>
      </div>
    </div>
  );
}

interface ConversationItemProps {
  conversation: ConversationSummary;
  isActive: boolean;
  onSelect: () => void;
  onDelete: (e: React.MouseEvent) => void;
  formatTimestamp: (timestamp: string) => string;
}

function ConversationItem({ 
  conversation, 
  isActive, 
  onSelect, 
  onDelete,
  formatTimestamp,
}: ConversationItemProps) {
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <div
      onClick={onSelect}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        padding: '10px 12px',
        borderRadius: '6px',
        cursor: 'pointer',
        backgroundColor: isActive 
          ? tokens.colorBrandBackground2 
          : isHovered 
            ? tokens.colorNeutralBackground1Hover 
            : 'transparent',
        transition: 'background-color 0.15s',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '8px',
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <Text 
          size={200}
          weight={isActive ? 'semibold' : 'regular'}
          style={{ 
            overflow: 'hidden', 
            textOverflow: 'ellipsis', 
            whiteSpace: 'nowrap',
            display: 'block',
          }}
        >
          {conversation.title || 'Untitled'}
        </Text>
        <Text 
          size={100} 
          style={{ 
            color: tokens.colorNeutralForeground4,
          }}
        >
          {formatTimestamp(conversation.timestamp)}
        </Text>
      </div>
      
      {isHovered && (
        <Button
          appearance="subtle"
          icon={<Delete24Regular style={{ fontSize: '16px' }} />}
          size="small"
          onClick={onDelete}
          style={{ 
            minWidth: '28px', 
            height: '28px',
            padding: '4px',
          }}
        />
      )}
    </div>
  );
}
