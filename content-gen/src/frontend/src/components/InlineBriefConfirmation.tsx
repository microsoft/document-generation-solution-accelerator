import { useState } from 'react';
import {
  Card,
  Button,
  Input,
  Textarea,
  Text,
  Badge,
  tokens,
} from '@fluentui/react-components';
import {
  Checkmark24Regular,
  Dismiss24Regular,
  Edit24Regular,
  Bot24Regular,
} from '@fluentui/react-icons';
import type { CreativeBrief } from '../types';

interface InlineBriefConfirmationProps {
  brief: CreativeBrief;
  onConfirm: (brief: CreativeBrief) => void;
  onCancel: () => void;
  onEdit: (brief: CreativeBrief) => void;
}

export function InlineBriefConfirmation({
  brief,
  onConfirm,
  onCancel,
  onEdit,
}: InlineBriefConfirmationProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedBrief, setEditedBrief] = useState<CreativeBrief>(brief);

  const handleFieldChange = (field: keyof CreativeBrief, value: string) => {
    setEditedBrief(prev => ({ ...prev, [field]: value }));
  };

  const handleSaveEdit = () => {
    onEdit(editedBrief);
    setIsEditing(false);
  };

  const briefFields: { key: keyof CreativeBrief; label: string; multiline?: boolean }[] = [
    { key: 'overview', label: 'Overview', multiline: true },
    { key: 'objectives', label: 'Objectives', multiline: true },
    { key: 'target_audience', label: 'Target Audience' },
    { key: 'key_message', label: 'Key Message', multiline: true },
    { key: 'tone_and_style', label: 'Tone & Style' },
    { key: 'deliverable', label: 'Deliverable' },
    { key: 'timelines', label: 'Timelines' },
    { key: 'visual_guidelines', label: 'Visual Guidelines', multiline: true },
    { key: 'cta', label: 'Call to Action' },
  ];

  return (
    <div style={{ 
      display: 'flex',
      gap: '8px',
      alignItems: 'flex-start',
      maxWidth: '100%'
    }}>
      {/* Bot Avatar */}
      <div style={{ 
        width: '32px',
        height: '32px',
        borderRadius: '50%',
        backgroundColor: tokens.colorNeutralBackground3,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0
      }}>
        <Bot24Regular style={{ fontSize: '16px' }} />
      </div>
      
      <Card style={{ 
        flex: 1,
        maxWidth: 'calc(100% - 40px)',
        backgroundColor: tokens.colorNeutralBackground1
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
          <Badge appearance="outline" size="small">
            PlanningAgent
          </Badge>
          {!isEditing && (
            <Button
              appearance="subtle"
              icon={<Edit24Regular />}
              onClick={() => setIsEditing(true)}
              size="small"
            >
              Edit
            </Button>
          )}
        </div>
        
        <Text weight="semibold" size={300} block style={{ marginBottom: '8px' }}>
          Confirm Your Creative Brief
        </Text>
        
        <Text size={200} style={{ color: tokens.colorNeutralForeground3, marginBottom: '12px', display: 'block' }}>
          Please review the parsed brief and confirm or edit before proceeding.
        </Text>
        
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '8px',
          maxHeight: '300px',
          overflowY: 'auto',
          paddingRight: '8px'
        }}>
          {briefFields.map(({ key, label, multiline }) => (
            <div key={key} style={{ 
              padding: '8px', 
              backgroundColor: tokens.colorNeutralBackground2, 
              borderRadius: '4px' 
            }}>
              <Text weight="semibold" size={100} style={{ color: tokens.colorNeutralForeground3, display: 'block', marginBottom: '2px' }}>
                {label}
              </Text>
              {isEditing ? (
                multiline ? (
                  <Textarea
                    value={editedBrief[key]}
                    onChange={(e) => handleFieldChange(key, e.target.value)}
                    resize="vertical"
                    style={{ width: '100%' }}
                    size="small"
                  />
                ) : (
                  <Input
                    value={editedBrief[key]}
                    onChange={(e) => handleFieldChange(key, e.target.value)}
                    style={{ width: '100%' }}
                    size="small"
                  />
                )
              ) : (
                <Text 
                  size={200}
                  style={{ 
                    color: brief[key] ? tokens.colorNeutralForeground1 : tokens.colorNeutralForeground4,
                    fontStyle: brief[key] ? 'normal' : 'italic'
                  }}
                >
                  {brief[key] || 'Not specified'}
                </Text>
              )}
            </div>
          ))}
        </div>
        
        <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
          {isEditing ? (
            <>
              <Button
                appearance="primary"
                icon={<Checkmark24Regular />}
                onClick={handleSaveEdit}
                size="small"
              >
                Save Changes
              </Button>
              <Button
                appearance="subtle"
                onClick={() => {
                  setEditedBrief(brief);
                  setIsEditing(false);
                }}
                size="small"
              >
                Cancel
              </Button>
            </>
          ) : (
            <>
              <Button
                appearance="primary"
                icon={<Checkmark24Regular />}
                onClick={() => onConfirm(brief)}
                size="small"
              >
                Confirm Brief
              </Button>
              <Button
                appearance="subtle"
                icon={<Dismiss24Regular />}
                onClick={onCancel}
                size="small"
              >
                Start Over
              </Button>
            </>
          )}
        </div>
      </Card>
    </div>
  );
}
