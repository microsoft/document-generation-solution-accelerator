import { useState, useRef, useEffect } from 'react';
import {
  Card,
  Input,
  Button,
  Spinner,
  Text,
  Badge,
  tokens,
} from '@fluentui/react-components';
import {
  Send24Regular,
  Bot24Regular,
  Person24Regular,
} from '@fluentui/react-icons';
import ReactMarkdown from 'react-markdown';
import type { ChatMessage, CreativeBrief, Product, GeneratedContent } from '../types';
import { InlineBriefConfirmation } from './InlineBriefConfirmation';
import { InlineProductSelector } from './InlineProductSelector';
import { InlineContentPreview } from './InlineContentPreview';

interface ChatPanelProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  // Inline component props
  pendingBrief?: CreativeBrief | null;
  confirmedBrief?: CreativeBrief | null;
  generatedContent?: GeneratedContent | null;
  selectedProducts?: Product[];
  onBriefConfirm?: (brief: CreativeBrief) => void;
  onBriefCancel?: () => void;
  onBriefEdit?: (brief: CreativeBrief) => void;
  onProductsChange?: (products: Product[]) => void;
  onGenerateContent?: () => void;
  onRegenerateContent?: () => void;
}

export function ChatPanel({ 
  messages, 
  onSendMessage, 
  isLoading,
  pendingBrief,
  confirmedBrief,
  generatedContent,
  selectedProducts = [],
  onBriefConfirm,
  onBriefCancel,
  onBriefEdit,
  onProductsChange,
  onGenerateContent,
  onRegenerateContent,
}: ChatPanelProps) {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, pendingBrief, confirmedBrief, generatedContent]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  // Determine if we should show inline components
  const showBriefConfirmation = pendingBrief && onBriefConfirm && onBriefCancel && onBriefEdit;
  const showProductSelector = confirmedBrief && !generatedContent && onProductsChange && onGenerateContent;
  const showContentPreview = generatedContent && onRegenerateContent;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Messages Area */}
      <div style={{ 
        flex: 1, 
        overflowY: 'auto', 
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        {messages.length === 0 && !showBriefConfirmation && !showProductSelector && !showContentPreview && (
          <div style={{ 
            textAlign: 'center', 
            padding: '48px',
            color: tokens.colorNeutralForeground3 
          }}>
            <Bot24Regular style={{ fontSize: '48px', marginBottom: '16px' }} />
            <Text size={400} block style={{ marginBottom: '8px' }}>
              Welcome to Content Generation Accelerator
            </Text>
            <Text size={300}>
              Start by describing your marketing campaign or pasting a creative brief.
            </Text>
          </div>
        )}
        
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {/* Inline Brief Confirmation */}
        {showBriefConfirmation && (
          <InlineBriefConfirmation
            brief={pendingBrief}
            onConfirm={onBriefConfirm}
            onCancel={onBriefCancel}
            onEdit={onBriefEdit}
          />
        )}
        
        {/* Inline Product Selector */}
        {showProductSelector && (
          <InlineProductSelector
            selectedProducts={selectedProducts}
            onProductsChange={onProductsChange}
            onGenerate={onGenerateContent}
            isLoading={isLoading}
          />
        )}
        
        {/* Inline Content Preview */}
        {showContentPreview && (
          <InlineContentPreview
            content={generatedContent}
            onRegenerate={onRegenerateContent}
            isLoading={isLoading}
          />
        )}
        
        {isLoading && !showProductSelector && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Spinner size="tiny" />
            <Text size={200}>Generating response...</Text>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Area */}
      <form 
        onSubmit={handleSubmit}
        style={{ 
          padding: '16px',
          borderTop: `1px solid ${tokens.colorNeutralStroke1}`,
          display: 'flex',
          gap: '8px'
        }}
      >
        <Input
          style={{ flex: 1 }}
          placeholder="Describe your marketing campaign or paste a creative brief..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={isLoading}
        />
        <Button
          appearance="primary"
          icon={<Send24Regular />}
          type="submit"
          disabled={!inputValue.trim() || isLoading}
        >
          Send
        </Button>
      </form>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';
  
  return (
    <div style={{ 
      display: 'flex',
      flexDirection: isUser ? 'row-reverse' : 'row',
      gap: '8px',
      alignItems: 'flex-start'
    }}>
      <div style={{ 
        width: '32px',
        height: '32px',
        borderRadius: '50%',
        backgroundColor: isUser ? tokens.colorBrandBackground : tokens.colorNeutralBackground3,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0
      }}>
        {isUser ? (
          <Person24Regular style={{ fontSize: '16px', color: 'white' }} />
        ) : (
          <Bot24Regular style={{ fontSize: '16px' }} />
        )}
      </div>
      
      <Card style={{ 
        maxWidth: '70%',
        backgroundColor: isUser ? tokens.colorBrandBackground2 : tokens.colorNeutralBackground1
      }}>
        {message.agent && (
          <Badge appearance="outline" size="small" style={{ marginBottom: '8px' }}>
            {message.agent}
          </Badge>
        )}
        <div style={{ fontSize: '14px' }}>
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
        <Text 
          size={100} 
          style={{ 
            color: tokens.colorNeutralForeground3,
            marginTop: '8px'
          }}
        >
          {new Date(message.timestamp).toLocaleTimeString()}
        </Text>
      </Card>
    </div>
  );
}
