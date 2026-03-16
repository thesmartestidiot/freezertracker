import type { Item, Tag, CreateItemRequest, UpdateItemRequest, CreateTagRequest } from '@/types'

const BASE = '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!resp.ok) {
    throw new Error(`API error: ${resp.status}`)
  }
  if (resp.status === 204) return undefined as T
  return resp.json()
}

export async function fetchItems(tag?: string | string[]): Promise<Item[]> {
  const params = new URLSearchParams()
  if (tag) {
    const tags = Array.isArray(tag) ? tag : [tag]
    tags.forEach((t) => params.append('tag', t))
  }
  const query = params.toString()
  return request<Item[]>(`/items${query ? `?${query}` : ''}`)
}

export async function createItem(data: CreateItemRequest): Promise<Item> {
  return request<Item>('/items', { method: 'POST', body: JSON.stringify(data) })
}

export async function updateItem(id: number, data: UpdateItemRequest): Promise<Item> {
  return request<Item>(`/items/${id}`, { method: 'PATCH', body: JSON.stringify(data) })
}

export async function deleteItem(id: number): Promise<void> {
  return request<void>(`/items/${id}`, { method: 'DELETE' })
}

export async function fetchTags(): Promise<Tag[]> {
  return request<Tag[]>('/tags')
}

export async function createTag(data: CreateTagRequest): Promise<Tag> {
  return request<Tag>('/tags', { method: 'POST', body: JSON.stringify(data) })
}

export async function deleteTag(id: number): Promise<void> {
  return request<void>(`/tags/${id}`, { method: 'DELETE' })
}
