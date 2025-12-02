import {
  Card,
  Button,
  Text,
  Badge,
  Divider,
  tokens,
} from '@fluentui/react-components';
import {
  ArrowSync24Regular,
  CheckmarkCircle24Regular,
  Warning24Regular,
  Info24Regular,
  ErrorCircle24Regular,
  Copy24Regular,
  ArrowDownload24Regular,
  Bot24Regular,
} from '@fluentui/react-icons';
import type { GeneratedContent, ComplianceViolation } from '../types';

interface InlineContentPreviewProps {
  content: GeneratedContent;
  onRegenerate: () => void;
  isLoading?: boolean;
}

export function InlineContentPreview({ content, onRegenerate, isLoading }: InlineContentPreviewProps) {
  const { text_content, image_content, violations, requires_modification } = content;

  const handleCopyText = () => {
    const textToCopy = [
      text_content?.headline && `Headline: ${text_content.headline}`,
      text_content?.body && `Body: ${text_content.body}`,
      text_content?.cta_text && `CTA: ${text_content.cta_text}`,
      text_content?.tagline && `Tagline: ${text_content.tagline}`,
    ].filter(Boolean).join('\n\n');
    
    navigator.clipboard.writeText(textToCopy);
  };

  const handleDownloadImage = () => {
    if (image_content?.image_url) {
      const link = document.createElement('a');
      link.href = image_content.image_url;
      link.download = 'generated-image.png';
      link.click();
    }
  };

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
            ContentAgent
          </Badge>
          <Button
            appearance="subtle"
            icon={<ArrowSync24Regular />}
            onClick={onRegenerate}
            size="small"
            disabled={isLoading}
          >
            Regenerate
          </Button>
        </div>
        
        <Text weight="semibold" size={300} block style={{ marginBottom: '8px' }}>
          Generated Marketing Content
        </Text>
        
        {/* Approval Status */}
        <div style={{ marginBottom: '12px' }}>
          {requires_modification ? (
            <Badge
              appearance="filled"
              color="danger"
              icon={<ErrorCircle24Regular />}
            >
              Requires Modification
            </Badge>
          ) : violations.length > 0 ? (
            <Badge
              appearance="filled"
              color="warning"
              icon={<Warning24Regular />}
            >
              Review Recommended
            </Badge>
          ) : (
            <Badge
              appearance="filled"
              color="success"
              icon={<CheckmarkCircle24Regular />}
            >
              Approved
            </Badge>
          )}
        </div>
        
        {/* Violations */}
        {violations.length > 0 && (
          <div style={{ marginBottom: '12px' }}>
            <Text weight="semibold" size={200} style={{ marginBottom: '8px', display: 'block' }}>
              Compliance Issues
            </Text>
            {violations.map((violation, index) => (
              <ViolationCard key={index} violation={violation} />
            ))}
          </div>
        )}
        
        <Divider style={{ margin: '12px 0' }} />
        
        {/* Text Content */}
        {text_content && (
          <div style={{ marginBottom: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <Text weight="semibold" size={200}>Text Content</Text>
              <Button
                appearance="subtle"
                icon={<Copy24Regular />}
                size="small"
                onClick={handleCopyText}
              >
                Copy
              </Button>
            </div>
            
            {text_content.headline && (
              <div style={{ marginBottom: '8px', padding: '8px', backgroundColor: tokens.colorNeutralBackground2, borderRadius: '4px' }}>
                <Text size={100} style={{ color: tokens.colorNeutralForeground3 }}>Headline</Text>
                <Text size={300} weight="bold" block>{text_content.headline}</Text>
              </div>
            )}
            
            {text_content.body && (
              <div style={{ marginBottom: '8px', padding: '8px', backgroundColor: tokens.colorNeutralBackground2, borderRadius: '4px' }}>
                <Text size={100} style={{ color: tokens.colorNeutralForeground3 }}>Body</Text>
                <Text size={200} block>{text_content.body}</Text>
              </div>
            )}
            
            {text_content.cta_text && (
              <div style={{ marginBottom: '8px', padding: '8px', backgroundColor: tokens.colorNeutralBackground2, borderRadius: '4px' }}>
                <Text size={100} style={{ color: tokens.colorNeutralForeground3 }}>Call to Action</Text>
                <Text size={200} weight="semibold" block style={{ color: tokens.colorBrandForeground1 }}>
                  {text_content.cta_text}
                </Text>
              </div>
            )}
            
            {text_content.tagline && (
              <div style={{ marginBottom: '8px', padding: '8px', backgroundColor: tokens.colorNeutralBackground2, borderRadius: '4px' }}>
                <Text size={100} style={{ color: tokens.colorNeutralForeground3 }}>Tagline</Text>
                <Text size={200} italic block>{text_content.tagline}</Text>
              </div>
            )}
          </div>
        )}
        
        {/* Image Content */}
        {image_content?.image_url && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <Text weight="semibold" size={200}>Generated Image</Text>
              <Button
                appearance="subtle"
                icon={<ArrowDownload24Regular />}
                size="small"
                onClick={handleDownloadImage}
              >
                Download
              </Button>
            </div>
            
            <img
              src={image_content.image_url}
              alt={image_content.alt_text || 'Generated marketing image'}
              style={{
                width: '100%',
                maxWidth: '400px',
                borderRadius: '8px',
                marginBottom: '8px'
              }}
            />
            
            {image_content.alt_text && (
              <Text size={100} style={{ color: tokens.colorNeutralForeground3 }}>
                Alt text: {image_content.alt_text}
              </Text>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}

function ViolationCard({ violation }: { violation: ComplianceViolation }) {
  const getSeverityStyles = () => {
    switch (violation.severity) {
      case 'error':
        return {
          icon: <ErrorCircle24Regular style={{ color: '#d13438', fontSize: '16px' }} />,
          bg: '#fde7e9',
        };
      case 'warning':
        return {
          icon: <Warning24Regular style={{ color: '#ffb900', fontSize: '16px' }} />,
          bg: '#fff4ce',
        };
      case 'info':
        return {
          icon: <Info24Regular style={{ color: '#0078d4', fontSize: '16px' }} />,
          bg: '#deecf9',
        };
    }
  };

  const { icon, bg } = getSeverityStyles();

  return (
    <div style={{ 
      padding: '8px', 
      backgroundColor: bg, 
      borderRadius: '4px',
      marginBottom: '4px',
      display: 'flex',
      alignItems: 'flex-start',
      gap: '8px'
    }}>
      {icon}
      <div>
        <Text weight="semibold" size={200} block>
          {violation.message}
        </Text>
        <Text size={100} style={{ color: tokens.colorNeutralForeground3 }}>
          {violation.suggestion}
        </Text>
      </div>
    </div>
  );
}
