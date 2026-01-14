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
  Compose20Regular,
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
  const hasMore = displayConversations.length > INITIAL_COUNT;

  return (
    <div style={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      padding: '16px',
      backgroundColor: tokens.colorNeutralBackground3,
      overflow: 'hidden',
    }}>
      <Text 
        weight="semibold" 
        size={300}
        style={{ 
          marginBottom: '12px',
          color: tokens.colorNeutralForeground1,
          flexShrink: 0,
        }}
      >
        Chat History
      </Text>

      <div style={{ 
        borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
        marginBottom: '12px',
        flexShrink: 0,
      }} />

      <div style={{ 
        flex: 1, 
        display: 'flex',
        flexDirection: 'column',
        minHeight: 0,
        overflowY: showAll ? 'auto' : 'hidden',
        paddingLeft: '8px',
        paddingRight: '8px',
        marginLeft: '-8px',
        marginRight: '-8px',
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
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
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
                isActive={conversation.id === currentConversationId}
                onSelect={() => onSelectConversation(conversation.id)}
                showMenu={index === 0}
              />
            ))}
          </>
        )}

        <div style={{ 
          marginTop: '8px',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          flexShrink: 0,
          ...(showAll && {
            position: 'sticky',
            bottom: 0,
            backgroundColor: tokens.colorNeutralBackground3,
            paddingTop: '8px',
            paddingBottom: '4px',
          }),
        }}>
          {hasMore && (
            <Link
              onClick={() => setShowAll(!showAll)}
              style={{
                fontSize: '13px',
                color: tokens.colorBrandForeground1,
              }}
            >
              {showAll ? 'Show less' : 'See all'}
            </Link>
          )}
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
            <Compose20Regular />
            Start new chat
          </Link>
        </div>
      </div>
    </div>
  );
}

interface ConversationItemProps {
  conversation: ConversationSummary;
  isActive: boolean;
  onSelect: () => void;
  showMenu?: boolean;
}

function ConversationItem({ 
  conversation, 
  isActive,
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
        padding: '8px',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '8px',
        backgroundColor: isActive 
          ? tokens.colorNeutralBackground1 
          : 'transparent',
        border: isActive 
          ? `1px solid ${tokens.colorNeutralStroke2}` 
          : '1px solid transparent',
        borderRadius: '6px',
        marginLeft: '-8px',
        marginRight: '-8px',
        transition: 'background-color 0.15s, border-color 0.15s',
      }}
    >
      <Text 
        size={200}
        weight={isActive ? 'semibold' : 'regular'}
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
      
      {(showMenu || isHovered) && (
        <Button
          appearance="subtle"
          icon={<MoreHorizontal20Regular />}
          size="small"
          onClick={(e) => {
            e.stopPropagation();
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
