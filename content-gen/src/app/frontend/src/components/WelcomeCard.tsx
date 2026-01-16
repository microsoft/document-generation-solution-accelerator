import {
  Card,
  Text,
  tokens,
} from '@fluentui/react-components';
import SamplePromptIcon from '../styles/images/SamplePrompt.png';

// Copilot-style hexagon icon
function CopilotIcon() {
  return (
    <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="copilotGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#6366F1" />
          <stop offset="50%" stopColor="#8B5CF6" />
          <stop offset="100%" stopColor="#06B6D4" />
        </linearGradient>
      </defs>
      <path 
        d="M24 4L42 14V34L24 44L6 34V14L24 4Z" 
        fill="url(#copilotGradient)"
      />
      <path 
        d="M24 12L36 18V30L24 36L12 30V18L24 12Z" 
        fill="white" 
        fillOpacity="0.3"
      />
      <circle cx="24" cy="24" r="6" fill="white"/>
    </svg>
  );
}

interface SuggestionCard {
  title: string;
  description: string;
  prompt: string;
}

const suggestions: SuggestionCard[] = [
  {
    title: 'Generate ad copy and image ideas for a social media campaign promoting Paint for Home Décor.',
    description: 'Generate compelling copy for your next campaign',
    prompt: 'Generate ad copy and image ideas for a social media campaign promoting Paint for Home Décor.',
  },
  {
    title: 'Summarize my creative brief and suggest mood, audience, and image style for the campaign.',
    description: 'Summarize your creative brief for better insights',
    prompt: 'Summarize my creative brief and suggest mood, audience, and image style for the campaign.',
  },
  {
    title: 'Create a multi-modal content plan with visuals and captions based on brand guidelines.',
    description: 'Create a content plan with visuals and captions',
    prompt: 'Create a multi-modal content plan with visuals and captions based on brand guidelines.',
  },
];

interface WelcomeCardProps {
  onSuggestionClick: (prompt: string) => void;
}

export function WelcomeCard({ onSuggestionClick }: WelcomeCardProps) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      flex: 1,
      padding: 'clamp(16px, 4vw, 32px)',
      gap: 'clamp(16px, 3vw, 24px)',
      width: '100%',
      boxSizing: 'border-box',
    }}>
      {/* Today label */}
      <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
        Today
      </Text>
      
      {/* Welcome card with suggestions inside */}
      <div style={{
        padding: 'clamp(16px, 4vw, 32px)',
        maxWidth: 'min(600px, 100%)',
        width: '100%',
        backgroundColor: tokens.colorNeutralBackground3,
        borderRadius: '12px',
        boxSizing: 'border-box',
      }}>
        {/* Header with icon and welcome message */}
        <div style={{ textAlign: 'center', marginBottom: 'clamp(16px, 3vw, 24px)' }}>
          <div style={{ marginBottom: 'clamp(12px, 2vw, 16px)', display: 'flex', justifyContent: 'center' }}>
            <CopilotIcon />
          </div>
          <Text 
            size={400} 
            weight="semibold" 
            block 
            style={{ 
              marginBottom: '8px', 
              textAlign: 'center',
              fontSize: 'clamp(16px, 2.5vw, 20px)',
            }}
          >
            Welcome to your Content Generation Accelerator
          </Text>
          <Text 
            size={300} 
            style={{ 
              color: tokens.colorNeutralForeground3, 
              display: 'block', 
              textAlign: 'center',
              fontSize: 'clamp(13px, 2vw, 15px)',
            }}
          >
            Here are the options I can assist you with today
          </Text>
        </div>
        
        {/* Suggestion cards - vertical layout */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 'clamp(8px, 1.5vw, 12px)',
        }}>
          {suggestions.map((suggestion, index) => (
            <Card
              key={index}
              onClick={() => onSuggestionClick(suggestion.prompt)}
              style={{
                padding: 'clamp(12px, 2vw, 16px)',
                cursor: 'pointer',
                backgroundColor: tokens.colorNeutralBackground1,
                border: `1px solid ${tokens.colorNeutralStroke1}`,
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = tokens.colorNeutralBackground1Hover;
                e.currentTarget.style.borderColor = tokens.colorBrandStroke1;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = tokens.colorNeutralBackground1;
                e.currentTarget.style.borderColor = tokens.colorNeutralStroke1;
              }}
            >
              <div style={{ 
                display: 'flex',
                alignItems: 'center',
                gap: 'clamp(8px, 1.5vw, 12px)',
              }}>
                <div style={{ 
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: 'clamp(32px, 5vw, 40px)',
                  height: 'clamp(32px, 5vw, 40px)',
                  minWidth: '32px',
                  minHeight: '32px',
                  flexShrink: 0,
                }}>
                  <img 
                    src={SamplePromptIcon} 
                    alt="Sample prompt" 
                    style={{ 
                      width: '100%', 
                      height: '100%', 
                      objectFit: 'contain' 
                    }} 
                  />
                </div>
                <div style={{ minWidth: 0, flex: 1 }}>
                  <Text 
                    weight="semibold" 
                    size={300} 
                    block 
                    style={{ 
                      marginBottom: '2px',
                      fontSize: 'clamp(13px, 1.8vw, 15px)',
                    }}
                  >
                    {suggestion.title}
                  </Text>
                  <Text 
                    size={200} 
                    style={{ 
                      color: tokens.colorNeutralForeground3,
                      fontSize: 'clamp(11px, 1.5vw, 13px)',
                    }}
                  >
                    {suggestion.description}
                  </Text>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
