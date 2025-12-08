import {
  Card,
  Button,
  Text,
  Badge,
  tokens,
} from '@fluentui/react-components';
import {
  Bot24Regular,
  ArrowReset24Regular,
  Box24Regular,
  Sparkle24Regular,
} from '@fluentui/react-icons';
import type { Product } from '../types';

interface ProductReviewProps {
  products: Product[];
  onConfirm: () => void;
  onStartOver: () => void;
  isAwaitingResponse?: boolean;
}

export function ProductReview({
  products,
  onConfirm,
  onStartOver,
  isAwaitingResponse = false,
}: ProductReviewProps) {
  const hasProducts = products.length > 0;

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
        minWidth: 0,
      }}>
        <Badge appearance="outline" size="small" style={{ marginBottom: '8px' }}>
          ProductAgent
        </Badge>
        
        <Text 
          weight="semibold" 
          size={300} 
          block 
          style={{ 
            marginBottom: '8px',
            fontSize: 'clamp(13px, 1.8vw, 15px)',
          }}
        >
          {hasProducts 
            ? `Selected Products (${products.length})`
            : 'No Products Selected Yet'
          }
        </Text>
        
        {/* Selected Products Display */}
        {hasProducts ? (
          <div style={{ 
            display: 'flex',
            flexDirection: 'column',
            gap: 'clamp(6px, 1vw, 8px)',
            marginBottom: 'clamp(12px, 2vw, 16px)',
          }}>
            {products.map((product, index) => (
              <div
                key={product.sku || index}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'clamp(8px, 1.5vw, 12px)',
                  padding: 'clamp(8px, 1.5vw, 12px)',
                  backgroundColor: tokens.colorBrandBackground2,
                  borderRadius: '8px',
                  border: `1px solid ${tokens.colorBrandStroke1}`,
                }}
              >
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.product_name}
                    style={{
                      width: 'clamp(40px, 6vw, 50px)',
                      height: 'clamp(40px, 6vw, 50px)',
                      objectFit: 'cover',
                      borderRadius: '6px',
                      flexShrink: 0,
                    }}
                  />
                ) : (
                  <div style={{
                    width: 'clamp(40px, 6vw, 50px)',
                    height: 'clamp(40px, 6vw, 50px)',
                    borderRadius: '6px',
                    backgroundColor: tokens.colorNeutralBackground3,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}>
                    <Box24Regular />
                  </div>
                )}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <Text 
                    weight="semibold" 
                    size={200} 
                    block
                    style={{
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      fontSize: 'clamp(12px, 1.6vw, 14px)',
                    }}
                  >
                    {product.product_name}
                  </Text>
                  <Text 
                    size={100}
                    style={{ 
                      color: tokens.colorNeutralForeground3,
                      fontSize: 'clamp(10px, 1.2vw, 12px)',
                    }}
                  >
                    {product.category || product.tags} {product.price ? `• $${product.price.toFixed(2)}` : ''}
                  </Text>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{
            padding: 'clamp(16px, 3vw, 24px)',
            textAlign: 'center',
            backgroundColor: tokens.colorNeutralBackground2,
            borderRadius: '8px',
            marginBottom: 'clamp(12px, 2vw, 16px)',
          }}>
            <Box24Regular style={{ fontSize: '32px', color: tokens.colorNeutralForeground3, marginBottom: '8px' }} />
            <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
              Tell me which products you'd like to feature
            </Text>
          </div>
        )}
        
        {/* Conversational Prompts */}
        <div style={{
          padding: 'clamp(8px, 1.5vw, 12px)',
          backgroundColor: tokens.colorNeutralBackground2,
          borderRadius: '8px',
          marginBottom: 'clamp(12px, 2vw, 16px)',
        }}>
          <Text 
            size={200} 
            style={{ 
              color: tokens.colorNeutralForeground2,
              lineHeight: '1.5',
              fontSize: 'clamp(11px, 1.4vw, 13px)',
            }}
          >
            {hasProducts ? (
              <>
                <strong>Looking good!</strong> You can continue to refine your selection:
                <ul style={{ margin: '8px 0 0 0', paddingLeft: '16px' }}>
                  <li>"Add the Arctic Frost paint to the selection"</li>
                  <li>"Remove the second product"</li>
                  <li>"Show me more blue paints"</li>
                  <li>"Replace with products for outdoor use"</li>
                </ul>
                <div style={{ marginTop: '8px' }}>
                  When you're satisfied, click <strong>Generate Content</strong> to create your marketing materials.
                </div>
              </>
            ) : (
              <>
                <strong>Let's find the right products!</strong> Try saying:
                <ul style={{ margin: '8px 0 0 0', paddingLeft: '16px' }}>
                  <li>"Show me exterior paints"</li>
                  <li>"I need paint for a kitchen renovation"</li>
                  <li>"Find products with blue tones"</li>
                  <li>"Select SnowVeil and Ocean Mist"</li>
                </ul>
              </>
            )}
          </Text>
        </div>
        
        {/* Action Buttons */}
        <div style={{ 
          display: 'flex',
          gap: 'clamp(6px, 1vw, 8px)',
          flexWrap: 'wrap',
        }}>
          <Button
            appearance="primary"
            icon={<Sparkle24Regular />}
            onClick={onConfirm}
            disabled={isAwaitingResponse || !hasProducts}
            size="small"
          >
            Generate Content
          </Button>
          <Button
            appearance="subtle"
            icon={<ArrowReset24Regular />}
            onClick={onStartOver}
            disabled={isAwaitingResponse}
            size="small"
          >
            Start Over
          </Button>
        </div>
      </Card>
    </div>
  );
}
