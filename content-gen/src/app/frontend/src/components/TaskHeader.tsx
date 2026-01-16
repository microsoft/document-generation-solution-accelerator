import { Text, tokens } from '@fluentui/react-components';

interface TaskHeaderProps {
  title?: string;
  description?: string;
  isVisible?: boolean;
}

/**
 * TaskHeader - Purple gradient banner showing current task
 * Matches the Figma design with gradient background
 */
export function TaskHeader({ 
  title: _title = 'Content Generation',
  description,
  isVisible = true,
}: TaskHeaderProps) {
  if (!isVisible || !description) return null;

  return (
    <div style={{
      background: 'linear-gradient(135deg, #5c3d91 0%, #6366f1 50%, #8b5cf6 100%)',
      padding: '16px 24px',
      borderRadius: '8px',
      margin: '16px 16px 0 16px',
    }}>
      <Text 
        size={300}
        style={{ 
          color: 'white',
          display: 'block',
          lineHeight: '1.5',
        }}
      >
        {description}
      </Text>
    </div>
  );
}

/**
 * Simple inline task indicator that appears at the top of messages
 * Alternative to full banner - shows as a subtle header
 */
export function TaskIndicator({ 
  task,
  isActive = true,
}: { 
  task: string;
  isActive?: boolean;
}) {
  if (!isActive || !task) return null;

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '8px 16px',
      backgroundColor: tokens.colorBrandBackground2,
      borderRadius: '4px',
      marginBottom: '16px',
    }}>
      <div style={{
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        backgroundColor: tokens.colorBrandBackground,
        animation: 'pulse 2s infinite',
      }} />
      <Text size={200} style={{ color: tokens.colorBrandForeground1 }}>
        {task}
      </Text>
    </div>
  );
}
