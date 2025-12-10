import {
  Card,
  Text,
  Badge,
  tokens,
} from '@fluentui/react-components';
import {
  Bot24Regular,
  Checkmark24Regular,
  Box24Regular,
} from '@fluentui/react-icons';
import type { Product } from '../types';

interface SelectedProductViewProps {
  products: Product[];
}

export function SelectedProductView({ products }: SelectedProductViewProps) {
  if (products.length === 0) return null;

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
        opacity: 0.9,
      }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '8px', 
          marginBottom: '8px' 
        }}>
          <Badge appearance="outline" size="small">
            ProductAgent
          </Badge>
          <Badge 
            appearance="filled" 
            size="small" 
            color="success"
            icon={<Checkmark24Regular />}
          >
            Product Selected
          </Badge>
        </div>
        
        {/* Products - Collapsed View */}
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '6px',
          maxHeight: 'clamp(120px, 20vh, 160px)',
          overflowY: 'auto',
          paddingRight: '8px',
        }}>
          {products.map((product, index) => (
            <div 
              key={product.sku || index} 
              style={{ 
                display: 'flex',
                alignItems: 'center',
                gap: 'clamp(8px, 1.5vw, 10px)',
                padding: 'clamp(6px, 1vw, 8px)', 
                backgroundColor: tokens.colorNeutralBackground2, 
                borderRadius: '4px',
              }}
            >
              {/* Product Image or Placeholder */}
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={product.product_name}
                  style={{
                    width: 'clamp(32px, 5vw, 40px)',
                    height: 'clamp(32px, 5vw, 40px)',
                    objectFit: 'cover',
                    borderRadius: '4px',
                    flexShrink: 0,
                  }}
                />
              ) : (
                <div style={{
                  width: 'clamp(32px, 5vw, 40px)',
                  height: 'clamp(32px, 5vw, 40px)',
                  borderRadius: '4px',
                  backgroundColor: tokens.colorNeutralBackground3,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}>
                  <Box24Regular style={{ fontSize: 'clamp(14px, 2vw, 18px)' }} />
                </div>
              )}
              
              {/* Product Info */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <Text 
                  weight="semibold" 
                  size={200}
                  style={{
                    display: 'block',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    fontSize: 'clamp(11px, 1.4vw, 13px)',
                  }}
                >
                  {product.product_name}
                </Text>
                <Text 
                  size={100}
                  style={{ 
                    color: tokens.colorNeutralForeground3,
                    fontSize: 'clamp(10px, 1.2vw, 11px)',
                  }}
                >
                  {product.category || product.tags}
                  {product.price ? ` • $${product.price.toFixed(2)}` : ''}
                  {product.sku ? ` • SKU: ${product.sku}` : ''}
                </Text>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
