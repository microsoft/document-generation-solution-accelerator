/**
 * API service for interacting with the Content Generation backend
 */

import type {
  CreativeBrief,
  Product,
  ChatMessage,
  AgentResponse,
  BrandGuidelines,
  ParsedBriefResponse,
  Conversation,
} from '../types';

const API_BASE = '/api';

/**
 * Parse a free-text creative brief into structured format
 */
export async function parseBrief(
  briefText: string,
  conversationId?: string,
  userId?: string
): Promise<ParsedBriefResponse> {
  const response = await fetch(`${API_BASE}/brief/parse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      brief_text: briefText,
      conversation_id: conversationId,
      user_id: userId || 'anonymous',
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to parse brief: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Confirm a parsed creative brief
 */
export async function confirmBrief(
  brief: CreativeBrief,
  conversationId?: string,
  userId?: string
): Promise<{ status: string; conversation_id: string; brief: CreativeBrief }> {
  const response = await fetch(`${API_BASE}/brief/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      brief,
      conversation_id: conversationId,
      user_id: userId || 'anonymous',
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to confirm brief: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Stream chat messages from the agent orchestration
 */
export async function* streamChat(
  message: string,
  conversationId?: string,
  userId?: string
): AsyncGenerator<AgentResponse> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      user_id: userId || 'anonymous',
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('No response body');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') {
          return;
        }
        try {
          yield JSON.parse(data) as AgentResponse;
        } catch {
          console.error('Failed to parse SSE data:', data);
        }
      }
    }
  }
}

/**
 * Generate content from a confirmed brief
 */
export async function* streamGenerateContent(
  brief: CreativeBrief,
  products?: Product[],
  generateImages: boolean = true,
  conversationId?: string,
  userId?: string
): AsyncGenerator<AgentResponse> {
  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      brief,
      products: products || [],
      generate_images: generateImages,
      conversation_id: conversationId,
      user_id: userId || 'anonymous',
    }),
  });

  if (!response.ok) {
    throw new Error(`Content generation failed: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('No response body');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') {
          return;
        }
        try {
          yield JSON.parse(data) as AgentResponse;
        } catch {
          console.error('Failed to parse SSE data:', data);
        }
      }
    }
  }
}

/**
 * Get products from the catalog
 */
export async function getProducts(params?: {
  category?: string;
  sub_category?: string;
  search?: string;
  limit?: number;
}): Promise<{ products: Product[]; count: number }> {
  const searchParams = new URLSearchParams();
  if (params?.category) searchParams.set('category', params.category);
  if (params?.sub_category) searchParams.set('sub_category', params.sub_category);
  if (params?.search) searchParams.set('search', params.search);
  if (params?.limit) searchParams.set('limit', params.limit.toString());

  const response = await fetch(`${API_BASE}/products?${searchParams}`);

  if (!response.ok) {
    throw new Error(`Failed to get products: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get a single product by SKU
 */
export async function getProduct(sku: string): Promise<Product> {
  const response = await fetch(`${API_BASE}/products/${sku}`);

  if (!response.ok) {
    throw new Error(`Failed to get product: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Upload a product image
 */
export async function uploadProductImage(
  sku: string,
  file: File
): Promise<{ image_url: string; image_description: string }> {
  const formData = new FormData();
  formData.append('image', file);

  const response = await fetch(`${API_BASE}/products/${sku}/image`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Failed to upload image: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get brand guidelines
 */
export async function getBrandGuidelines(): Promise<BrandGuidelines> {
  const response = await fetch(`${API_BASE}/brand-guidelines`);

  if (!response.ok) {
    throw new Error(`Failed to get brand guidelines: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get user conversations
 */
export async function getConversations(
  userId: string,
  limit?: number
): Promise<{ conversations: Conversation[]; count: number }> {
  const searchParams = new URLSearchParams();
  searchParams.set('user_id', userId);
  if (limit) searchParams.set('limit', limit.toString());

  const response = await fetch(`${API_BASE}/conversations?${searchParams}`);

  if (!response.ok) {
    throw new Error(`Failed to get conversations: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get a specific conversation
 */
export async function getConversation(
  conversationId: string,
  userId: string
): Promise<Conversation> {
  const response = await fetch(
    `${API_BASE}/conversations/${conversationId}?user_id=${userId}`
  );

  if (!response.ok) {
    throw new Error(`Failed to get conversation: ${response.statusText}`);
  }

  return response.json();
}
