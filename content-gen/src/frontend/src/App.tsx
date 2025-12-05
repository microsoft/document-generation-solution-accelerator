import { useState, useCallback, useEffect } from 'react';
import {
  Title1,
  Subtitle1,
  Divider,
  tokens,
} from '@fluentui/react-components';
import {
  Sparkle24Regular,
} from '@fluentui/react-icons';
import { v4 as uuidv4 } from 'uuid';

import { ChatPanel } from './components/ChatPanel';
import { ChatHistory } from './components/ChatHistory';
import type { ChatMessage, CreativeBrief, Product, GeneratedContent } from './types';

interface UserInfo {
  user_principal_id: string;
  user_name: string;
  auth_provider: string;
  is_authenticated: boolean;
}

function App() {
  const [conversationId, setConversationId] = useState<string>(() => uuidv4());
  const [userId, setUserId] = useState<string>('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Brief confirmation flow
  const [pendingBrief, setPendingBrief] = useState<CreativeBrief | null>(null);
  const [confirmedBrief, setConfirmedBrief] = useState<CreativeBrief | null>(null);
  
  // Product selection
  const [selectedProducts, setSelectedProducts] = useState<Product[]>([]);
  
  // Generated content
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent | null>(null);

  // Trigger for refreshing chat history
  const [historyRefreshTrigger, setHistoryRefreshTrigger] = useState(0);

  // Fetch current user on mount
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await fetch('/api/user');
        if (response.ok) {
          const user: UserInfo = await response.json();
          // Use user_principal_id if authenticated, otherwise empty string for dev mode
          setUserId(user.user_principal_id || '');
        }
      } catch (err) {
        console.error('Error fetching user:', err);
        // Default to empty string for development mode
        setUserId('');
      }
    };
    fetchUser();
  }, []);

  // Handle selecting a conversation from history
  const handleSelectConversation = useCallback(async (selectedConversationId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/conversations/${selectedConversationId}?user_id=${encodeURIComponent(userId)}`);
      if (response.ok) {
        const data = await response.json();
        setConversationId(selectedConversationId);
        // Map messages to ChatMessage format
        const loadedMessages: ChatMessage[] = (data.messages || []).map((msg: { role: string; content: string; timestamp?: string; agent?: string }, index: number) => ({
          id: `${selectedConversationId}-${index}`,
          role: msg.role as 'user' | 'assistant',
          content: msg.content,
          timestamp: msg.timestamp || new Date().toISOString(),
          agent: msg.agent,
        }));
        setMessages(loadedMessages);
        setPendingBrief(null);
        setConfirmedBrief(data.brief || null);
        
        // Restore generated content if it exists
        if (data.generated_content) {
          const gc = data.generated_content;
          // Parse text_content if it's a string
          let textContent = gc.text_content;
          if (typeof textContent === 'string') {
            try {
              textContent = JSON.parse(textContent);
            } catch {
              // Keep as string if not valid JSON
            }
          }
          
          // Build image URL: convert old blob URLs to proxy URLs, or use existing proxy URL
          let imageUrl: string | undefined = gc.image_url;
          if (imageUrl && imageUrl.includes('blob.core.windows.net')) {
            // Convert old blob URL to proxy URL
            // blob URL format: https://account.blob.core.windows.net/container/conv_id/filename.png
            const parts = imageUrl.split('/');
            const filename = parts[parts.length - 1];
            const convId = parts[parts.length - 2];
            imageUrl = `/api/images/${convId}/${filename}`;
          }
          if (!imageUrl && gc.image_base64) {
            imageUrl = `data:image/png;base64,${gc.image_base64}`;
          }
          
          const restoredContent: GeneratedContent = {
            text_content: typeof textContent === 'object' && textContent ? {
              headline: textContent?.headline,
              body: textContent?.body,
              cta_text: textContent?.cta,
              tagline: textContent?.tagline,
            } : undefined,
            image_content: (imageUrl || gc.image_prompt) ? {
              image_url: imageUrl,
              prompt_used: gc.image_prompt,
              alt_text: gc.image_revised_prompt || 'Generated marketing image',
            } : undefined,
            violations: gc.violations || [],
            requires_modification: gc.requires_modification || false,
          };
          setGeneratedContent(restoredContent);
        } else {
          setGeneratedContent(null);
        }
        
        setSelectedProducts([]);
      }
    } catch (error) {
      console.error('Error loading conversation:', error);
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // Handle starting a new conversation
  const handleNewConversation = useCallback(() => {
    setConversationId(uuidv4());
    setMessages([]);
    setPendingBrief(null);
    setConfirmedBrief(null);
    setGeneratedContent(null);
    setSelectedProducts([]);
  }, []);

  const handleSendMessage = useCallback(async (content: string) => {
    const userMessage: ChatMessage = {
      id: uuidv4(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    try {
      // Import dynamically to avoid SSR issues
      const { streamChat, parseBrief } = await import('./api');
      
      // Check if this looks like a creative brief
      const briefKeywords = ['campaign', 'marketing', 'target audience', 'objective', 'deliverable'];
      const isBriefLike = briefKeywords.some(kw => content.toLowerCase().includes(kw));
      
      if (isBriefLike && !confirmedBrief) {
        // Parse as a creative brief
        const parsed = await parseBrief(content, conversationId, userId);
        setPendingBrief(parsed.brief);
        
        const assistantMessage: ChatMessage = {
          id: uuidv4(),
          role: 'assistant',
          content: 'I\'ve parsed your creative brief. Please review and confirm the details before we proceed.',
          agent: 'PlanningAgent',
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        // Stream chat response
        let fullContent = '';
        let currentAgent = '';
        let messageAdded = false;
        
        for await (const response of streamChat(content, conversationId, userId)) {
          if (response.type === 'agent_response') {
            fullContent = response.content;
            currentAgent = response.agent || '';
            
            // Add message when final OR when requiring user input (interactive response)
            if ((response.is_final || response.requires_user_input) && !messageAdded) {
              const assistantMessage: ChatMessage = {
                id: uuidv4(),
                role: 'assistant',
                content: fullContent,
                agent: currentAgent,
                timestamp: new Date().toISOString(),
              };
              setMessages(prev => [...prev, assistantMessage]);
              messageAdded = true;
            }
          } else if (response.type === 'error') {
            // Handle error responses
            const errorMessage: ChatMessage = {
              id: uuidv4(),
              role: 'assistant',
              content: response.content || 'An error occurred while processing your request.',
              timestamp: new Date().toISOString(),
            };
            setMessages(prev => [...prev, errorMessage]);
            messageAdded = true;
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      // Trigger refresh of chat history after message is sent
      setHistoryRefreshTrigger(prev => prev + 1);
    }
  }, [conversationId, userId, confirmedBrief]);

  const handleBriefConfirm = useCallback(async (brief: CreativeBrief) => {
    try {
      const { confirmBrief } = await import('./api');
      await confirmBrief(brief, conversationId, userId);
      setConfirmedBrief(brief);
      setPendingBrief(null);
      
      const assistantMessage: ChatMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: 'Great! Your creative brief has been confirmed. Now you can select products to feature and generate content.',
        agent: 'TriageAgent',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error confirming brief:', error);
    }
  }, [conversationId, userId]);

  const handleBriefCancel = useCallback(() => {
    setPendingBrief(null);
    const assistantMessage: ChatMessage = {
      id: uuidv4(),
      role: 'assistant',
      content: 'No problem. Please provide your creative brief again or ask me any questions.',
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, assistantMessage]);
  }, []);

  const handleGenerateContent = useCallback(async () => {
    if (!confirmedBrief) return;
    
    setIsLoading(true);
    try {
      const { streamGenerateContent } = await import('./api');
      
      for await (const response of streamGenerateContent(
        confirmedBrief,
        selectedProducts,
        true,
        conversationId,
        userId
      )) {
        if (response.is_final && response.type !== 'error') {
          try {
            const rawContent = JSON.parse(response.content);
            
            // Parse text_content if it's a string (from orchestrator)
            let textContent = rawContent.text_content;
            if (typeof textContent === 'string') {
              try {
                textContent = JSON.parse(textContent);
              } catch {
                // Keep as string if not valid JSON
              }
            }
            
            // Build image_url: prefer blob URL, fallback to base64 data URL
            let imageUrl: string | undefined;
            if (rawContent.image_url) {
              imageUrl = rawContent.image_url;
            } else if (rawContent.image_base64) {
              imageUrl = `data:image/png;base64,${rawContent.image_base64}`;
            }
            
            const content: GeneratedContent = {
              text_content: typeof textContent === 'object' ? {
                headline: textContent?.headline,
                body: textContent?.body,
                cta_text: textContent?.cta,
                tagline: textContent?.tagline,
              } : undefined,
              image_content: (imageUrl || rawContent.image_prompt) ? {
                image_url: imageUrl,
                prompt_used: rawContent.image_prompt,
                alt_text: rawContent.image_revised_prompt || 'Generated marketing image',
              } : undefined,
              violations: rawContent.violations || [],
              requires_modification: rawContent.requires_modification || false,
            };
            setGeneratedContent(content);
            
            // Add a message to chat showing content was generated
            const assistantMessage: ChatMessage = {
              id: uuidv4(),
              role: 'assistant',
              content: `Content generated successfully! ${textContent?.headline ? `Headline: "${textContent.headline}"` : ''}`,
              agent: 'ContentAgent',
              timestamp: new Date().toISOString(),
            };
            setMessages(prev => [...prev, assistantMessage]);
          } catch (parseError) {
            console.error('Error parsing generated content:', parseError);
          }
        } else if (response.type === 'error') {
          const errorMessage: ChatMessage = {
            id: uuidv4(),
            role: 'assistant',
            content: `Error generating content: ${response.content}`,
            timestamp: new Date().toISOString(),
          };
          setMessages(prev => [...prev, errorMessage]);
        }
      }
    } catch (error) {
      console.error('Error generating content:', error);
      const errorMessage: ChatMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: 'Sorry, there was an error generating content. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [confirmedBrief, selectedProducts, conversationId]);

  return (
    <div className="app-container">
      {/* Header */}
      <header style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '12px',
        padding: '16px 0',
        marginBottom: '8px'
      }}>
        <Sparkle24Regular style={{ color: tokens.colorBrandForeground1 }} />
        <div>
          <Title1>Content Generation Accelerator</Title1>
          <Subtitle1 style={{ color: tokens.colorNeutralForeground3 }}>
            AI-powered marketing content creation
          </Subtitle1>
        </div>
      </header>
      
      <Divider />
      
      {/* Main Content */}
      <div className="main-content" style={{ marginTop: '16px' }}>
        {/* Chat History Sidebar */}
        <div className="history-panel">
          <ChatHistory
            currentConversationId={conversationId}
            currentMessages={messages}
            onSelectConversation={handleSelectConversation}
            onNewConversation={handleNewConversation}
            refreshTrigger={historyRefreshTrigger}
          />
        </div>
        
        {/* Chat Panel - now includes inline product selector and content preview */}
        <div className="chat-panel" style={{ flex: 1 }}>
          <ChatPanel
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            pendingBrief={pendingBrief}
            confirmedBrief={confirmedBrief}
            generatedContent={generatedContent}
            selectedProducts={selectedProducts}
            onBriefConfirm={handleBriefConfirm}
            onBriefCancel={handleBriefCancel}
            onBriefEdit={setPendingBrief}
            onProductsChange={setSelectedProducts}
            onGenerateContent={handleGenerateContent}
            onRegenerateContent={handleGenerateContent}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
