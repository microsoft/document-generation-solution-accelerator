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
  MoreHorizontal20Regular,
  EditRegular,
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

  const visibleConversations = showAll ? displayConversations : displayConversations.slice(0, INITIAL_COUNT);

  return (
    <div style={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      padding: '16px',
      backgroundColor: tokens.colorNeutralBackground1,
      overflow: 'hidden',
    }}>
      {/* Header */}
        <Text 
          weight="semibold" 
        size={300}
        style={{ 
          marginBottom: '16px',
          color: tokens.colorNeutralForeground1,
        }}
        >
          Chat History
        </Text>

      {/* Conversation List */}
      <div style={{ 
        flex: 1, 
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '0',
        minHeight: 0,
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
            {visibleConversations.map((conversation, index) => (
              <ConversationItem
                key={conversation.id}
                conversation={conversation}
                onSelect={() => onSelectConversation(conversation.id)}
                showMenu={index === 0} // Only show menu on first item per Figma
              />
            ))}
          </>
        )}
      </div>

      {/* Footer Links */}
      <div style={{ 
        marginTop: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        flexShrink: 0,
      }}>
          <Link
            onClick={() => setShowAll(!showAll)}
            style={{
            fontSize: '13px',
            color: tokens.colorBrandForeground1,
            }}
          >
          See all
          </Link>
        
        <Link
          onClick={onNewConversation}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '13px',
            color: tokens.colorNeutralForeground1,
          }}
        >
          <EditRegular style={{ fontSize: '16px' }} />
          Start new chat
        </Link>
      </div>
    </div>
  );
}

interface ConversationItemProps {
  conversation: ConversationSummary;
  onSelect: () => void;
  showMenu?: boolean;
}

function ConversationItem({ 
  conversation, 
  onSelect, 
  showMenu = false,
}: ConversationItemProps) {
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <div
      onClick={onSelect}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        padding: '8px 0',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '8px',
        borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
      }}
    >
        <Text 
          size={200}
          style={{ 
            overflow: 'hidden', 
            textOverflow: 'ellipsis', 
            whiteSpace: 'nowrap',
          flex: 1,
          fontSize: '13px',
          color: tokens.colorNeutralForeground1,
          }}
        >
          {conversation.title || 'Untitled'}
        </Text>
      
      {/* Three-dot ellipsis menu - only show on first item or hover */}
      {(showMenu || isHovered) && (
        <Button
          appearance="subtle"
          icon={<MoreHorizontal20Regular />}
          size="small"
          onClick={(e) => {
            e.stopPropagation();
            // Future: open menu with options
          }}
          style={{ 
            minWidth: '24px', 
            height: '24px',
            padding: '2px',
            color: tokens.colorNeutralForeground3,
          }}
        />
      )}
    </div>
  );
}
