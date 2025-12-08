import { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Input,
  Text,
  Checkbox,
  Spinner,
  Badge,
  tokens,
} from '@fluentui/react-components';
import {
  Search24Regular,
  Sparkle24Regular,
  Box24Regular,
  Bot24Regular,
} from '@fluentui/react-icons';
import type { Product } from '../types';

interface InlineProductSelectorProps {
  selectedProducts: Product[];
  onProductsChange: (products: Product[]) => void;
  onGenerate: () => void;
  isLoading: boolean;
}

export function InlineProductSelector({
  selectedProducts,
  onProductsChange,
  onGenerate,
  isLoading,
}: InlineProductSelectorProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState<Product[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async (search?: string) => {
    setIsSearching(true);
    try {
      const { getProducts } = await import('../api');
      const result = await getProducts({ search, limit: 8 });
      setProducts(result.products);
    } catch (error) {
      console.error('Error loading products:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSearch = () => {
    loadProducts(searchQuery);
  };

  const handleProductToggle = (product: Product, checked: boolean) => {
    if (checked) {
      onProductsChange([...selectedProducts, product]);
    } else {
      onProductsChange(selectedProducts.filter(p => p.sku !== product.sku));
    }
  };

  const isProductSelected = (product: Product) =>
    selectedProducts.some(p => p.sku === product.sku);

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
        minWidth: 0, /* Allow card to shrink */
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
          Select Products for Your Campaign
        </Text>
        
        <Text 
          size={200} 
          style={{ 
            color: tokens.colorNeutralForeground3, 
            marginBottom: 'clamp(8px, 1.5vw, 12px)', 
            display: 'block',
            fontSize: 'clamp(11px, 1.5vw, 13px)',
          }}
        >
          Choose products to feature in your marketing content, then click Generate.
        </Text>
        
        {/* Search */}
        <div style={{ 
          display: 'flex', 
          gap: '8px', 
          marginBottom: 'clamp(8px, 1.5vw, 12px)',
        }}>
          <Input
            style={{ flex: 1, minWidth: 0 }}
            placeholder="Search products..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            size="small"
          />
          <Button
            icon={<Search24Regular />}
            onClick={handleSearch}
            disabled={isSearching}
            size="small"
          />
        </div>
        
        {/* Product List */}
        <div style={{ 
          maxHeight: 'clamp(180px, 30vh, 250px)', 
          overflowY: 'auto',
          marginBottom: 'clamp(8px, 1.5vw, 12px)',
          border: `1px solid ${tokens.colorNeutralStroke1}`,
          borderRadius: '4px'
        }}>
          {isSearching ? (
            <div style={{ padding: 'clamp(12px, 2vw, 16px)', textAlign: 'center' }}>
              <Spinner size="tiny" />
            </div>
          ) : products.length === 0 ? (
            <div style={{ 
              padding: 'clamp(12px, 2vw, 16px)', 
              textAlign: 'center', 
              color: tokens.colorNeutralForeground3 
            }}>
              <Box24Regular style={{ fontSize: 'clamp(20px, 3vw, 24px)', marginBottom: '4px' }} />
              <Text size={200}>No products found</Text>
            </div>
          ) : (
            products.map((product) => (
              <div
                key={product.sku}
                style={{
                  padding: 'clamp(6px, 1vw, 8px) clamp(8px, 1.5vw, 12px)',
                  borderBottom: `1px solid ${tokens.colorNeutralStroke1}`,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'clamp(6px, 1vw, 8px)',
                  backgroundColor: isProductSelected(product) ? tokens.colorBrandBackground2 : 'transparent',
                }}
              >
                <Checkbox
                  checked={isProductSelected(product)}
                  onChange={(_, data) => handleProductToggle(product, !!data.checked)}
                />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <Text 
                    weight="semibold" 
                    size={200} 
                    block 
                    style={{ 
                      overflow: 'hidden', 
                      textOverflow: 'ellipsis', 
                      whiteSpace: 'nowrap',
                      fontSize: 'clamp(11px, 1.5vw, 13px)',
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
                    {product.tags} • ${product.price?.toFixed(2) || '59.95'}
                  </Text>
                </div>
                {product.image_url && (
                  <img
                    src={product.image_url}
                    alt={product.product_name}
                    style={{
                      width: 'clamp(28px, 5vw, 36px)',
                      height: 'clamp(28px, 5vw, 36px)',
                      objectFit: 'cover',
                      borderRadius: '4px',
                      flexShrink: 0,
                    }}
                  />
                )}
              </div>
            ))
          )}
        </div>
        
        {/* Footer */}
        <div style={{ 
          display: 'flex', 
          flexDirection: 'row',
          flexWrap: 'wrap',
          justifyContent: 'space-between', 
          alignItems: 'center',
          gap: '8px',
        }}>
          <Text 
            size={200} 
            style={{ 
              color: tokens.colorNeutralForeground3,
              fontSize: 'clamp(11px, 1.5vw, 13px)',
            }}
          >
            {selectedProducts.length} product(s) selected
          </Text>
          
          <Button
            appearance="primary"
            icon={<Sparkle24Regular />}
            onClick={onGenerate}
            disabled={isLoading}
            size="small"
          >
            {isLoading ? 'Generating...' : 'Generate Content'}
          </Button>
        </div>
      </Card>
    </div>
  );
}
