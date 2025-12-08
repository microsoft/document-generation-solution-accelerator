import {
  Card,
  Button,
  Text,
  Badge,
  tokens,
} from '@fluentui/react-components';
import {
  Checkmark24Regular,
  Dismiss24Regular,
  Bot24Regular,
} from '@fluentui/react-icons';
import type { CreativeBrief } from '../types';

interface BriefReviewProps {
  brief: CreativeBrief;
  onConfirm: () => void;
  onStartOver: () => void;
  isAwaitingResponse?: boolean;
}

const briefFields: { key: keyof CreativeBrief; label: string }[] = [
  { key: 'overview', label: 'Overview' },
  { key: 'objectives', label: 'Objectives' },
  { key: 'target_audience', label: 'Target Audience' },
  { key: 'key_message', label: 'Key Message' },
  { key: 'tone_and_style', label: 'Tone & Style' },
  { key: 'deliverable', label: 'Deliverable' },
  { key: 'timelines', label: 'Timelines' },
  { key: 'visual_guidelines', label: 'Visual Guidelines' },
  { key: 'cta', label: 'Call to Action' },
];

export function BriefReview({
  brief,
  onConfirm,
  onStartOver,
  isAwaitingResponse = false,
}: BriefReviewProps) {
  // Count how many fields are populated
  const populatedFields = briefFields.filter(({ key }) => brief[key]?.trim()).length;
  
  return (
    <div style={{ 
      display: 'flex',
      gap: 'clamp(6px, 1vw, 8px)',
      alignItems: 'flex-start',
      maxWidth: '100%'
    }}>
      {/* Bot Avatar */}
      <div style={{ 
        width: 'clamp(28px, 4vw, 32px)',
        height: 'clamp(28px, 4vw, 32px)',
        minWidth: '28px',
        minHeight: '28px',
        borderRadius: '50%',
        backgroundColor: tokens.colorNeutralBackground3,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0
      }}>
        <Bot24Regular style={{ fontSize: 'clamp(14px, 2vw, 16px)' }} />
      </div>
      
      <Card style={{ 
        flex: 1,
        maxWidth: 'calc(100% - 40px)',
        backgroundColor: tokens.colorNeutralBackground1,
        minWidth: 0,
      }}>
        <Badge appearance="outline" size="small" style={{ marginBottom: '8px' }}>
          PlanningAgent
        </Badge>
        
        <Text 
          weight="semibold" 
          size={300} 
          block 
          style={{ 
            marginBottom: '8px',
            fontSize: 'clamp(14px, 2vw, 16px)',
          }}
        >
          Here's what I've captured from your creative brief:
        </Text>
        
        {/* Brief Fields - Read Only */}
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '8px',
          maxHeight: 'clamp(250px, 40vh, 350px)',
          overflowY: 'auto',
          paddingRight: '8px',
          marginBottom: '16px',
        }}>
          {briefFields.map(({ key, label }) => {
            const value = brief[key];
            if (!value?.trim()) return null; // Skip empty fields
            
            return (
              <div key={key} style={{ 
                padding: 'clamp(8px, 1.5vw, 12px)', 
                backgroundColor: tokens.colorNeutralBackground2, 
                borderRadius: '6px',
              }}>
                <Text 
                  weight="semibold" 
                  size={100} 
                  style={{ 
                    color: tokens.colorBrandForeground1, 
                    display: 'block', 
                    marginBottom: '4px',
                    fontSize: 'clamp(11px, 1.4vw, 12px)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  }}
                >
                  {label}
                </Text>
                <Text 
                  size={200}
                  style={{ 
                    color: tokens.colorNeutralForeground1,
                    fontSize: 'clamp(13px, 1.8vw, 14px)',
                    lineHeight: '1.5',
                  }}
                >
                  {value}
                </Text>
              </div>
            );
          })}
        </div>
        
        {/* Prompt for feedback */}
        <div style={{
          padding: 'clamp(12px, 2vw, 16px)',
          backgroundColor: tokens.colorNeutralBackground3,
          borderRadius: '8px',
          marginBottom: '16px',
          borderLeft: `3px solid ${tokens.colorBrandBackground}`,
        }}>
          <Text 
            size={200} 
            style={{ 
              color: tokens.colorNeutralForeground1,
              fontSize: 'clamp(13px, 1.8vw, 14px)',
              lineHeight: '1.6',
            }}
          >
            {populatedFields < 5 ? (
              <>
                I've captured <strong>{populatedFields}</strong> of 9 key areas. Would you like to add more details? 
                You can tell me things like:
                <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
                  <li>"The target audience should be homeowners aged 35-55"</li>
                  <li>"Add a timeline of 2 weeks for the campaign"</li>
                  <li>"The tone should be warm and inviting"</li>
                </ul>
              </>
            ) : (
              <>
                Does this look correct? You can:
                <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
                  <li><strong>Modify:</strong> "Change the target audience to young professionals"</li>
                  <li><strong>Add:</strong> "Add a call to action: Shop Now"</li>
                  <li><strong>Remove:</strong> "Remove the timelines section"</li>
                </ul>
                Or if everything looks good, click <strong>Confirm Brief</strong> to proceed.
              </>
            )}
          </Text>
        </div>
        
        {/* Action Buttons */}
        <div style={{ 
          display: 'flex', 
          gap: '8px',
          flexWrap: 'wrap',
        }}>
          <Button
            appearance="primary"
            icon={<Checkmark24Regular />}
            onClick={onConfirm}
            size="small"
            disabled={isAwaitingResponse}
          >
            Confirm Brief
          </Button>
          <Button
            appearance="subtle"
            icon={<Dismiss24Regular />}
            onClick={onStartOver}
            size="small"
            disabled={isAwaitingResponse}
          >
            Start Over
          </Button>
        </div>
      </Card>
    </div>
  );
}
