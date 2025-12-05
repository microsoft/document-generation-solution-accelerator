import { useState } from 'react';
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
import type { GeneratedContent, ComplianceViolation, Product } from '../types';

interface InlineContentPreviewProps {
  content: GeneratedContent;
  onRegenerate: () => void;
  isLoading?: boolean;
  selectedProduct?: Product;
}

export function InlineContentPreview({ content, onRegenerate, isLoading, selectedProduct }: InlineContentPreviewProps) {
  const { text_content, image_content, violations, requires_modification } = content;
  const [copied, setCopied] = useState(false);

  const handleCopyText = () => {
    const textToCopy = [
      text_content?.headline && `✨ ${text_content.headline} ✨`,
      text_content?.body,
      text_content?.tagline,
    ].filter(Boolean).join('\n\n');
    
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
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
        backgroundColor: tokens.colorNeutralBackground1,
        padding: '20px',
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Badge appearance="outline" size="small">
              ContentAgent
            </Badge>
            {/* Approval Status */}
            {requires_modification ? (
              <Badge appearance="filled" color="danger" icon={<ErrorCircle24Regular />}>
                Requires Modification
              </Badge>
            ) : violations.length > 0 ? (
              <Badge appearance="filled" color="warning" icon={<Warning24Regular />}>
                Review Recommended
              </Badge>
            ) : (
              <Badge appearance="filled" color="success" icon={<CheckmarkCircle24Regular />}>
                Approved
              </Badge>
            )}
          </div>
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
        
        {/* Violations */}
        {violations.length > 0 && (
          <div style={{ marginBottom: '16px' }}>
            {violations.map((violation, index) => (
              <ViolationCard key={index} violation={violation} />
            ))}
          </div>
        )}
        
        {/* Product number header */}
        {selectedProduct && (
          <Text weight="bold" size={500} block style={{ marginBottom: '16px' }}>
            1. {selectedProduct.product_name}
          </Text>
        )}
        
        {/* Main Content Grid: Product Card + Images */}
        <div style={{ 
          display: 'grid',
          gridTemplateColumns: selectedProduct ? '200px 1fr 1fr' : '1fr 1fr',
          gap: '16px',
          marginBottom: '20px',
        }}>
          {/* Product Card */}
          {selectedProduct && (
            <div style={{ 
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
            }}>
              <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
                {selectedProduct.product_name}
              </Text>
              
              {/* Color Swatch / Product Image */}
              <div style={{
                width: '100%',
                aspectRatio: '1.5',
                backgroundColor: '#EEEFEA', // Default soft white
                borderRadius: '4px',
                border: `1px solid ${tokens.colorNeutralStroke1}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                overflow: 'hidden',
              }}>
                {selectedProduct.image_url ? (
                  <img 
                    src={selectedProduct.image_url} 
                    alt={selectedProduct.product_name}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                ) : null}
              </div>
              
              <Text weight="semibold" size={300}>
                {selectedProduct.product_name}
              </Text>
              <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
                {selectedProduct.tags || selectedProduct.description}
              </Text>
              
              <Text size={200} weight="semibold" style={{ color: tokens.colorNeutralForeground1 }}>
                ${selectedProduct.price?.toFixed(2) || '59.95'} USD
              </Text>
            </div>
          )}
          
          {/* Generated Image 1 - with overlay text */}
          {image_content?.image_url && (
            <div style={{ 
              position: 'relative',
              borderRadius: '8px',
              overflow: 'hidden',
              aspectRatio: '1',
            }}>
              <img
                src={image_content.image_url}
                alt={image_content.alt_text || 'Generated marketing image'}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                }}
              />
              {/* Text overlay */}
              {text_content?.headline && (
                <div style={{
                  position: 'absolute',
                  top: '16px',
                  left: '16px',
                  right: '16px',
                  color: 'white',
                  textShadow: '0 2px 4px rgba(0,0,0,0.3)',
                }}>
                  <Text size={500} weight="semibold" style={{ 
                    color: 'white', 
                    display: 'block',
                    fontFamily: 'Georgia, serif',
                  }}>
                    {selectedProduct?.product_name || text_content.headline}
                  </Text>
                  <Text size={200} style={{ color: 'rgba(255,255,255,0.9)' }}>
                    {text_content.cta_text || 'A Modern Choice'}
                  </Text>
                </div>
              )}
              {/* Download button */}
              <Button
                appearance="subtle"
                icon={<ArrowDownload24Regular />}
                size="small"
                onClick={handleDownloadImage}
                style={{
                  position: 'absolute',
                  bottom: '8px',
                  right: '8px',
                  backgroundColor: 'rgba(255,255,255,0.9)',
                  minWidth: '32px',
                }}
              />
            </div>
          )}
          
          {/* Generated Image 2 / Additional Image placeholder */}
          <div style={{ 
            borderRadius: '8px',
            overflow: 'hidden',
            aspectRatio: '1',
            backgroundColor: tokens.colorNeutralBackground3,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            {image_content?.image_url ? (
              <img
                src={image_content.image_url}
                alt="Secondary marketing image"
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  filter: 'brightness(1.05)',
                }}
              />
            ) : (
              <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
                Additional image
              </Text>
            )}
          </div>
        </div>
        
        <Divider style={{ margin: '16px 0' }} />
        
        {/* Marketing Copy Section */}
        {text_content && (
          <div style={{ position: 'relative' }}>
            {/* Copy button */}
            <Button
              appearance="subtle"
              icon={<Copy24Regular />}
              size="small"
              onClick={handleCopyText}
              style={{
                position: 'absolute',
                top: '0',
                right: '0',
              }}
            >
              {copied ? 'Copied!' : 'Copy'}
            </Button>
            
            {/* Headline with sparkles */}
            {text_content.headline && (
              <Text size={400} weight="semibold" block style={{ marginBottom: '12px', paddingRight: '80px' }}>
                ✨ {text_content.headline} ✨
              </Text>
            )}
            
            {/* Body text */}
            {text_content.body && (
              <Text size={300} block style={{ marginBottom: '16px', lineHeight: '1.6' }}>
                {text_content.body}
              </Text>
            )}
            
            {/* Hashtags */}
            {text_content.tagline && (
              <Text size={200} style={{ color: tokens.colorBrandForeground1, lineHeight: '1.8' }}>
                {text_content.tagline}
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
