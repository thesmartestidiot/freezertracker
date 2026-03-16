<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import type { Tag } from '@/types'

const props = defineProps<{ tags: Tag[] }>()

const emit = defineEmits<{
  addItem: [name: string, unit: string | null, tags: string[]]
}>()

const isOpen = ref(false)
const newItemName = ref('')
const newItemUnit = ref('')
const tagInput = ref('')
const selectedTags = ref<string[]>([])
const inputRef = ref<HTMLInputElement | null>(null)

const canSubmit = computed(() => newItemName.value.trim().length > 0)

const filteredSuggestions = computed(() => {
  if (!tagInput.value.trim()) return []
  const query = tagInput.value.toLowerCase()
  return props.tags
    .filter(
      (t) =>
        t.name.toLowerCase().includes(query) &&
        !selectedTags.value.includes(t.name),
    )
    .slice(0, 5)
})

function openModal() {
  isOpen.value = true
}

function closeModal() {
  isOpen.value = false
  newItemName.value = ''
  newItemUnit.value = ''
  tagInput.value = ''
  selectedTags.value = []
}

function submitItem() {
  const name = newItemName.value.trim()
  if (name) {
    const unit = newItemUnit.value.trim() || null
    emit('addItem', name, unit, [...selectedTags.value])
    closeModal()
  }
}

function addTag(tagName: string) {
  const name = tagName.trim()
  if (name && !selectedTags.value.includes(name)) {
    selectedTags.value.push(name)
  }
  tagInput.value = ''
}

function removeTag(tagName: string) {
  selectedTags.value = selectedTags.value.filter((t) => t !== tagName)
}

function handleTagKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    e.preventDefault()
    if (tagInput.value.trim()) {
      addTag(tagInput.value)
    }
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
    <button
      type="button"
      class="rounded bg-blue-600 px-4 py-2 font-medium text-white transition hover:bg-blue-500"
      @click="openModal"
    >
      Add Item
    </button>
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
        aria-label="Add new item"
        class="w-full max-w-md rounded-lg border border-gray-700 bg-gray-800 p-6 text-white shadow-2xl"
        @keydown.esc="closeModal"
      >
        <h2 class="mb-4 text-xl font-semibold">Add New Item</h2>

        <label for="new-item-name" class="mb-2 block text-sm text-gray-300">Item name</label>
        <input
          id="new-item-name"
          ref="inputRef"
          v-model="newItemName"
          type="text"
          placeholder="ex: Ground beef"
          class="mb-4 w-full rounded border border-gray-600 bg-gray-900 px-3 py-2 text-white outline-none transition focus:border-blue-500"
          @keydown.enter.prevent="submitItem"
        />

        <label for="new-item-unit" class="mb-2 block text-sm text-gray-300">Unit (optional)</label>
        <input
          id="new-item-unit"
          v-model="newItemUnit"
          type="text"
          placeholder="ex: lbs, bags, packs"
          class="mb-4 w-full rounded border border-gray-600 bg-gray-900 px-3 py-2 text-white outline-none transition focus:border-blue-500"
        />

        <label class="mb-2 block text-sm text-gray-300">Tags</label>
        <div class="mb-2 flex flex-wrap gap-2">
          <span
            v-for="tag in selectedTags"
            :key="tag"
            class="flex items-center gap-1 rounded-full bg-blue-600 px-3 py-1 text-sm"
          >
            {{ tag }}
            <button type="button" class="ml-1 text-blue-200 hover:text-white" @click="removeTag(tag)">
              &times;
            </button>
          </span>
        </div>
        <div class="relative mb-5">
          <input
            v-model="tagInput"
            type="text"
            placeholder="Type to add tags..."
            class="w-full rounded border border-gray-600 bg-gray-900 px-3 py-2 text-white outline-none transition focus:border-blue-500"
            @keydown="handleTagKeydown"
          />
          <div
            v-if="filteredSuggestions.length"
            class="absolute z-10 mt-1 w-full rounded border border-gray-600 bg-gray-900 shadow-lg"
          >
            <button
              v-for="suggestion in filteredSuggestions"
              :key="suggestion.id"
              type="button"
              class="block w-full px-3 py-2 text-left text-sm text-gray-200 hover:bg-gray-700"
              @click="addTag(suggestion.name)"
            >
              {{ suggestion.name }}
            </button>
          </div>
        </div>

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
