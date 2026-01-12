import { useState } from 'react';
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

type ViewMode = 'list' | 'grid';

export function ProductReview({
  products,
  onConfirm,
  onStartOver: _onStartOver,
  isAwaitingResponse = false,
  availableProducts = [],
  onProductSelect,
}: ProductReviewProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const hasProducts = products.length > 0;
  
  // Use available products if provided, otherwise use selected products for display
  const displayProducts = availableProducts.length > 0 ? availableProducts : products;
  const selectedProductIds = new Set(products.map(p => p.sku || p.product_name));

  // Get color from product (use hex_value if available, otherwise a default based on name)
  const getProductColor = (product: Product): string => {
    if (product.hex_value) return product.hex_value;
    // Generate a color based on product name hash for demo purposes
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
      {/* Header with view toggle */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px',
      }}>
        <Text size={300} style={{ color: tokens.colorNeutralForeground1 }}>
          Here is the list of available paints{' '}
          <span className="view-toggle" style={{ fontSize: '13px' }}>
            (
            <span 
              onClick={() => setViewMode('list')}
              style={{
                color: tokens.colorBrandForeground1,
                cursor: 'pointer',
                fontWeight: viewMode === 'list' ? 600 : 400,
                textDecoration: 'none',
              }}
            >
              list style 1
            </span>
            ):
          </span>
        </Text>
      </div>

      {/* Products Display */}
      {displayProducts.length > 0 ? (
        viewMode === 'list' ? (
          // List View - Style 1
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            marginBottom: '16px',
            maxHeight: '400px',
            overflowY: 'auto',
          }}>
            {displayProducts.map((product, index) => (
              <ProductCardList
                key={product.sku || index}
                product={product}
                color={getProductColor(product)}
                isSelected={isProductSelected(product)}
                onClick={() => handleProductClick(product)}
                showSelectButton={!!onProductSelect}
              />
            ))}
          </div>
        ) : (
          // Grid View - Style 2
          <div className="product-grid" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: '12px',
            marginBottom: '16px',
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
        )
      ) : (
        // Empty state
        <div style={{
          padding: '24px',
          textAlign: 'center',
          backgroundColor: tokens.colorNeutralBackground2,
          borderRadius: '8px',
          marginBottom: '16px',
        }}>
          <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
            No products available. Ask me to show you the available paints.
          </Text>
        </div>
      )}

      {/* Second view toggle link */}
      <div style={{ marginBottom: '16px' }}>
        <Text size={300} style={{ color: tokens.colorNeutralForeground1 }}>
          Here is the list of available paints{' '}
          <span style={{ fontSize: '13px' }}>
            (
            <span 
              onClick={() => setViewMode('grid')}
              style={{
                color: tokens.colorBrandForeground1,
                cursor: 'pointer',
                fontWeight: viewMode === 'grid' ? 600 : 400,
                textDecoration: 'none',
              }}
            >
              list style 2
            </span>
            ):
          </span>
        </Text>
      </div>

      {/* Grid view preview */}
      {displayProducts.length > 0 && (
        <div className="product-grid" style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '12px',
          marginBottom: '16px',
        }}>
          {displayProducts.slice(0, 4).map((product, index) => (
            <ProductCardGrid
              key={`grid-${product.sku || index}`}
              product={product}
              color={getProductColor(product)}
              isSelected={isProductSelected(product)}
              onClick={() => handleProductClick(product)}
            />
          ))}
        </div>
      )}

      {/* Action Buttons */}
      {hasProducts && (
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
            disabled={isAwaitingResponse || !hasProducts}
            size="small"
          >
            Generate Content
          </Button>
        </div>
      )}

      {/* AI disclaimer footer */}
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

// Product Card - List View (Style 1)
interface ProductCardListProps {
  product: Product;
  color: string;
  isSelected: boolean;
  onClick: () => void;
  showSelectButton?: boolean;
}

function ProductCardList({ product, color, isSelected, onClick, showSelectButton = true }: ProductCardListProps) {
  return (
    <div 
      className={`product-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '12px 16px',
        borderRadius: '8px',
        border: `1px dashed ${tokens.colorNeutralStroke2}`,
        backgroundColor: tokens.colorNeutralBackground1,
        cursor: 'pointer',
        transition: 'all 0.15s ease-in-out',
      }}
    >
      {/* Color Swatch - Square with rounded corners */}
      <div 
        className="product-color-swatch"
        style={{
          width: '48px',
          height: '48px',
          borderRadius: '6px',
          backgroundColor: color,
          border: `1px solid ${tokens.colorNeutralStroke2}`,
          flexShrink: 0,
        }}
      />
      
      {/* Product Info */}
      <div className="product-info" style={{ flex: 1, minWidth: 0 }}>
        <Text 
          weight="semibold" 
          size={300}
          style={{ 
            display: 'block',
            color: tokens.colorNeutralForeground1,
            marginBottom: '2px',
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
          }}
        >
          {product.tags || product.description || 'soft white, airy, minimal, fresh'}
        </Text>
        <Text 
          weight="semibold" 
          size={200}
          style={{ 
            display: 'block',
            color: tokens.colorNeutralForeground1,
            marginTop: '4px',
          }}
        >
          ${product.price?.toFixed(2) || '59.95'} USD
        </Text>
      </div>
      
      {/* Select Button */}
      {showSelectButton && (
        <Button
          appearance={isSelected ? 'primary' : 'outline'}
          size="small"
          onClick={(e) => {
            e.stopPropagation();
            onClick();
          }}
          style={{
            minWidth: '70px',
          }}
        >
          Select
        </Button>
      )}
    </div>
  );
}

// Product Card - Grid View (Style 2)
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
        flexDirection: 'column',
        alignItems: 'flex-start',
        gap: '8px',
        padding: '12px',
        borderRadius: '8px',
        border: `1px dashed ${tokens.colorNeutralStroke2}`,
        backgroundColor: tokens.colorNeutralBackground1,
        cursor: 'pointer',
        transition: 'all 0.15s ease-in-out',
      }}
    >
      {/* Color Swatch - Square with rounded corners */}
      <div 
        className="product-color-swatch"
        style={{
          width: '40px',
          height: '40px',
          borderRadius: '6px',
          backgroundColor: color,
          border: `1px solid ${tokens.colorNeutralStroke2}`,
        }}
      />
      
      {/* Product Info */}
      <div className="product-info" style={{ width: '100%' }}>
        <Text 
          weight="semibold" 
          size={200}
          style={{ 
            display: 'block',
            color: tokens.colorNeutralForeground1,
            marginBottom: '2px',
          }}
        >
          {product.product_name}
        </Text>
        <Text 
          size={100}
          style={{ 
            display: 'block',
            color: tokens.colorNeutralForeground3,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {product.tags || product.description || 'soft white, airy, minimal, fresh'}
        </Text>
        <Text 
          weight="semibold" 
          size={100}
          style={{ 
            display: 'block',
            color: tokens.colorNeutralForeground1,
            marginTop: '4px',
          }}
        >
          ${product.price?.toFixed(2) || '59.95'} USD
        </Text>
      </div>
    </div>
  );
}
