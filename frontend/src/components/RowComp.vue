<script setup lang="ts">
import type { Item } from '@/types'

defineProps<{ item: Item }>()
defineEmits<{
  updateQuantity: [value: number]
  delete: []
}>()
</script>

<template>
  <div
    class="flex h-16 w-full gap-4 items-center justify-between bg-gray-800 px-4 text-white rounded-lg text-3xl"
  >
    <div class="flex flex-1 items-center gap-3 overflow-hidden">
      <span class="truncate">{{ item.name }}</span>
      <span v-if="item.unit" class="text-base text-gray-400">({{ item.unit }})</span>
      <span
        v-for="tag in item.tags"
        :key="tag.id"
        class="rounded-full px-2 py-0.5 text-xs font-medium"
        :style="{ backgroundColor: tag.color || '#374151', color: '#fff' }"
      >
        {{ tag.name }}
      </span>
    </div>
    <button
      type="button"
      class="flex items-center justify-center bg-gray-700 size-14 p-2 rounded"
      @click="$emit('updateQuantity', item.quantity - 1)"
    >
      -
    </button>
    <span class="w-16 text-center">{{ item.quantity }}</span>
    <button
      type="button"
      class="flex items-center justify-center bg-gray-700 size-14 p-2 rounded"
      @click="$emit('updateQuantity', item.quantity + 1)"
    >
      +
    </button>
    <button
      v-if="item.quantity === 0"
      type="button"
      class="flex items-center justify-center bg-red-700 size-14 p-2 rounded text-lg"
      @click="$emit('delete')"
    >
      &times;
    </button>
  </div>
</template>
