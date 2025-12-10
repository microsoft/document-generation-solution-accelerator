import { useState, useEffect } from 'react';
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

// Custom hook for responsive breakpoints
function useWindowSize() {
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 1200);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowWidth;
}

export function InlineContentPreview({ content, onRegenerate, isLoading, selectedProduct }: InlineContentPreviewProps) {
  const { text_content, image_content, violations, requires_modification } = content;
  const [copied, setCopied] = useState(false);
  const windowWidth = useWindowSize();
  
  // Responsive breakpoints
  const isSmall = windowWidth < 768;
  const isMedium = windowWidth < 1024;

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

  const handleDownloadImage = async () => {
    if (!image_content?.image_url) return;

    try {
      // Create canvas to composite image with text overlay
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      // Load the image
      const img = new Image();
      img.crossOrigin = 'anonymous'; // Enable CORS for blob storage images
      
      img.onload = () => {
        // Set canvas size to match image
        canvas.width = img.width;
        canvas.height = img.height;

        // Draw the image
        ctx.drawImage(img, 0, 0);

        // Add text overlay if headline exists
        if (text_content?.headline) {
          const padding = Math.max(16, img.width * 0.03);
          const maxTextWidth = img.width - (padding * 2);

          // Draw headline text
          const headlineText = selectedProduct?.product_name || text_content.headline;
          const headlineFontSize = Math.max(20, Math.min(48, img.width * 0.05));
          ctx.font = `600 ${headlineFontSize}px Georgia, serif`;
          
          // Text shadow effect
          ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
          ctx.fillText(headlineText, padding + 2, padding + headlineFontSize + 2, maxTextWidth);
          
          // Main text
          ctx.fillStyle = 'white';
          ctx.fillText(headlineText, padding, padding + headlineFontSize, maxTextWidth);

          // Draw subtitle/CTA text
          if (text_content.cta_text) {
            const subtitleFontSize = Math.max(13, Math.min(24, img.width * 0.025));
            ctx.font = `400 ${subtitleFontSize}px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`;
            
            // Text shadow
            ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
            ctx.fillText(text_content.cta_text, padding + 2, padding + headlineFontSize + subtitleFontSize + 10, maxTextWidth);
            
            // Main text
            ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
            ctx.fillText(text_content.cta_text, padding, padding + headlineFontSize + subtitleFontSize + 8, maxTextWidth);
          }
        }

        // Convert canvas to blob and download
        canvas.toBlob((blob) => {
          if (blob) {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'generated-image-with-text.png';
            link.click();
            URL.revokeObjectURL(url);
          }
        }, 'image/png');
      };

      img.onerror = () => {
        // Fallback: download original image if canvas approach fails
        if (image_content?.image_url) {
          const link = document.createElement('a');
          link.href = image_content.image_url;
          link.download = 'generated-image.png';
          link.click();
        }
      };

      img.src = image_content.image_url;
    } catch (error) {
      // Fallback: download original image
      if (image_content?.image_url) {
        const link = document.createElement('a');
        link.href = image_content.image_url;
        link.download = 'generated-image.png';
        link.click();
      }
    }
  };

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
        padding: 'clamp(12px, 2.5vw, 20px)',
        minWidth: 0, /* Allow card to shrink */
      }}>
        {/* Header */}
        <div style={{ 
          display: 'flex', 
          flexDirection: isSmall ? 'column' : 'row',
          justifyContent: 'space-between', 
          alignItems: isSmall ? 'flex-start' : 'flex-start', 
          marginBottom: 'clamp(12px, 2vw, 16px)',
          gap: isSmall ? '12px' : '8px',
        }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 'clamp(8px, 1.5vw, 12px)',
            flexWrap: 'wrap',
          }}>
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
            {isSmall ? '' : 'Regenerate'}
          </Button>
        </div>
        
        {/* Violations */}
        {violations.length > 0 && (
          <div style={{ marginBottom: 'clamp(12px, 2vw, 16px)' }}>
            {violations.map((violation, index) => (
              <ViolationCard key={index} violation={violation} />
            ))}
          </div>
        )}
        
        {/* Product number header */}
        {selectedProduct && (
          <Text 
            weight="bold" 
            size={500} 
            block 
            style={{ 
              marginBottom: 'clamp(12px, 2vw, 16px)',
              fontSize: 'clamp(16px, 2.5vw, 20px)',
            }}
          >
            1. {selectedProduct.product_name}
          </Text>
        )}
        
        {/* Main Content Grid: Product Card + Images */}
        <div style={{ 
          display: 'grid',
          gridTemplateColumns: isSmall 
            ? '1fr' 
            : isMedium 
              ? (selectedProduct ? '1fr 1fr' : '1fr 1fr')
              : (selectedProduct ? 'minmax(150px, 200px) 1fr 1fr' : '1fr 1fr'),
          gap: 'clamp(12px, 2vw, 16px)',
          marginBottom: 'clamp(16px, 2.5vw, 20px)',
        }}>
          {/* Product Card */}
          {selectedProduct && (
            <div style={{ 
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
              gridColumn: isSmall ? '1' : 'auto',
            }}>
              <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
                {selectedProduct.product_name}
              </Text>
              
              {/* Color Swatch / Product Image */}
              <div style={{
                width: '100%',
                aspectRatio: '1.5',
                maxHeight: isSmall ? '120px' : '150px',
                backgroundColor: '#EEEFEA',
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
              
              <Text weight="semibold" size={300} style={{ fontSize: 'clamp(13px, 1.8vw, 15px)' }}>
                {selectedProduct.product_name}
              </Text>
              <Text size={200} style={{ color: tokens.colorNeutralForeground3, fontSize: 'clamp(11px, 1.5vw, 13px)' }}>
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
              minHeight: isSmall ? '200px' : 'auto',
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
                  top: 'clamp(8px, 2vw, 16px)',
                  left: 'clamp(8px, 2vw, 16px)',
                  right: 'clamp(8px, 2vw, 16px)',
                  color: 'white',
                  textShadow: '0 2px 4px rgba(0,0,0,0.3)',
                }}>
                  <Text 
                    size={500} 
                    weight="semibold" 
                    style={{ 
                      color: 'white', 
                      display: 'block',
                      fontFamily: 'Georgia, serif',
                      fontSize: 'clamp(14px, 2.5vw, 20px)',
                    }}
                  >
                    {selectedProduct?.product_name || text_content.headline}
                  </Text>
                  <Text size={200} style={{ color: 'rgba(255,255,255,0.9)', fontSize: 'clamp(11px, 1.5vw, 13px)' }}>
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
          {!isSmall && (
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
          )}
        </div>
        
        <Divider style={{ margin: 'clamp(12px, 2vw, 16px) 0' }} />
        
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
              {copied ? 'Copied!' : (isSmall ? '' : 'Copy')}
            </Button>
            
            {/* Headline with sparkles */}
            {text_content.headline && (
              <Text 
                size={400} 
                weight="semibold" 
                block 
                style={{ 
                  marginBottom: 'clamp(8px, 1.5vw, 12px)', 
                  paddingRight: 'clamp(60px, 10vw, 80px)',
                  fontSize: 'clamp(14px, 2vw, 18px)',
                }}
              >
                ✨ {text_content.headline} ✨
              </Text>
            )}
            
            {/* Body text */}
            {text_content.body && (
              <Text 
                size={300} 
                block 
                style={{ 
                  marginBottom: 'clamp(12px, 2vw, 16px)', 
                  lineHeight: '1.6',
                  fontSize: 'clamp(13px, 1.8vw, 15px)',
                }}
              >
                {text_content.body}
              </Text>
            )}
            
            {/* Hashtags */}
            {text_content.tagline && (
              <Text 
                size={200} 
                style={{ 
                  color: tokens.colorBrandForeground1, 
                  lineHeight: '1.8',
                  fontSize: 'clamp(11px, 1.5vw, 13px)',
                }}
              >
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
