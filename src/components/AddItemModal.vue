<script setup lang="ts">
import { ref } from "vue";

const emit = defineEmits<{
  (e: "add-item", value: string): void;
}>();

const isOpen = ref(false);
const newItemLabel = ref("");

const addItem = (label: string) => {
  if (label.trim()) {
    emit("add-item", label);
    newItemLabel.value = "";
    isOpen.value = false;
  }
};
</script>

<template>
  <div>
    <slot>
      <button type="button" class="px-4 py-2 bg-blue-600 text-white rounded" @click="isOpen = true">
        Add Item
      </button>
    </slot>

    <div
      v-if="isOpen"
      class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50"
    >
      <div class="bg-white p-6 rounded-lg w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">Add New Item</h2>
        <input
          type="text"
          v-model="newItemLabel"
          placeholder="Item name"
          class="w-full px-4 py-2 border rounded mb-4"
        />
        <button
          type="button"
          class="px-4 py-2 bg-blue-600 text-white rounded"
          @click="addItem(newItemLabel)"
        >
          Add
        </button>

        <button type="button" class="mt-4 px-4 py-2 bg-gray-300 rounded" @click="isOpen = false">
          Close
        </button>
      </div>
    </div>
  </div>
</template>
