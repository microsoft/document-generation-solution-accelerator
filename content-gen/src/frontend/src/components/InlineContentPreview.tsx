import { useState, useEffect } from 'react';
import {
  Button,
  Text,
  Badge,
  Divider,
  tokens,
  Tooltip,
} from '@fluentui/react-components';
import {
  ArrowSync20Regular,
  CheckmarkCircle20Regular,
  Warning20Regular,
  Info20Regular,
  ErrorCircle20Regular,
  Copy20Regular,
  ArrowDownload20Regular,
  ShieldError20Regular,
} from '@fluentui/react-icons';
import type { GeneratedContent, ComplianceViolation, Product } from '../types';

interface InlineContentPreviewProps {
  content: GeneratedContent;
  onRegenerate: () => void;
  isLoading?: boolean;
  selectedProduct?: Product;
  imageGenerationEnabled?: boolean;
  onActionChipClick?: (action: string) => void;
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

export function InlineContentPreview({ 
  content, 
  onRegenerate, 
  isLoading, 
  selectedProduct, 
  imageGenerationEnabled = true,
  onActionChipClick,
}: InlineContentPreviewProps) {
  const { text_content, image_content, violations, requires_modification, error, image_error, text_error } = content;
  const [copied, setCopied] = useState(false);
  const windowWidth = useWindowSize();
  
  const isSmall = windowWidth < 768;

  // Helper to detect content filter errors
  const isContentFilterError = (errorMessage?: string): boolean => {
    if (!errorMessage) return false;
    const filterPatterns = [
      'content_filter', 'ContentFilter', 'content management policy',
      'ResponsibleAI', 'responsible_ai_policy', 'content filtering',
      'filtered', 'safety system', 'self_harm', 'sexual', 'violence', 'hate',
    ];
    return filterPatterns.some(pattern => 
      errorMessage.toLowerCase().includes(pattern.toLowerCase())
    );
  };

  const getErrorMessage = (errorMessage?: string): { title: string; description: string } => {
    if (isContentFilterError(errorMessage)) {
      return {
        title: 'Content Filtered',
        description: 'Your request was blocked by content safety filters. Please try modifying your creative brief.',
      };
    }
    return {
      title: 'Generation Failed',
      description: errorMessage || 'An error occurred. Please try again.',
    };
  };

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
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const img = new Image();
      img.crossOrigin = 'anonymous';
      
      img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);

