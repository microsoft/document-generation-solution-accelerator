import {
  Card,
  CardHeader,
  Button,
  Text,
  Title3,
  Badge,
  Divider,
  tokens,
  Accordion,
  AccordionItem,
  AccordionHeader,
  AccordionPanel,
} from '@fluentui/react-components';
import {
  ArrowSync24Regular,
  CheckmarkCircle24Regular,
  Warning24Regular,
  Info24Regular,
  ErrorCircle24Regular,
  Copy24Regular,
  ArrowDownload24Regular,
} from '@fluentui/react-icons';
import type { GeneratedContent, ComplianceViolation } from '../types';

interface ContentPreviewProps {
  content: GeneratedContent;
  onRegenerate: () => void;
}

export function ContentPreview({ content, onRegenerate }: ContentPreviewProps) {
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
    <Card className="panel-card">
      <CardHeader
        header={<Title3>Generated Content</Title3>}
        action={
          <Button
            appearance="subtle"
            icon={<ArrowSync24Regular />}
            onClick={onRegenerate}
          >
            Regenerate
          </Button>
        }
      />
      
      {/* Approval Status */}
      <div style={{ marginBottom: '16px' }}>
        {requires_modification ? (
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            gap: '8px',
            padding: '12px',
            backgroundColor: 'rgba(209, 52, 56, 0.08)',
            borderRadius: '8px',
            border: '1px solid rgba(209, 52, 56, 0.3)'
          }}>
            <Badge
              appearance="filled"
              color="danger"
              icon={<ErrorCircle24Regular />}
            >
              Requires Modification
            </Badge>
            <Text size={200} style={{ color: tokens.colorNeutralForeground1 }}>
              <strong>Action needed:</strong> This content has compliance issues that must be addressed before use. 
              Review the issues below and click <strong>"Regenerate"</strong> to create new content, 
              or manually edit the text to resolve the flagged concerns.
            </Text>
          </div>
        ) : violations.length > 0 ? (
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            gap: '8px',
            padding: '12px',
            backgroundColor: 'rgba(255, 185, 0, 0.08)',
            borderRadius: '8px',
            border: '1px solid rgba(255, 185, 0, 0.3)'
          }}>
            <Badge
              appearance="filled"
              color="warning"
              icon={<Warning24Regular />}
            >
              Review Recommended
            </Badge>
            <Text size={200} style={{ color: tokens.colorNeutralForeground1 }}>
              <strong>Optional review:</strong> Minor suggestions were identified. You may proceed with this content, 
              but consider reviewing the guidelines below to improve quality.
            </Text>
          </div>
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
      
      <Divider style={{ margin: '16px 0' }} />
      
      {/* Text Content */}
      {text_content && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <Text weight="semibold" size={300}>Text Content</Text>
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
            <div style={{ marginBottom: '12px' }}>
              <Text size={100} style={{ color: tokens.colorNeutralForeground3 }}>Headline</Text>
              <Text size={400} weight="bold" block>{text_content.headline}</Text>
            </div>
          )}
          
          {text_content.body && (
            <div style={{ marginBottom: '12px' }}>
              <Text size={100} style={{ color: tokens.colorNeutralForeground3 }}>Body</Text>
              <Text size={200} block>{text_content.body}</Text>
            </div>
          )}
          
          {text_content.cta_text && (
            <div style={{ marginBottom: '12px' }}>
              <Text size={100} style={{ color: tokens.colorNeutralForeground3 }}>Call to Action</Text>
              <Text size={200} weight="semibold" block style={{ color: tokens.colorBrandForeground1 }}>
                {text_content.cta_text}
              </Text>
            </div>
          )}
          
          {text_content.tagline && (
            <div style={{ marginBottom: '12px' }}>
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
            <Text weight="semibold" size={300}>Generated Image</Text>
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

      {/* Collapsible Compliance Section */}
      {violations.length > 0 && (
        <Accordion 
          collapsible 
          style={{ 
            marginTop: '16px',
            borderTop: `1px solid ${tokens.colorNeutralStroke2}`,
            paddingTop: '8px',
          }}
        >
          <AccordionItem value="compliance">
            <AccordionHeader expandIconPosition="end">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {requires_modification ? (
                  <ErrorCircle24Regular style={{ color: '#d13438' }} />
                ) : violations.some(v => v.severity === 'error') ? (
                  <ErrorCircle24Regular style={{ color: '#d13438' }} />
                ) : violations.some(v => v.severity === 'warning') ? (
                  <Warning24Regular style={{ color: '#ffb900' }} />
                ) : (
                  <Info24Regular style={{ color: '#0078d4' }} />
                )}
                <Text weight="semibold" size={200}>
                  Compliance Guidelines ({violations.length} {violations.length === 1 ? 'issue' : 'issues'})
                </Text>
              </div>
            </AccordionHeader>
            <AccordionPanel>
              <div style={{ paddingTop: '8px' }}>
                {violations.map((violation, index) => (
                  <ViolationCard key={index} violation={violation} />
                ))}
              </div>
            </AccordionPanel>
          </AccordionItem>
        </Accordion>
      )}
    </Card>
  );
}

function ViolationCard({ violation }: { violation: ComplianceViolation }) {
  const getSeverityStyles = () => {
    switch (violation.severity) {
      case 'error':
        return {
          className: 'severity-error',
          icon: <ErrorCircle24Regular style={{ color: '#d13438' }} />,
        };
      case 'warning':
        return {
          className: 'severity-warning',
          icon: <Warning24Regular style={{ color: '#ffb900' }} />,
        };
      case 'info':
        return {
          className: 'severity-info',
          icon: <Info24Regular style={{ color: '#0078d4' }} />,
        };
    }
  };

  const { className, icon } = getSeverityStyles();

  return (
    <div className={`violation-card ${className}`}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
        {icon}
        <div>
          <Text weight="semibold" size={200} block>
            {violation.message}
          </Text>
          <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
            {violation.suggestion}
          </Text>
          {violation.field && (
            <Badge appearance="outline" size="small" style={{ marginTop: '4px' }}>
              {violation.field}
            </Badge>
          )}
        </div>
      </div>
    </div>
  );
}
