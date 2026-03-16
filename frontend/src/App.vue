<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import RowComp from '@/components/RowComp.vue'
import AddItemModal from '@/components/AddItemModal.vue'
import type { Item, Tag } from '@/types'
import { fetchItems, fetchTags, createItem, updateItem, deleteItem } from '@/api'

const items = ref<Item[]>([])
const tags = ref<Tag[]>([])
const activeTag = ref<string | null>(null)

const sortedItems = computed(() => {
  return [...items.value].sort((a, b) => a.name.localeCompare(b.name))
})

const filteredItems = computed(() => {
  if (!activeTag.value) return sortedItems.value
  return sortedItems.value.filter((item) =>
    item.tags.some((t) => t.name.toLowerCase() === activeTag.value!.toLowerCase()),
  )
})

async function loadData() {
  const [itemData, tagData] = await Promise.all([fetchItems(), fetchTags()])
  items.value = itemData
  tags.value = tagData
}

async function handleUpdateQuantity(id: number, quantity: number) {
  await updateItem(id, { quantity: Math.max(0, quantity) })
  await loadData()
}

async function handleAddItem(name: string, unit: string | null, itemTags: string[]) {
  await createItem({ name, unit: unit || undefined, tags: itemTags })
  await loadData()
}

async function handleDeleteItem(id: number) {
  await deleteItem(id)
  await loadData()
}

function toggleTag(tagName: string) {
  activeTag.value = activeTag.value === tagName ? null : tagName
}

onMounted(loadData)
</script>

<template>
  <div class="h-screen w-screen bg-gray-900 p-4">
    <div class="mx-auto flex h-full w-full flex-col overflow-hidden rounded-lg bg-gray-800">
      <header class="flex items-center gap-4 border-b border-gray-700 p-4">
        <img src="./assets/doggo.png" alt="" class="h-14 w-14 rounded-lg object-cover" />
        <div class="flex-1">
          <h1 class="text-xl font-semibold text-white">Freezer Tracker</h1>
          <p class="text-sm text-gray-300">Manage your inventory</p>
        </div>
      </header>

      <div v-if="tags.length" class="flex gap-2 overflow-x-auto border-b border-gray-700 px-4 py-3">
        <button
          v-for="tag in tags"
          :key="tag.id"
          type="button"
          class="shrink-0 rounded-full px-3 py-1 text-sm font-medium transition"
          :class="
            activeTag === tag.name
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          "
          @click="toggleTag(tag.name)"
        >
          {{ tag.name }}
        </button>
      </div>

      <main class="min-h-0 flex-1 overflow-y-auto p-4 space-y-4">
        <RowComp
          v-for="item in filteredItems"
          :key="item.id"
          :item="item"
          @update-quantity="handleUpdateQuantity(item.id, $event)"
          @delete="handleDeleteItem(item.id)"
        />
      </main>

      <footer class="flex justify-between items-center w-full border-t border-gray-700 p-4">
        <div class="text-xl text-gray-300">{{ filteredItems.length }} items</div>
        <AddItemModal :tags="tags" @add-item="handleAddItem" />
      </footer>
    </div>
  </div>
</template>
