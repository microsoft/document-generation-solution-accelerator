import {
  Button,
  Text,
  tokens,
} from '@fluentui/react-components';
import {
  Checkmark20Regular,
  ArrowReset20Regular,
} from '@fluentui/react-icons';
import type { CreativeBrief } from '../types';

interface BriefReviewProps {
  brief: CreativeBrief;
  onConfirm: () => void;
  onStartOver: () => void;
  isAwaitingResponse?: boolean;
}

// Define the brief fields to display - matching Figma order
const briefFields: { key: keyof CreativeBrief; label: string; prefix?: string }[] = [
  { key: 'objectives', label: 'Objective', prefix: '• ' },
  { key: 'target_audience', label: 'Audience', prefix: '• ' },
  { key: 'tone_and_style', label: 'Tone & Style', prefix: '• ' },
  { key: 'deliverable', label: 'Deliverables', prefix: '• ' },
];

// Additional fields that appear in the main content area
const contentFields: { key: keyof CreativeBrief; label: string }[] = [
  { key: 'overview', label: '' },
  { key: 'key_message', label: 'Key Message' },
  { key: 'visual_guidelines', label: '' },
  { key: 'cta', label: 'CTA' },
  { key: 'timelines', label: 'Timeline' },
];

export function BriefReview({
  brief,
  onConfirm,
  onStartOver,
  isAwaitingResponse = false,
}: BriefReviewProps) {

  return (
    <div className="message assistant" style={{ 
      width: '100%',
      alignSelf: 'flex-start',
      backgroundColor: tokens.colorNeutralBackground3,
      padding: '12px 16px',
      borderRadius: '8px',
      margin: '16px 0 0 0',
    }}>
      {/* Header text */}
      <Text 
        size={300} 
        style={{ 
          display: 'block',
          marginBottom: '12px',
          color: tokens.colorNeutralForeground1,
        }}
      >
        Thanks—here's my understanding:
      </Text>
      
      {/* Brief Fields - Bullet point list like Figma */}
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '8px',
        marginBottom: '16px',
      }}>
        {briefFields.map(({ key, label, prefix }) => {
          const value = brief[key];
          if (!value?.trim()) return null;
          
          return (
            <div key={key} style={{ 
              display: 'flex',
              alignItems: 'flex-start',
              gap: '4px',
            }}>
              <Text size={200} style={{ color: tokens.colorNeutralForeground1 }}>
                {prefix}
              </Text>
              <div>
                <Text 
                  weight="semibold" 
                  size={200}
                  style={{ color: tokens.colorNeutralForeground1 }}
                >
                  {label}:
                </Text>
                {' '}
                <Text size={200} style={{ color: tokens.colorNeutralForeground2 }}>
                  {value}
                </Text>
              </div>
            </div>
          );
        })}
      </div>

      {/* Additional content fields in a bordered card - like Figma */}
      {(brief.overview || brief.key_message || brief.visual_guidelines) && (
        <div style={{
          padding: '16px',
          backgroundColor: tokens.colorNeutralBackground2,
          borderRadius: '8px',
          marginBottom: '16px',
          border: `1px solid ${tokens.colorNeutralStroke2}`,
        }}>
          {/* Campaign Objective section */}
          {brief.overview && (
            <div style={{ marginBottom: '12px' }}>
              <Text 
                weight="semibold" 
                size={300}
                style={{ 
                  color: tokens.colorNeutralForeground1,
                  display: 'block',
                  marginBottom: '4px',
                }}
              >
                Campaign Objective
              </Text>
              <Text size={200} style={{ color: tokens.colorNeutralForeground2, lineHeight: '1.5' }}>
                {brief.overview}
              </Text>
            </div>
          )}

          {/* Audience section */}
          {brief.target_audience && (
            <div style={{ marginBottom: '12px' }}>
              <Text 
                weight="semibold" 
                size={300}
                style={{ 
                  color: tokens.colorNeutralForeground1,
                  display: 'block',
                  marginBottom: '4px',
                }}
              >
                Audience
              </Text>
              <Text size={200} style={{ color: tokens.colorNeutralForeground2, lineHeight: '1.5' }}>
                {brief.target_audience}
              </Text>
            </div>
          )}

          {/* Visual guidelines / Creation instructions */}
          {brief.visual_guidelines && (
            <div style={{ marginBottom: '12px' }}>
              <Text size={200} style={{ color: tokens.colorNeutralForeground2, lineHeight: '1.5' }}>
                {brief.visual_guidelines}
              </Text>
            </div>
          )}

          {/* Tone & Style section */}
          {brief.tone_and_style && (
            <div style={{ marginBottom: '12px' }}>
              <Text 
                weight="semibold" 
                size={300}
                style={{ 
                  color: tokens.colorNeutralForeground1,
                  display: 'block',
                  marginBottom: '4px',
                }}
              >
                Tone & Style:
              </Text>
              <Text size={200} style={{ color: tokens.colorNeutralForeground2, lineHeight: '1.5' }}>
                {brief.tone_and_style}
              </Text>
            </div>
          )}

          {/* Deliverables section */}
          {brief.deliverable && (
            <div>
              <Text 
                weight="semibold" 
                size={300}
                style={{ 
                  color: tokens.colorNeutralForeground1,
                  display: 'block',
                  marginBottom: '4px',
                }}
              >
                Deliverables:
              </Text>
              <Text size={200} style={{ color: tokens.colorNeutralForeground2, lineHeight: '1.5' }}>
                {brief.deliverable}
              </Text>
            </div>
          )}
        </div>
      )}
      
      {/* Action Buttons - Matching Figma styling */}
      <div style={{ 
        display: 'flex', 
        gap: '8px',
        flexWrap: 'wrap',
      }}>
        <Button
          appearance="outline"
          icon={<ArrowReset20Regular />}
          onClick={onStartOver}
          size="small"
          disabled={isAwaitingResponse}
          style={{
            borderColor: tokens.colorNeutralStroke1,
          }}
        >
          Start over
        </Button>
        <Button
          appearance="primary"
          icon={<Checkmark20Regular />}
          onClick={onConfirm}
          size="small"
          disabled={isAwaitingResponse}
        >
          Confirm brief
        </Button>
      </div>

      {/* AI disclaimer footer */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: '12px',
        paddingTop: '8px',
      }}>
        <Text size={100} style={{ color: tokens.colorNeutralForeground4 }}>
          AI-generated content may be incorrect
        </Text>
      </div>
    </div>
  );
}
