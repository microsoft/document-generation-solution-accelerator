import {
  Button,
  Text,
  tokens,
} from '@fluentui/react-components';
import type { CreativeBrief } from '../types';

interface BriefReviewProps {
  brief: CreativeBrief;
  onConfirm: () => void;
  onStartOver: () => void;
  isAwaitingResponse?: boolean;
}

const briefFields: { key: keyof CreativeBrief; label: string; prefix?: string }[] = [
  { key: 'objectives', label: 'Objective', prefix: '• ' },
  { key: 'target_audience', label: 'Audience', prefix: '• ' },
  { key: 'key_message', label: 'Key Message', prefix: '• ' },
  { key: 'tone_and_style', label: 'Tone & Style', prefix: '• ' },
  { key: 'timelines', label: 'Timelines', prefix: '• ' },
  { key: 'cta', label: 'Call to Action', prefix: '• ' },
];

// Mapping of field keys to user-friendly labels for the 9 key areas
const fieldLabels: Record<keyof CreativeBrief, string> = {
  overview: 'Overview',
  objectives: 'Objectives',
  target_audience: 'Target Audience',
  key_message: 'Key Message',
  tone_and_style: 'Tone and Style',
  deliverable: 'Deliverable',
  timelines: 'Timelines',
  visual_guidelines: 'Visual Guidelines',
  cta: 'Call to Action',
};

export function BriefReview({
  brief,
  onConfirm,
  onStartOver,
  isAwaitingResponse = false,
}: BriefReviewProps) {
  const allFields: (keyof CreativeBrief)[] = [
    'overview', 'objectives', 'target_audience', 'key_message', 
    'tone_and_style', 'deliverable', 'timelines', 'visual_guidelines', 'cta'
  ];
  const populatedFields = allFields.filter(key => brief[key]?.trim()).length;
  const missingFields = allFields.filter(key => !brief[key]?.trim());

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
      {(brief.overview || brief.key_message || brief.visual_guidelines || brief.timelines || brief.cta) && (
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

          {/* Key Message section */}
          {brief.key_message && (
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
                Key Message
              </Text>
              <Text size={200} style={{ color: tokens.colorNeutralForeground2, lineHeight: '1.5' }}>
                {brief.key_message}
              </Text>
            </div>
          )}

          {/* Visual guidelines / Creation instructions */}
          {brief.visual_guidelines && (
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
                Visual Guidelines
              </Text>
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
            <div style={{ marginBottom: brief.timelines || brief.cta ? '12px' : '0' }}>
              <Text 
                weight="semibold" 
                size={300}
                style={{ 
                  color: tokens.colorNeutralForeground1,
                  display: 'block',
                  marginBottom: '4px',
                }}
              >
                Deliverables
              </Text>
              <Text size={200} style={{ color: tokens.colorNeutralForeground2, lineHeight: '1.5' }}>
                {brief.deliverable}
              </Text>
            </div>
          )}

          {/* Timelines section */}
          {brief.timelines && (
            <div style={{ marginBottom: brief.cta ? '12px' : '0' }}>
              <Text 
                weight="semibold" 
                size={300}
                style={{ 
                  color: tokens.colorNeutralForeground1,
                  display: 'block',
                  marginBottom: '4px',
                }}
              >
                Timelines
              </Text>
              <Text size={200} style={{ color: tokens.colorNeutralForeground2, lineHeight: '1.5' }}>
                {brief.timelines}
              </Text>
            </div>
          )}

          {/* Call to Action section */}
          {brief.cta && (
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
                Call to Action
              </Text>
              <Text size={200} style={{ color: tokens.colorNeutralForeground2, lineHeight: '1.5' }}>
                {brief.cta}
              </Text>
            </div>
          )}
        </div>
      )}

      <div style={{
        padding: '12px 16px',
        backgroundColor: tokens.colorNeutralBackground2,
        borderRadius: '8px',
        marginBottom: '16px',
        borderLeft: `3px solid ${tokens.colorBrandBackground}`,
      }}>
        <Text size={200} style={{ color: tokens.colorNeutralForeground1, lineHeight: '1.6' }}>
          {populatedFields < 5 ? (
            <>
              I've captured <strong>{populatedFields}</strong> of 9 key areas. Would you like to add more details? 
              You are missing: <strong>{missingFields.map(f => fieldLabels[f]).join(', ')}</strong>.
              <br /><br />
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
              Or if everything looks good, click <strong>Confirm brief</strong> to proceed.
            </>
          )}
        </Text>
      </div>
      
      {/* Action Buttons - Matching Figma styling */}
      <div style={{ 
        display: 'flex', 
        gap: '8px',
        flexWrap: 'wrap',
      }}>
        <Button
          appearance="outline"
          onClick={onStartOver}
          size="small"
          disabled={isAwaitingResponse}
          style={{
            borderColor: tokens.colorNeutralStroke1,
            fontWeight: 600,
          }}
        >
          Start over
        </Button>
        <Button
          appearance="primary"
          onClick={onConfirm}
          size="small"
          disabled={isAwaitingResponse}
          style={{ fontWeight: 600 }}
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