        if (text_content?.headline) {
          const padding = Math.max(16, img.width * 0.03);
          const maxTextWidth = img.width - (padding * 2);
          const headlineText = selectedProduct?.product_name || text_content.headline;
          const headlineFontSize = Math.max(20, Math.min(48, img.width * 0.05));
          
          ctx.font = `600 ${headlineFontSize}px Georgia, serif`;
          ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
          ctx.fillText(headlineText, padding + 2, padding + headlineFontSize + 2, maxTextWidth);
          ctx.fillStyle = 'white';
          ctx.fillText(headlineText, padding, padding + headlineFontSize, maxTextWidth);

          if (text_content.cta_text) {
            const subtitleFontSize = Math.max(13, Math.min(24, img.width * 0.025));
            ctx.font = `400 ${subtitleFontSize}px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`;
            ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
            ctx.fillText(text_content.cta_text, padding + 2, padding + headlineFontSize + subtitleFontSize + 10, maxTextWidth);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
            ctx.fillText(text_content.cta_text, padding, padding + headlineFontSize + subtitleFontSize + 8, maxTextWidth);
          }
        }

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
        if (image_content?.image_url) {
          const link = document.createElement('a');
          link.href = image_content.image_url;
          link.download = 'generated-image.png';
          link.click();
        }
      };

      img.src = image_content.image_url;
    } catch {
      if (image_content?.image_url) {
        const link = document.createElement('a');
        link.href = image_content.image_url;
        link.download = 'generated-image.png';
        link.click();
      }
    }
  };

  // Get product display name
  const getProductDisplayName = () => {
    if (selectedProduct) {
      return selectedProduct.product_name;
    }
    return text_content?.headline || 'Your Content';
  };

  return (
    <div className="message assistant" style={{ 
      width: '100%',
      alignSelf: 'flex-start',
      backgroundColor: tokens.colorNeutralBackground3,
      padding: '12px 16px',
      borderRadius: '8px',
      margin: '16px 0 0 0',
    }}>
      {/* Selection confirmation */}
      {selectedProduct && (
        <Text size={200} style={{ 
          color: tokens.colorNeutralForeground3, 
          display: 'block',
          marginBottom: '8px',
        }}>
          You selected "{selectedProduct.product_name}". Here's what I've created – let me know if you need anything changed.
        </Text>
      )}

      {/* Sparkle Headline - Figma style */}
      {text_content?.headline && (
        <Text 
          weight="semibold" 
          size={400}
          style={{ 
            display: 'block',
            marginBottom: '16px',
            color: tokens.colorNeutralForeground1,
            fontSize: '18px',
          }}
        >
          ✨ Discover the serene elegance of {getProductDisplayName()}.
        </Text>
      )}

      {/* Body Copy */}
      {text_content?.body && (
        <Text 
          size={300}
          style={{ 
            display: 'block',
            marginBottom: '16px',
            lineHeight: '1.6',
            color: tokens.colorNeutralForeground2,
          }}
        >
          {text_content.body}
        </Text>
      )}

      {/* Hashtags */}
      {text_content?.tagline && (
        <Text 
          size={200}
          style={{ 
            display: 'block',
            marginBottom: '16px',
            lineHeight: '1.8',
            color: tokens.colorBrandForeground1,
          }}
        >
          {text_content.tagline}
        </Text>
      )}

      {/* Violations Banner */}
      {violations.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          {violations.map((violation, index) => (
            <ViolationCard key={index} violation={violation} />
          ))}
        </div>
      )}

      {/* Error Banner */}
      {(error || text_error) && !violations.some(v => v.message.toLowerCase().includes('filter')) && (
        <div style={{ 
          padding: '12px 16px', 
          backgroundColor: isContentFilterError(error || text_error) ? '#fef3f2' : '#fef9ee',
          border: `1px solid ${isContentFilterError(error || text_error) ? '#fecaca' : '#fde68a'}`,
          borderRadius: '8px',
          marginBottom: '16px',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '12px'
        }}>
          <ShieldError20Regular style={{ 
            color: isContentFilterError(error || text_error) ? '#dc2626' : '#d97706',
            flexShrink: 0,
            marginTop: '2px',
          }} />
          <div>
            <Text weight="semibold" size={300} block style={{ 
              color: isContentFilterError(error || text_error) ? '#b91c1c' : '#92400e',
              marginBottom: '4px',
            }}>
              {getErrorMessage(error || text_error).title}
            </Text>
            <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
              {getErrorMessage(error || text_error).description}
            </Text>
          </div>
        </div>
      )}

      {/* Image Preview - with product overlay */}
      {imageGenerationEnabled && image_content?.image_url && (
        <div style={{ 
          position: 'relative',
          borderRadius: '8px',
          overflow: 'hidden',
          marginBottom: '16px',
          maxWidth: isSmall ? '100%' : '500px',
        }}>
          <img
            src={image_content.image_url}
            alt={image_content.alt_text || 'Generated marketing image'}
            style={{
              width: '100%',
              height: 'auto',
              display: 'block',
            }}
          />
          
          {/* Text overlay on image */}
          <div style={{
            position: 'absolute',
            top: '16px',
            left: '16px',
            right: '16px',
            color: 'white',
            textShadow: '0 2px 4px rgba(0,0,0,0.4)',
          }}>
            <Text 
              size={500} 
              weight="semibold" 
              style={{ 
                color: 'white', 
                display: 'block',
                fontFamily: 'Georgia, serif',
                fontSize: isSmall ? '16px' : '24px',
              }}
            >
              {selectedProduct?.product_name || text_content?.headline || 'Snow Veil'}
            </Text>
            <Text size={200} style={{ 
              color: 'rgba(255,255,255,0.9)',
              fontStyle: 'italic',
            }}>
              A Crisp White for Modern Interiors
            </Text>
          </div>
          
          {/* Download button */}
          <Tooltip content="Download image" relationship="label">
            <Button
              appearance="subtle"
              icon={<ArrowDownload20Regular />}
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
          </Tooltip>
        </div>
      )}

      {/* Image Error State */}
      {imageGenerationEnabled && !image_content?.image_url && (image_error || error) && (
        <div style={{ 
          borderRadius: '8px',
          padding: '32px',
          backgroundColor: isContentFilterError(image_error || error) ? '#fef3f2' : '#fef9ee',
          border: `1px solid ${isContentFilterError(image_error || error) ? '#fecaca' : '#fde68a'}`,
          marginBottom: '16px',
          textAlign: 'center',
        }}>
          <ShieldError20Regular style={{ 
            fontSize: '32px', 
            color: isContentFilterError(image_error || error) ? '#dc2626' : '#d97706',
            marginBottom: '8px',
          }} />
          <Text weight="semibold" size={300} block style={{ 
            color: isContentFilterError(image_error || error) ? '#b91c1c' : '#92400e',
          }}>
            {getErrorMessage(image_error || error).title}
          </Text>
          <Text size={200} style={{ color: tokens.colorNeutralForeground3, marginTop: '4px' }}>
            Click Regenerate to try again
          </Text>
        </div>
      )}

      {/* Action Chip - for quick follow-up requests */}
      {image_content?.image_url && (
        <div 
          className="action-chip"
          onClick={() => onActionChipClick?.('Create an other image with same paint color, but a modern kitchen area, with no text on it')}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '10px 16px',
            borderRadius: '20px',
            backgroundColor: tokens.colorBrandBackground2,
            color: tokens.colorBrandForeground1,
            fontSize: '13px',
            cursor: 'pointer',
            border: `1px solid ${tokens.colorBrandStroke1}`,
            transition: 'all 0.15s ease-in-out',
            marginBottom: '16px',
          }}
        >
          Create an other image with same paint color, but a modern kitchen area, with no text on it
        </div>
      )}

      <Divider style={{ margin: '16px 0' }} />

      {/* Footer with actions */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {/* Approval Status Badge */}
          {requires_modification ? (
            <Badge appearance="filled" color="danger" size="small" icon={<ErrorCircle20Regular />}>
              Requires Modification
            </Badge>
          ) : violations.length > 0 ? (
            <Badge appearance="filled" color="warning" size="small" icon={<Warning20Regular />}>
              Review Recommended
            </Badge>
          ) : (
            <Badge appearance="filled" color="success" size="small" icon={<CheckmarkCircle20Regular />}>
              Approved
            </Badge>
          )}
        </div>

        <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
          <Tooltip content={copied ? 'Copied!' : 'Copy text'} relationship="label">
            <Button
              appearance="subtle"
              icon={<Copy20Regular />}
              size="small"
              onClick={handleCopyText}
              style={{ minWidth: '32px', color: tokens.colorNeutralForeground3 }}
            />
          </Tooltip>
          <Tooltip content="Regenerate" relationship="label">
            <Button
              appearance="subtle"
              icon={<ArrowSync20Regular />}
              size="small"
              onClick={onRegenerate}
              disabled={isLoading}
              style={{ minWidth: '32px', color: tokens.colorNeutralForeground3 }}
            />
          </Tooltip>
        </div>
      </div>

      {/* AI disclaimer */}
      <Text size={100} style={{ 
        color: tokens.colorNeutralForeground4,
        display: 'block',
        marginTop: '8px',
      }}>
        AI-generated content may be incorrect
      </Text>
    </div>
  );
}

function ViolationCard({ violation }: { violation: ComplianceViolation }) {
  const getSeverityStyles = () => {
    switch (violation.severity) {
      case 'error':
        return {
          icon: <ErrorCircle20Regular style={{ color: '#d13438' }} />,
          bg: '#fde7e9',
        };
      case 'warning':
        return {
          icon: <Warning20Regular style={{ color: '#ffb900' }} />,
          bg: '#fff4ce',
        };
      case 'info':
        return {
          icon: <Info20Regular style={{ color: '#0078d4' }} />,
          bg: '#deecf9',
        };
    }
  };

  const { icon, bg } = getSeverityStyles();

  return (
    <div style={{ 
      padding: '8px 12px', 
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
