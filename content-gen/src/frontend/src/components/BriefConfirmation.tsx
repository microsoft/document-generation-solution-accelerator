import { useState } from 'react';
import {
  Card,
  CardHeader,
  Button,
  Input,
  Textarea,
  Text,
  Title3,
  tokens,
} from '@fluentui/react-components';
import {
  Checkmark24Regular,
  Dismiss24Regular,
  Edit24Regular,
} from '@fluentui/react-icons';
import type { CreativeBrief } from '../types';

interface BriefConfirmationProps {
  brief: CreativeBrief;
  onConfirm: (brief: CreativeBrief) => void;
  onCancel: () => void;
  onEdit: (brief: CreativeBrief) => void;
}

export function BriefConfirmation({
  brief,
  onConfirm,
  onCancel,
  onEdit,
}: BriefConfirmationProps) {
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
    <Card className="panel-card">
      <CardHeader
        header={<Title3>Confirm Creative Brief</Title3>}
        action={
          !isEditing ? (
            <Button
              appearance="subtle"
              icon={<Edit24Regular />}
              onClick={() => setIsEditing(true)}
            >
              Edit
            </Button>
          ) : undefined
        }
      />
      
      <Text size={200} style={{ color: tokens.colorNeutralForeground3, marginBottom: '16px' }}>
        Please review the parsed brief and confirm or edit before proceeding.
      </Text>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {briefFields.map(({ key, label, multiline }) => (
          <div key={key}>
            <Text weight="semibold" size={200} style={{ marginBottom: '4px', display: 'block' }}>
              {label}
            </Text>
            {isEditing ? (
              multiline ? (
                <Textarea
                  value={editedBrief[key]}
                  onChange={(e) => handleFieldChange(key, e.target.value)}
                  resize="vertical"
                  style={{ width: '100%' }}
                />
              ) : (
                <Input
                  value={editedBrief[key]}
                  onChange={(e) => handleFieldChange(key, e.target.value)}
                  style={{ width: '100%' }}
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
      
      <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
        {isEditing ? (
          <>
            <Button
              appearance="primary"
              icon={<Checkmark24Regular />}
              onClick={handleSaveEdit}
            >
              Save Changes
            </Button>
            <Button
              appearance="subtle"
              onClick={() => {
                setEditedBrief(brief);
                setIsEditing(false);
              }}
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
            >
              Confirm Brief
            </Button>
            <Button
              appearance="subtle"
              icon={<Dismiss24Regular />}
              onClick={onCancel}
            >
              Start Over
            </Button>
          </>
        )}
      </div>
    </Card>
  );
}
