<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'

const emit = defineEmits<{
  (e: 'add-item', value: string): void
}>()

const isOpen = ref(false)
const newItemLabel = ref('')
const inputRef = ref<HTMLInputElement | null>(null)

const canSubmit = computed(() => newItemLabel.value.trim().length > 0)

const openModal = () => {
  isOpen.value = true
}

const closeModal = () => {
  isOpen.value = false
  newItemLabel.value = ''
}

const submitItem = () => {
  const label = newItemLabel.value.trim()
  if (label) {
    emit('add-item', label)
    closeModal()
  }
}

watch(isOpen, async (open) => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = open ? 'hidden' : ''
  }

  if (open) {
    await nextTick()
    inputRef.value?.focus()
  }
})

onBeforeUnmount(() => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = ''
  }
})
</script>

<template>
  <div class="inline-flex">
    <slot>
      <button
        type="button"
        class="rounded bg-blue-600 px-4 py-2 font-medium text-white transition hover:bg-blue-500"
        @click="openModal"
      >
        Add Item
      </button>
    </slot>
  </div>

  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
      @click.self="closeModal"
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Add new freezer item"
        class="w-full max-w-md rounded-lg border border-gray-700 bg-gray-800 p-6 text-white shadow-2xl"
        @keydown.esc="closeModal"
      >
        <h2 class="mb-4 text-xl font-semibold">Add New Item</h2>
        <label for="new-item-label" class="mb-2 block text-sm text-gray-300">Item name</label>
        <input
          id="new-item-label"
          ref="inputRef"
          v-model="newItemLabel"
          type="text"
          placeholder="ex: Ground beef"
          class="mb-5 w-full rounded border border-gray-600 bg-gray-900 px-3 py-2 text-white outline-none ring-0 transition focus:border-blue-500"
          @keydown.enter.prevent="submitItem"
        />

        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="rounded border border-gray-600 px-4 py-2 text-gray-200 transition hover:bg-gray-700"
            @click="closeModal"
          >
            Cancel
          </button>
          <button
            type="button"
            class="rounded bg-blue-600 px-4 py-2 font-medium text-white transition enabled:hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="!canSubmit"
            @click="submitItem"
          >
            Add
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
