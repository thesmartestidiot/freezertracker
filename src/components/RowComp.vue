<script setup lang="ts">
import { Row } from "@/types";
defineProps<{ row: Row }>();
defineEmits<{
  (e: "update:quantity", value: number): void;
}>();
</script>

<template>
  <div
    class="flex h-16 w-full gap-4 items-center justify-between bg-gray-800 px-4 text-white rounded-lg"
  >
    <span class="w-lg">{{ row.label }}</span>
    <span class="w-16 text-center">{{ row.quantity }}</span>
    <button
      type="button"
      class="flex items-center justify-center bg-gray-700 size-8 p-2 rounded"
      @click="$emit('update:quantity', row.quantity - 1)"
    >
      -
    </button>
    <button
      type="button"
      class="flex items-center justify-center bg-gray-700 size-8 p-2 rounded"
      @click="$emit('update:quantity', row.quantity + 1)"
    >
      +
    </button>
  </div>
</template>
