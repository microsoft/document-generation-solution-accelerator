import {
  Button,
  Text,
  tokens,
} from '@fluentui/react-components';
import {
  Sparkle20Regular,
} from '@fluentui/react-icons';
import type { Product } from '../types';

interface ProductReviewProps {
  products: Product[];
  onConfirm: () => void;
  onStartOver: () => void;
  isAwaitingResponse?: boolean;
  availableProducts?: Product[];
  onProductSelect?: (product: Product) => void;
}

export function ProductReview({
  products,
  onConfirm,
  onStartOver: _onStartOver,
  isAwaitingResponse = false,
  availableProducts = [],
  onProductSelect,
}: ProductReviewProps) {
  const displayProducts = availableProducts.length > 0 ? availableProducts : products;
  const selectedProductIds = new Set(products.map(p => p.sku || p.product_name));

  const getProductColor = (product: Product): string => {
    if (product.hex_value) return product.hex_value;
    const hash = product.product_name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const hue = hash % 360;
    return `hsl(${hue}, 30%, 85%)`;
  };

  const isProductSelected = (product: Product): boolean => {
    return selectedProductIds.has(product.sku || product.product_name);
  };

  const handleProductClick = (product: Product) => {
    if (onProductSelect) {
      onProductSelect(product);
    }
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
      <div style={{ marginBottom: '16px' }}>
        <Text size={300} style={{ color: tokens.colorNeutralForeground1 }}>
          Here is the list of available paints:
        </Text>
      </div>

      {displayProducts.length > 0 ? (
        <div className="product-grid" style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '16px',
          marginBottom: '16px',
          maxHeight: '500px',
          overflowY: 'auto',
        }}>
          {displayProducts.map((product, index) => (
            <ProductCardGrid
              key={product.sku || index}
              product={product}
              color={getProductColor(product)}
              isSelected={isProductSelected(product)}
              onClick={() => handleProductClick(product)}
            />
          ))}
        </div>
      ) : (
        <div style={{
          padding: '24px',
          textAlign: 'center',
          backgroundColor: tokens.colorNeutralBackground2,
          borderRadius: '8px',
          marginBottom: '16px',
        }}>
          <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
            No products available.
          </Text>
        </div>
      )}

      {displayProducts.length > 0 && (
        <div style={{ 
          display: 'flex',
          gap: '8px',
          flexWrap: 'wrap',
          marginTop: '16px',
        }}>
          <Button
            appearance="primary"
            icon={<Sparkle20Regular />}
            onClick={onConfirm}
            disabled={isAwaitingResponse}
            size="small"
          >
            Generate Content
          </Button>
        </div>
      )}

      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: '12px',
        paddingTop: '8px',
      }}>
        <Text size={100} style={{ color: tokens.colorNeutralForeground4 }}>
          AI-generated content may be incorrect
        </Text>
      </div>
    </div>
  );
}

interface ProductCardGridProps {
  product: Product;
  color: string;
  isSelected: boolean;
  onClick: () => void;
}

function ProductCardGrid({ product, color, isSelected, onClick }: ProductCardGridProps) {
  return (
    <div 
      className={`product-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
      style={{
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        gap: '16px',
        padding: '16px',
        borderRadius: '8px',
        border: isSelected ? `2px solid ${tokens.colorBrandStroke1}` : `1px dashed ${tokens.colorNeutralStroke2}`,
        backgroundColor: isSelected ? tokens.colorBrandBackground2 : tokens.colorNeutralBackground1,
        cursor: 'pointer',
        transition: 'all 0.15s ease-in-out',
      }}
    >
      <div 
        className="product-color-swatch"
        style={{
          width: '80px',
          height: '80px',
          borderRadius: '8px',
          backgroundColor: color,
          border: `1px solid ${tokens.colorNeutralStroke2}`,
          flexShrink: 0,
        }}
      />
      
      <div className="product-info" style={{ flex: 1, minWidth: 0 }}>
        <Text 
          weight="semibold" 
          size={400}
          style={{ 
            display: 'block',
            color: tokens.colorNeutralForeground1,
            marginBottom: '4px',
          }}
        >
          {product.product_name}
        </Text>
        <Text 
          size={200}
          style={{ 
            display: 'block',
            color: tokens.colorNeutralForeground3,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            marginBottom: '4px',
          }}
        >
          {product.tags || product.description || 'soft white, airy, minimal, fresh'}
        </Text>
        <Text 
          weight="semibold" 
          size={300}
          style={{ 
            display: 'block',
            color: tokens.colorNeutralForeground1,
          }}
        >
          ${product.price?.toFixed(2) || '59.95'} USD
        </Text>
      </div>
    </div>
  );
}
