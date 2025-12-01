import { useState, useEffect } from 'react';
import {
  Card,
  CardHeader,
  Button,
  Input,
  Text,
  Title3,
  Checkbox,
  Spinner,
  tokens,
} from '@fluentui/react-components';
import {
  Search24Regular,
  Sparkle24Regular,
  Box24Regular,
} from '@fluentui/react-icons';
import type { Product } from '../types';

interface ProductSelectorProps {
  selectedProducts: Product[];
  onProductsChange: (products: Product[]) => void;
  onGenerate: () => void;
  isLoading: boolean;
}

export function ProductSelector({
  selectedProducts,
  onProductsChange,
  onGenerate,
  isLoading,
}: ProductSelectorProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState<Product[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    // Load initial products
    loadProducts();
  }, []);

  const loadProducts = async (search?: string) => {
    setIsSearching(true);
    try {
      const { getProducts } = await import('../api');
      const result = await getProducts({ search, limit: 10 });
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
    <Card className="panel-card">
      <CardHeader
        header={<Title3>Select Products</Title3>}
      />
      
      <Text size={200} style={{ color: tokens.colorNeutralForeground3, marginBottom: '16px' }}>
        Choose products to feature in your marketing content.
      </Text>
      
      {/* Search */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        <Input
          style={{ flex: 1 }}
          placeholder="Search products..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
        <Button
          icon={<Search24Regular />}
          onClick={handleSearch}
          disabled={isSearching}
        />
      </div>
      
      {/* Product List */}
      <div style={{ 
        maxHeight: '300px', 
        overflowY: 'auto',
        marginBottom: '16px',
        border: `1px solid ${tokens.colorNeutralStroke1}`,
        borderRadius: '4px'
      }}>
        {isSearching ? (
          <div style={{ padding: '24px', textAlign: 'center' }}>
            <Spinner size="small" />
          </div>
        ) : products.length === 0 ? (
          <div style={{ padding: '24px', textAlign: 'center', color: tokens.colorNeutralForeground3 }}>
            <Box24Regular style={{ fontSize: '32px', marginBottom: '8px' }} />
            <Text>No products found</Text>
          </div>
        ) : (
          products.map((product) => (
            <div
              key={product.sku}
              style={{
                padding: '12px',
                borderBottom: `1px solid ${tokens.colorNeutralStroke1}`,
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
              }}
            >
              <Checkbox
                checked={isProductSelected(product)}
                onChange={(_, data) => handleProductToggle(product, !!data.checked)}
              />
              <div style={{ flex: 1 }}>
                <Text weight="semibold" size={200} block>
                  {product.product_name}
                </Text>
                <Text size={100} style={{ color: tokens.colorNeutralForeground3 }}>
                  {product.category} • {product.sku}
                </Text>
                {product.marketing_description && (
                  <Text size={100} block style={{ 
                    marginTop: '4px',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical'
                  }}>
                    {product.marketing_description}
                  </Text>
                )}
              </div>
              {product.image_url && (
                <img
                  src={product.image_url}
                  alt={product.product_name}
                  style={{
                    width: '48px',
                    height: '48px',
                    objectFit: 'cover',
                    borderRadius: '4px'
                  }}
                />
              )}
            </div>
          ))
        )}
      </div>
      
      {/* Selected Count */}
      {selectedProducts.length > 0 && (
        <Text size={200} style={{ marginBottom: '12px' }}>
          {selectedProducts.length} product(s) selected
        </Text>
      )}
      
      {/* Generate Button */}
      <Button
        appearance="primary"
        icon={<Sparkle24Regular />}
        onClick={onGenerate}
        disabled={isLoading}
        style={{ width: '100%' }}
      >
        {isLoading ? 'Generating...' : 'Generate Content'}
      </Button>
    </Card>
  );
}
