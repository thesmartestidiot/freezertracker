export interface Tag {
  id: number
  name: string
  color: string | null
}

export interface Item {
  id: number
  name: string
  quantity: number
  unit: string | null
  barcode: string | null
  tags: Tag[]
  created_at: string
  updated_at: string
}

export interface CreateItemRequest {
  name: string
  quantity?: number
  unit?: string | null
  tags?: string[]
}

export interface UpdateItemRequest {
  name?: string
  quantity?: number
  unit?: string | null
  tags?: string[]
}

export interface CreateTagRequest {
  name: string
  color?: string | null
}
