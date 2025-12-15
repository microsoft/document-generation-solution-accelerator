import { useState, useCallback, useEffect, useRef } from 'react';
import {
  Text,
  Avatar,
  tokens,
} from '@fluentui/react-components';
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

// Contoso logo SVG component
function ContosoLogo() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M14 0L28 14L14 28L0 14L14 0Z" fill="#0078D4"/>
      <path d="M14 4L24 14L14 24L4 14L14 4Z" fill="#50E6FF"/>
      <path d="M14 8L20 14L14 20L8 14L14 8Z" fill="white"/>
    </svg>
  );
}

function App() {
  const [conversationId, setConversationId] = useState<string>(() => uuidv4());
  const [userId, setUserId] = useState<string>('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [generationStatus, setGenerationStatus] = useState<string>('');
  
  // Feature flags from config
  const [imageGenerationEnabled, setImageGenerationEnabled] = useState<boolean>(true);
  
  // Brief confirmation flow
  const [pendingBrief, setPendingBrief] = useState<CreativeBrief | null>(null);
  const [confirmedBrief, setConfirmedBrief] = useState<CreativeBrief | null>(null);
  
  // Product selection
  const [selectedProducts, setSelectedProducts] = useState<Product[]>([]);
  
  // Generated content
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent | null>(null);

  // Trigger for refreshing chat history
  const [historyRefreshTrigger, setHistoryRefreshTrigger] = useState(0);

  // Abort controller for cancelling ongoing requests
  const abortControllerRef = useRef<AbortController | null>(null);

  // Fetch app config on mount
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const { getAppConfig } = await import('./api');
        const config = await getAppConfig();
        setImageGenerationEnabled(config.enable_image_generation);
      } catch (err) {
        console.error('Error fetching config:', err);
        // Default to enabled if config fetch fails
        setImageGenerationEnabled(true);
      }
    };
    fetchConfig();
  }, []);

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
            // Restore any generation errors
            error: gc.error,
            image_error: gc.image_error,
            text_error: gc.text_error,
          };
          setGeneratedContent(restoredContent);
          
          // Restore selected products if they exist
          if (gc.selected_products && Array.isArray(gc.selected_products)) {
            setSelectedProducts(gc.selected_products);
          } else {
            setSelectedProducts([]);
          }
        } else {
          setGeneratedContent(null);
          setSelectedProducts([]);
        }
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
    
    // Create new abort controller for this request
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;
    
    try {
      // Import dynamically to avoid SSR issues
      const { streamChat, parseBrief, selectProducts } = await import('./api');
      
      // If we have a pending brief and user is providing feedback, update the brief
      if (pendingBrief && !confirmedBrief) {
        // User is refining the brief conversationally
        const refinementKeywords = ['change', 'update', 'modify', 'add', 'remove', 'delete', 'set', 'make', 'should be'];
        const isRefinement = refinementKeywords.some(kw => content.toLowerCase().includes(kw));
        
        if (isRefinement) {
          // Send the refinement request to update the brief
          // Combine original brief context with the refinement request
          const refinementPrompt = `Current creative brief:\n${JSON.stringify(pendingBrief, null, 2)}\n\nUser requested change: ${content}\n\nPlease update the brief accordingly and return the complete updated brief.`;
          
          setGenerationStatus('Updating creative brief...');
          const parsed = await parseBrief(refinementPrompt, conversationId, userId, signal);
          setPendingBrief(parsed.brief);
          setGenerationStatus('');
          
          const assistantMessage: ChatMessage = {
            id: uuidv4(),
            role: 'assistant',
            content: "I've updated the brief based on your feedback. Please review the changes above. Let me know if you'd like any other modifications, or click **Confirm Brief** when you're satisfied.",
            agent: 'PlanningAgent',
            timestamp: new Date().toISOString(),
          };
          setMessages(prev => [...prev, assistantMessage]);
        } else {
          // General question or comment while brief is pending
          let fullContent = '';
          let currentAgent = '';
          let messageAdded = false;
          
          setGenerationStatus('Processing your question...');
          for await (const response of streamChat(content, conversationId, userId, signal)) {
            if (response.type === 'agent_response') {
              fullContent = response.content;
              currentAgent = response.agent || '';
              
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
          setGenerationStatus('');
        }
      } else if (confirmedBrief && !generatedContent) {
        // Brief confirmed, in product selection phase - treat messages as product selection requests
        setGenerationStatus('Finding products...');
        const result = await selectProducts(content, selectedProducts, conversationId, userId, signal);
        
        // Update selected products with the result
        setSelectedProducts(result.products || []);
        setGenerationStatus('');
        
        const assistantMessage: ChatMessage = {
          id: uuidv4(),
          role: 'assistant',
          content: result.message || 'Products updated.',
          agent: 'ProductAgent',
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        // Check if this looks like a creative brief
        const briefKeywords = ['campaign', 'marketing', 'target audience', 'objective', 'deliverable'];
        const isBriefLike = briefKeywords.some(kw => content.toLowerCase().includes(kw));
        
        if (isBriefLike && !confirmedBrief) {
          // Parse as a creative brief
          setGenerationStatus('Parsing creative brief...');
          const parsed = await parseBrief(content, conversationId, userId, signal);
          setPendingBrief(parsed.brief);
          setGenerationStatus('');
          
          const assistantMessage: ChatMessage = {
            id: uuidv4(),
            role: 'assistant',
            content: "I've parsed your creative brief. Please review the details below and let me know if you'd like to make any changes. You can say things like \"change the target audience to...\" or \"add a call to action...\". When everything looks good, click **Confirm Brief** to proceed.",
            agent: 'PlanningAgent',
            timestamp: new Date().toISOString(),
          };
          setMessages(prev => [...prev, assistantMessage]);
        } else {
          // Stream chat response
          let fullContent = '';
          let currentAgent = '';
          let messageAdded = false;
          
          setGenerationStatus('Processing your request...');
          for await (const response of streamChat(content, conversationId, userId, signal)) {
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
          setGenerationStatus('');
        }
      }
    } catch (error) {
      // Check if this was a user-initiated cancellation
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request cancelled by user');
        const cancelMessage: ChatMessage = {
          id: uuidv4(),
          role: 'assistant',
          content: 'Generation stopped.',
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, cancelMessage]);
      } else {
        console.error('Error sending message:', error);
        const errorMessage: ChatMessage = {
          id: uuidv4(),
          role: 'assistant',
          content: 'Sorry, there was an error processing your request. Please try again.',
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } finally {
      setIsLoading(false);
      setGenerationStatus('');
      abortControllerRef.current = null;
      // Trigger refresh of chat history after message is sent
      setHistoryRefreshTrigger(prev => prev + 1);
    }
  }, [conversationId, userId, confirmedBrief, pendingBrief, selectedProducts, generatedContent]);

  const handleBriefConfirm = useCallback(async () => {
    if (!pendingBrief) return;
    
    try {
      const { confirmBrief } = await import('./api');
      await confirmBrief(pendingBrief, conversationId, userId);
      setConfirmedBrief(pendingBrief);
      setPendingBrief(null);
      
      const assistantMessage: ChatMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: "Great! Your creative brief has been confirmed. Now let's select products to feature in your campaign. Tell me what products you'd like to include - you can describe them by name, category, or characteristics.",
        agent: 'ProductAgent',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error confirming brief:', error);
    }
  }, [conversationId, userId, pendingBrief]);

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

  const handleProductsStartOver = useCallback(() => {
    setSelectedProducts([]);
    setConfirmedBrief(null);
    const assistantMessage: ChatMessage = {
      id: uuidv4(),
      role: 'assistant',
      content: 'Starting over. Please provide your creative brief to begin a new campaign.',
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, assistantMessage]);
  }, []);

  const handleStopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  const handleGenerateContent = useCallback(async () => {
    if (!confirmedBrief) return;
    
    setIsLoading(true);
    setGenerationStatus('Starting content generation...');
    
    // Create new abort controller for this request
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;
    
    try {
      const { streamGenerateContent } = await import('./api');
      
      for await (const response of streamGenerateContent(
        confirmedBrief,
        selectedProducts,
        true,
        conversationId,
        userId,
        signal
      )) {
        // Handle heartbeat events to show progress
        if (response.type === 'heartbeat') {
          // Use the message from the heartbeat directly - it contains the stage description
          const statusMessage = response.content || 'Generating content...';
          const elapsed = (response as { elapsed?: number }).elapsed || 0;
          setGenerationStatus(`${statusMessage} (${elapsed}s)`);
          continue;
        }
        
        if (response.is_final && response.type !== 'error') {
          setGenerationStatus('Processing results...');
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
              // Capture any generation errors
              error: rawContent.error,
              image_error: rawContent.image_error,
              text_error: rawContent.text_error,
            };
            setGeneratedContent(content);
            setGenerationStatus('');
            
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
          setGenerationStatus('');
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
      // Check if this was a user-initiated cancellation
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Content generation cancelled by user');
        const cancelMessage: ChatMessage = {
          id: uuidv4(),
          role: 'assistant',
          content: 'Content generation stopped.',
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, cancelMessage]);
      } else {
        console.error('Error generating content:', error);
        const errorMessage: ChatMessage = {
          id: uuidv4(),
          role: 'assistant',
          content: 'Sorry, there was an error generating content. Please try again.',
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } finally {
      setIsLoading(false);
      setGenerationStatus('');
      abortControllerRef.current = null;
    }
  }, [confirmedBrief, selectedProducts, conversationId]);

  // Get user initials for avatar
  const getUserInitials = () => {
    if (!userId) return 'U';
    // If we have a name, use first letter of first and last name
    const parts = userId.split('@')[0].split('.');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return userId[0].toUpperCase();
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        padding: 'clamp(8px, 1.5vw, 12px) clamp(16px, 3vw, 24px)',
        borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
        backgroundColor: tokens.colorNeutralBackground1,
        flexShrink: 0,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'clamp(8px, 1.5vw, 10px)' }}>
          <ContosoLogo />
          <Text weight="semibold" size={500} style={{ color: tokens.colorNeutralForeground1, fontSize: 'clamp(16px, 2.5vw, 20px)' }}>
            Contoso
          </Text>
        </div>
        <Avatar 
          name={userId || 'User'}
          initials={getUserInitials()}
          color="colorful"
          size={36}
        />
      </header>
      
      {/* Main Content */}
      <div className="main-content">
        {/* Chat Panel - main area */}
        <div className="chat-panel">
          <ChatPanel
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            generationStatus={generationStatus}
            onStopGeneration={handleStopGeneration}
            pendingBrief={pendingBrief}
            confirmedBrief={confirmedBrief}
            generatedContent={generatedContent}
            selectedProducts={selectedProducts}
            onBriefConfirm={handleBriefConfirm}
            onBriefCancel={handleBriefCancel}
            onGenerateContent={handleGenerateContent}
            onRegenerateContent={handleGenerateContent}
            onProductsStartOver={handleProductsStartOver}
            imageGenerationEnabled={imageGenerationEnabled}
          />
        </div>
        
        {/* Chat History Sidebar - RIGHT side */}
        <div className="history-panel">
          <ChatHistory
            currentConversationId={conversationId}
            currentMessages={messages}
            onSelectConversation={handleSelectConversation}
            onNewConversation={handleNewConversation}
            refreshTrigger={historyRefreshTrigger}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
