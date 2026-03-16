<script setup lang="ts">
import type { Row } from '@/types'
defineProps<{ row: Row }>()
defineEmits({
  updateQuantity: (value: number) => typeof value === 'number',
})
</script>

<template>
  <div
    class="flex h-16 w-full gap-4 items-center justify-between bg-gray-800 px-4 text-white rounded-lg text-3xl"
  >
    <span class="w-lg">{{ row.label }}</span>
    <button
      type="button"
      class="flex items-center justify-center bg-gray-700 size-14 p-2 rounded"
      @click="$emit('updateQuantity', row.quantity - 1)"
    >
      -
    </button>
    <span class="w-16 text-center">{{ row.quantity }}</span>
    <button
      type="button"
      class="flex items-center justify-center bg-gray-700 size-14 p-2 rounded"
      @click="$emit('updateQuantity', row.quantity + 1)"
    >
      +
    </button>
  </div>
</template>
