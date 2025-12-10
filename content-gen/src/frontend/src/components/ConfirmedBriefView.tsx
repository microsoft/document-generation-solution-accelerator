import {
  Card,
  Text,
  Badge,
  tokens,
} from '@fluentui/react-components';
import {
  Bot24Regular,
  Checkmark24Regular,
} from '@fluentui/react-icons';
import type { CreativeBrief } from '../types';

interface ConfirmedBriefViewProps {
  brief: CreativeBrief;
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

export function ConfirmedBriefView({ brief }: ConfirmedBriefViewProps) {
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
        opacity: 0.9,
      }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '8px', 
          marginBottom: '8px' 
        }}>
          <Badge appearance="outline" size="small">
            PlanningAgent
          </Badge>
          <Badge 
            appearance="filled" 
            size="small" 
            color="success"
            icon={<Checkmark24Regular />}
          >
            Brief Confirmed
          </Badge>
        </div>
        
        {/* Brief Fields - Collapsed View */}
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '6px',
          maxHeight: 'clamp(150px, 25vh, 200px)',
          overflowY: 'auto',
          paddingRight: '8px',
        }}>
          {briefFields.map(({ key, label }) => {
            const value = brief[key];
            if (!value?.trim()) return null;
            
            return (
              <div key={key} style={{ 
                padding: 'clamp(6px, 1vw, 8px)', 
                backgroundColor: tokens.colorNeutralBackground2, 
                borderRadius: '4px',
              }}>
                <Text 
                  weight="semibold" 
                  size={100} 
                  style={{ 
                    color: tokens.colorBrandForeground1, 
                    display: 'inline',
                    marginRight: '6px',
                    fontSize: 'clamp(10px, 1.2vw, 11px)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  }}
                >
                  {label}:
                </Text>
                <Text 
                  size={200}
                  style={{ 
                    color: tokens.colorNeutralForeground2,
                    fontSize: 'clamp(12px, 1.6vw, 13px)',
                    lineHeight: '1.4',
                  }}
                >
                  {value.length > 100 ? value.substring(0, 100) + '...' : value}
                </Text>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}
