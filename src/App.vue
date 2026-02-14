<script setup lang="ts">
import { computed, reactive } from 'vue'
import RowComp from '@/components/RowComp.vue'
import AddItemModal from '@/components/AddItemModal.vue'

const rows = reactive([
  { id: 1, label: 'Chuck Steak', quantity: 1 },
  { id: 2, label: 'Ribeye', quantity: 2 },
  { id: 3, label: 'T-Bone', quantity: 3 },
  { id: 4, label: 'Sirloin', quantity: 4 },
  { id: 5, label: 'Brisket', quantity: 5 },
  { id: 6, label: 'Flank', quantity: 6 },
  { id: 7, label: 'Skirt', quantity: 7 },
  { id: 8, label: 'New Item', quantity: 1 },
  { id: 9, label: 'Another Item', quantity: 2 },
  { id: 10, label: 'More Item', quantity: 3 },
  { id: 11, label: 'Chicken', quantity: 4 },
  { id: 12, label: 'Pork', quantity: 5 },
  { id: 13, label: 'Fish', quantity: 6 },
])

const sortedRows = computed(() => {
  return [...rows].sort((a, b) => a.label.localeCompare(b.label))
})

const updateQuantity = (id: number, quantity: number) => {
  const row = rows.find((r) => r.id === id)
  if (row) {
    row.quantity = Math.max(0, quantity)
  }
}

const addItem = (label: string) => {
  const newId = rows.length ? Math.max(...rows.map((r) => r.id)) + 1 : 1
  rows.push({ id: newId, label, quantity: 1 })
}
</script>

<template>
  <div class="h-screen w-screen bg-gray-900 p-2">
    <div class="mx-auto flex h-full w-full flex-col overflow-hidden rounded-lg bg-gray-800">
      <header class="flex items-center gap-4 border-b border-gray-700 p-4">
        <img src="./assets/doggo.png" alt="" class="h-14 w-14 rounded-lg object-cover" />
        <div>
          <h1 class="text-xl font-semibold text-white">Freezer Tracker</h1>
          <p class="text-sm text-gray-300">Manage your inventory</p>
        </div>
      </header>

      <main class="min-h-0 flex-1 overflow-y-auto p-4 space-y-4">
        <RowComp
          v-for="row in sortedRows"
          :key="row.id"
          :row="row"
          @update:quantity="(value) => updateQuantity(row.id, value)"
        />
      </main>

      <footer class="flex justify-between items-center w-full border-t border-gray-700 p-4">
        <div class="text-xl text-gray-300">{{ sortedRows.length }} items</div>
        <AddItemModal @add-item="addItem" />
      </footer>
    </div>
  </div>
</template>
