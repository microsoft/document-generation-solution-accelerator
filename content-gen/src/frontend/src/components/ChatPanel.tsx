import { useState, useRef, useEffect } from 'react';
import {
  Card,
  Input,
  Button,
  Spinner,
  Text,
  Badge,
  tokens,
  Tooltip,
} from '@fluentui/react-components';
import {
  Send24Regular,
  Bot24Regular,
  Person24Regular,
  Add24Regular,
} from '@fluentui/react-icons';
import ReactMarkdown from 'react-markdown';
import type { ChatMessage, CreativeBrief, Product, GeneratedContent } from '../types';
import { BriefReview } from './BriefReview';
import { ProductReview } from './ProductReview';
import { InlineContentPreview } from './InlineContentPreview';
import { WelcomeCard } from './WelcomeCard';

interface ChatPanelProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  generationStatus?: string;
  // Inline component props
  pendingBrief?: CreativeBrief | null;
  confirmedBrief?: CreativeBrief | null;
  generatedContent?: GeneratedContent | null;
  selectedProducts?: Product[];
  onBriefConfirm?: () => void;
  onBriefCancel?: () => void;
  onGenerateContent?: () => void;
  onRegenerateContent?: () => void;
  onProductsStartOver?: () => void;
}

export function ChatPanel({ 
  messages, 
  onSendMessage, 
  isLoading,
  generationStatus,
  pendingBrief,
  confirmedBrief,
  generatedContent,
  selectedProducts = [],
  onBriefConfirm,
  onBriefCancel,
  onGenerateContent,
  onRegenerateContent,
  onProductsStartOver,
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
  const showBriefReview = pendingBrief && onBriefConfirm && onBriefCancel;
  const showProductReview = confirmedBrief && !generatedContent && onGenerateContent;
  const showContentPreview = generatedContent && onRegenerateContent;
  const showWelcome = messages.length === 0 && !showBriefReview && !showProductReview && !showContentPreview;

  // Handle suggestion click from welcome card
  const handleSuggestionClick = (prompt: string) => {
    setInputValue(prompt);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Messages Area */}
      <div style={{ 
        flex: 1, 
        overflowY: 'auto', 
        padding: 'clamp(12px, 2vw, 16px)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'clamp(12px, 2vw, 16px)',
        minHeight: 0, /* Allow flex shrinking */
      }}>
        {showWelcome ? (
          <WelcomeCard onSuggestionClick={handleSuggestionClick} />
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            
            {/* Brief Review - Read Only with Conversational Prompts */}
            {showBriefReview && (
              <BriefReview
                brief={pendingBrief}
                onConfirm={onBriefConfirm}
                onStartOver={onBriefCancel}
                isAwaitingResponse={isLoading}
              />
            )}
            
            {/* Product Review - Conversational Product Selection */}
            {showProductReview && (
              <ProductReview
                products={selectedProducts}
                onConfirm={onGenerateContent}
                onStartOver={onProductsStartOver || (() => {})}
                isAwaitingResponse={isLoading}
              />
            )}
            
            {/* Inline Content Preview */}
            {showContentPreview && (
              <InlineContentPreview
                content={generatedContent}
                onRegenerate={onRegenerateContent}
                isLoading={isLoading}
                selectedProduct={selectedProducts.length > 0 ? selectedProducts[0] : undefined}
              />
            )}
            
            {isLoading && (
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '12px',
                padding: '16px 20px',
                backgroundColor: tokens.colorNeutralBackground3,
                borderRadius: '12px',
                border: `1px solid ${tokens.colorNeutralStroke2}`,
              }}>
                <Spinner size="small" />
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <Text weight="semibold" size={300}>
                    {generationStatus || 'Generating response...'}
                  </Text>
                  {generationStatus && (
                    <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
                      This may take up to a minute
                    </Text>
                  )}
                </div>
              </div>
            )}
          </>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Area */}
      <div style={{
        padding: 'clamp(12px, 2vw, 16px) clamp(16px, 3vw, 24px) clamp(8px, 1.5vw, 12px)',
        borderTop: `1px solid ${tokens.colorNeutralStroke2}`,
        backgroundColor: tokens.colorNeutralBackground1,
        flexShrink: 0,
      }}>
        <form 
          onSubmit={handleSubmit}
          style={{ 
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: tokens.colorNeutralBackground3,
            borderRadius: '24px',
            padding: 'clamp(6px, 1vw, 8px) clamp(8px, 1.5vw, 12px)',
            border: `1px solid ${tokens.colorNeutralStroke1}`,
          }}
        >
          <Tooltip content="Attach file" relationship="label">
            <Button
              appearance="subtle"
              icon={<Add24Regular />}
              shape="circular"
              size="small"
              disabled={isLoading}
              style={{ 
                minWidth: '32px',
                color: tokens.colorNeutralForeground3,
              }}
            />
          </Tooltip>
          <Input
            style={{ 
              flex: 1,
              border: 'none',
              backgroundColor: 'transparent',
              minWidth: 0, /* Allow input to shrink */
            }}
            appearance="underline"
            placeholder="Type a message"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isLoading}
          />
          <Button
            appearance="subtle"
            icon={<Send24Regular />}
            shape="circular"
            size="small"
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            style={{ 
              minWidth: '32px',
              color: inputValue.trim() ? tokens.colorBrandForeground1 : tokens.colorNeutralForeground4,
            }}
          />
        </form>
        
        {/* Disclaimer */}
        <Text 
          size={100} 
          style={{ 
            display: 'block',
            textAlign: 'center',
            marginTop: '8px',
            color: tokens.colorNeutralForeground4,
            fontSize: 'clamp(10px, 1.2vw, 12px)',
          }}
        >
          AI generated content may be incorrect. Check for mistakes.
        </Text>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';
  
  return (
    <div style={{ 
      display: 'flex',
      flexDirection: isUser ? 'row-reverse' : 'row',
      gap: 'clamp(6px, 1vw, 8px)',
      alignItems: 'flex-start'
    }}>
      <div style={{ 
        width: 'clamp(28px, 4vw, 32px)',
        height: 'clamp(28px, 4vw, 32px)',
        minWidth: '28px',
        minHeight: '28px',
        borderRadius: '50%',
        backgroundColor: isUser ? tokens.colorBrandBackground : tokens.colorNeutralBackground3,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0
      }}>
        {isUser ? (
          <Person24Regular style={{ fontSize: 'clamp(14px, 2vw, 16px)', color: 'white' }} />
        ) : (
          <Bot24Regular style={{ fontSize: 'clamp(14px, 2vw, 16px)' }} />
        )}
      </div>
      
      <Card style={{ 
        maxWidth: 'min(70%, calc(100% - 50px))',
        backgroundColor: isUser ? tokens.colorBrandBackground2 : tokens.colorNeutralBackground1,
        minWidth: 0, /* Allow card to shrink */
      }}>
        {message.agent && (
          <Badge appearance="outline" size="small" style={{ marginBottom: '8px' }}>
            {message.agent}
          </Badge>
        )}
        <div style={{ fontSize: 'clamp(13px, 1.8vw, 14px)', wordBreak: 'break-word' }}>
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
        <Text 
          size={100} 
          style={{ 
            color: tokens.colorNeutralForeground3,
            marginTop: '8px',
            fontSize: 'clamp(10px, 1.2vw, 12px)',
          }}
        >
          {new Date(message.timestamp).toLocaleTimeString()}
        </Text>
      </Card>
    </div>
  );
}
