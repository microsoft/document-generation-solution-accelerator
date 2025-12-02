import { useState, useEffect, useCallback } from 'react';
import {
  Card,
  CardHeader,
  Button,
  Text,
  Title3,
  Spinner,
  tokens,
  Menu,
  MenuTrigger,
  MenuList,
  MenuItem,
  MenuPopover,
} from '@fluentui/react-components';
import {
  History24Regular,
  Chat24Regular,
  Delete24Regular,
  MoreHorizontal24Regular,
  Add24Regular,
  ArrowSync24Regular,
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
  userId: string;
  currentMessages?: { role: string; content: string }[]; // Current session messages
  onSelectConversation: (conversationId: string) => void;
  onNewConversation: () => void;
  refreshTrigger?: number; // Increment to trigger refresh
}

export function ChatHistory({ 
  currentConversationId, 
  userId,
  currentMessages = [],
  onSelectConversation,
  onNewConversation,
  refreshTrigger = 0
}: ChatHistoryProps) {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadConversations = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/conversations?user_id=${encodeURIComponent(userId)}`);
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
  }, [userId]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations, refreshTrigger]);

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
      const response = await fetch(`/api/conversations/${conversationId}?user_id=${encodeURIComponent(userId)}`, {
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

  const truncateText = (text: string, maxLength: number = 50) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <Card className="panel-card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardHeader
        header={
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <History24Regular />
            <Title3>Chat History</Title3>
          </div>
        }
        action={
          <div style={{ display: 'flex', gap: '4px' }}>
            <Button
              appearance="subtle"
              icon={<ArrowSync24Regular />}
              size="small"
              onClick={loadConversations}
              title="Refresh"
            />
            <Button
              appearance="primary"
              icon={<Add24Regular />}
              size="small"
              onClick={onNewConversation}
            >
              New Chat
            </Button>
          </div>
        }
      />

      <div style={{ 
        flex: 1, 
        overflowY: 'auto',
        padding: '0 16px 16px 16px'
      }}>
        {isLoading ? (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center',
            padding: '32px' 
          }}>
            <Spinner size="small" label="Loading conversations..." />
          </div>
        ) : error ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '32px',
            color: tokens.colorNeutralForeground3 
          }}>
            <Text size={200}>{error}</Text>
            <Button 
              appearance="subtle" 
              size="small" 
              onClick={loadConversations}
              style={{ marginTop: '8px' }}
            >
              Retry
            </Button>
          </div>
        ) : displayConversations.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '32px',
            color: tokens.colorNeutralForeground3 
          }}>
            <Chat24Regular style={{ fontSize: '32px', marginBottom: '8px', opacity: 0.5 }} />
            <Text size={200} block>No previous conversations</Text>
            <Text size={100} style={{ color: tokens.colorNeutralForeground4 }}>
              Start a new chat to begin
            </Text>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {displayConversations.map((conversation) => (
              <ConversationItem
                key={conversation.id}
                conversation={conversation}
                isActive={conversation.id === currentConversationId}
                onSelect={() => onSelectConversation(conversation.id)}
                onDelete={(e) => handleDeleteConversation(conversation.id, e)}
                formatTimestamp={formatTimestamp}
                truncateText={truncateText}
              />
            ))}
          </div>
        )}
      </div>
    </Card>
  );
}

interface ConversationItemProps {
  conversation: ConversationSummary;
  isActive: boolean;
  onSelect: () => void;
  onDelete: (e: React.MouseEvent) => void;
  formatTimestamp: (timestamp: string) => string;
  truncateText: (text: string, maxLength?: number) => string;
}

function ConversationItem({ 
  conversation, 
  isActive, 
  onSelect, 
  onDelete,
  formatTimestamp,
  truncateText
}: ConversationItemProps) {
  return (
    <div
      onClick={onSelect}
      style={{
        padding: '12px',
        borderRadius: '8px',
        cursor: 'pointer',
        backgroundColor: isActive 
          ? tokens.colorBrandBackground2 
          : tokens.colorNeutralBackground1,
        border: `1px solid ${isActive ? tokens.colorBrandStroke1 : tokens.colorNeutralStroke1}`,
        transition: 'background-color 0.15s, border-color 0.15s',
      }}
      onMouseEnter={(e) => {
        if (!isActive) {
          e.currentTarget.style.backgroundColor = tokens.colorNeutralBackground1Hover;
        }
      }}
      onMouseLeave={(e) => {
        if (!isActive) {
          e.currentTarget.style.backgroundColor = tokens.colorNeutralBackground1;
        }
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <Text 
            weight="semibold" 
            size={200} 
            block
            style={{ 
              overflow: 'hidden', 
              textOverflow: 'ellipsis', 
              whiteSpace: 'nowrap' 
            }}
          >
            {conversation.title || 'Untitled Conversation'}
          </Text>
          <Text 
            size={100} 
            style={{ 
              color: tokens.colorNeutralForeground3,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              display: 'block'
            }}
          >
            {truncateText(conversation.lastMessage)}
          </Text>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginLeft: '8px' }}>
          <Text size={100} style={{ color: tokens.colorNeutralForeground4 }}>
            {formatTimestamp(conversation.timestamp)}
          </Text>
          
          <Menu>
            <MenuTrigger disableButtonEnhancement>
              <Button
                appearance="subtle"
                icon={<MoreHorizontal24Regular />}
                size="small"
                onClick={(e) => e.stopPropagation()}
              />
            </MenuTrigger>
            <MenuPopover>
              <MenuList>
                <MenuItem 
                  icon={<Delete24Regular />}
                  onClick={onDelete}
                >
                  Delete
                </MenuItem>
              </MenuList>
            </MenuPopover>
          </Menu>
        </div>
      </div>
      
      <div style={{ marginTop: '4px' }}>
        <Text size={100} style={{ color: tokens.colorNeutralForeground4 }}>
          {conversation.messageCount} messages
        </Text>
      </div>
    </div>
  );
}
