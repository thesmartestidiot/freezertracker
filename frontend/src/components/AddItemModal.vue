<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import type { Tag } from '@/types'

const props = defineProps<{
  tags: Tag[]
  kiosk: boolean
}>()

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
  <div class="inline-flex w-full items-center justify-center">
    <!-- Kiosk trigger -->
    <button
      v-if="kiosk"
      type="button"
      class="flex size-12 cursor-pointer items-center justify-center rounded-full border-0 bg-terracotta text-white transition-[background-color,transform] duration-150 active:scale-90 active:bg-terracotta-dark focus-visible:ring-2 focus-visible:ring-terracotta/40 focus-visible:ring-offset-2 focus-visible:ring-offset-cream focus-visible:outline-none dark:bg-d-terracotta dark:active:bg-d-terracotta-hover dark:focus-visible:ring-offset-d-bg"
      aria-label="Add new item"
      @click="openModal"
    >
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-6">
        <path d="M10.75 4.75a.75.75 0 0 0-1.5 0v4.5h-4.5a.75.75 0 0 0 0 1.5h4.5v4.5a.75.75 0 0 0 1.5 0v-4.5h4.5a.75.75 0 0 0 0-1.5h-4.5v-4.5Z" />
      </svg>
    </button>
    <!-- Desktop trigger -->
    <button
      v-else
      type="button"
      class="flex w-full cursor-pointer items-center justify-center gap-2 rounded-xl border-0 bg-terracotta px-4 py-2.5 text-sm font-semibold text-white transition-[background-color,transform] duration-150 hover:bg-terracotta-dark active:scale-98 focus-visible:ring-2 focus-visible:ring-terracotta/40 focus-visible:ring-offset-2 focus-visible:ring-offset-surface focus-visible:outline-none dark:bg-d-terracotta dark:hover:bg-d-terracotta-hover dark:focus-visible:ring-offset-d-surface"
      @click="openModal"
    >
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4">
        <path d="M10.75 4.75a.75.75 0 0 0-1.5 0v4.5h-4.5a.75.75 0 0 0 0 1.5h4.5v4.5a.75.75 0 0 0 1.5 0v-4.5h4.5a.75.75 0 0 0 0-1.5h-4.5v-4.5Z" />
      </svg>
      Add Item
    </button>
  </div>

  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-end justify-center sm:items-center"
        @click.self="closeModal"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-ink/30 backdrop-blur-sm dark:bg-black/50" @click="closeModal" />

        <!-- Modal panel -->
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Add new item"
          class="relative z-10 w-full rounded-t-2xl bg-surface p-7 shadow-[0_-4px_40px_rgba(44,36,22,0.12)] sm:max-w-md sm:rounded-2xl sm:shadow-[0_8px_40px_rgba(44,36,22,0.15)] dark:bg-d-surface dark:shadow-[0_8px_40px_rgba(0,0,0,0.4)]"
          :class="kiosk ? 'sm:max-w-lg' : ''"
          @keydown.esc="closeModal"
        >
          <!-- Header -->
          <div class="mb-6 flex items-center justify-between">
            <h2
              class="font-display font-semibold tracking-tight text-ink dark:text-d-text"
              :class="kiosk ? 'text-3xl' : 'text-2xl'"
            >
              New Item
            </h2>
            <button
              type="button"
              class="flex cursor-pointer items-center justify-center rounded-full text-ink-faint transition hover:bg-cream-dark hover:text-ink dark:text-d-text-faint dark:hover:bg-d-surface-hover dark:hover:text-d-text"
              :class="kiosk ? 'size-10' : 'size-8'"
              @click="closeModal"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" :class="kiosk ? 'size-6' : 'size-5'">
                <path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z" />
              </svg>
            </button>
          </div>

          <!-- Name -->
          <label
            for="new-item-name"
            class="mb-1.5 block font-medium text-ink dark:text-d-text"
            :class="kiosk ? 'text-[0.9375rem]' : 'text-[0.8125rem]'"
          >
            Name
          </label>
          <input
            id="new-item-name"
            ref="inputRef"
            v-model="newItemName"
            type="text"
            placeholder="Ground beef, chicken thighs..."
            class="mb-4 w-full rounded-xl border-1.5 border-border bg-cream font-body text-ink placeholder:text-ink-faint outline-none transition focus:border-terracotta-light focus:ring-3 focus:ring-terracotta/10 dark:border-d-border dark:bg-d-bg dark:text-d-text dark:placeholder:text-d-text-faint dark:focus:border-d-terracotta dark:focus:ring-d-terracotta/10"
            :class="kiosk ? 'px-4 py-3.5 text-lg' : 'px-3.5 py-2.5 text-[0.9375rem]'"
            @keydown.enter.prevent="submitItem"
          />

          <!-- Unit -->
          <label
            for="new-item-unit"
            class="mb-1.5 block font-medium text-ink dark:text-d-text"
            :class="kiosk ? 'text-[0.9375rem]' : 'text-[0.8125rem]'"
          >
            Unit <span class="font-normal text-ink-faint dark:text-d-text-faint">(optional)</span>
          </label>
          <input
            id="new-item-unit"
            v-model="newItemUnit"
            type="text"
            placeholder="lbs, bags, packs..."
            class="mb-4 w-full rounded-xl border-1.5 border-border bg-cream font-body text-ink placeholder:text-ink-faint outline-none transition focus:border-terracotta-light focus:ring-3 focus:ring-terracotta/10 dark:border-d-border dark:bg-d-bg dark:text-d-text dark:placeholder:text-d-text-faint dark:focus:border-d-terracotta dark:focus:ring-d-terracotta/10"
            :class="kiosk ? 'px-4 py-3.5 text-lg' : 'px-3.5 py-2.5 text-[0.9375rem]'"
          />

          <!-- Tags -->
          <label
            class="mb-1.5 block font-medium text-ink dark:text-d-text"
            :class="kiosk ? 'text-[0.9375rem]' : 'text-[0.8125rem]'"
          >
            Tags
          </label>
          <div v-if="selectedTags.length" class="mb-2 flex flex-wrap gap-2">
            <span
              v-for="tag in selectedTags"
              :key="tag"
              class="inline-flex items-center rounded-full border border-border bg-cream-dark font-medium text-ink dark:border-d-border dark:bg-d-surface-hover dark:text-d-text"
              :class="kiosk ? 'px-3 py-1.5 text-[0.9375rem]' : 'px-2.5 py-1 text-[0.8125rem]'"
            >
              {{ tag }}
              <button
                type="button"
                class="ml-1.5 cursor-pointer text-ink-faint transition hover:text-terracotta dark:text-d-text-faint dark:hover:text-d-terracotta"
                @click="removeTag(tag)"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="size-3.5">
                  <path d="M5.28 4.22a.75.75 0 0 0-1.06 1.06L6.94 8l-2.72 2.72a.75.75 0 1 0 1.06 1.06L8 9.06l2.72 2.72a.75.75 0 1 0 1.06-1.06L9.06 8l2.72-2.72a.75.75 0 0 0-1.06-1.06L8 6.94 5.28 4.22Z" />
                </svg>
              </button>
            </span>
          </div>
          <div class="relative mb-6">
            <input
              v-model="tagInput"
              type="text"
              placeholder="Type to add tags..."
              class="w-full rounded-xl border-1.5 border-border bg-cream font-body text-ink placeholder:text-ink-faint outline-none transition focus:border-terracotta-light focus:ring-3 focus:ring-terracotta/10 dark:border-d-border dark:bg-d-bg dark:text-d-text dark:placeholder:text-d-text-faint dark:focus:border-d-terracotta dark:focus:ring-d-terracotta/10"
              :class="kiosk ? 'px-4 py-3.5 text-lg' : 'px-3.5 py-2.5 text-[0.9375rem]'"
              @keydown="handleTagKeydown"
            />
            <Transition name="dropdown">
              <div
                v-if="filteredSuggestions.length"
                class="absolute z-20 mt-1.5 w-full overflow-hidden rounded-xl border-1.5 border-border bg-surface shadow-lg dark:border-d-border dark:bg-d-surface"
              >
                <button
                  v-for="suggestion in filteredSuggestions"
                  :key="suggestion.id"
                  type="button"
                  class="block w-full cursor-pointer border-0 bg-transparent text-left text-ink transition hover:bg-cream dark:text-d-text dark:hover:bg-d-surface-hover"
                  :class="kiosk ? 'px-4 py-3.5 text-base' : 'px-3.5 py-2.5 text-sm'"
                  @click="addTag(suggestion.name)"
                >
                  {{ suggestion.name }}
                </button>
              </div>
            </Transition>
          </div>

          <!-- Actions -->
          <div class="flex gap-3">
            <button
              type="button"
              class="flex-1 cursor-pointer rounded-xl border-1.5 border-border-dark font-medium text-ink-light transition hover:border-ink-faint hover:text-ink dark:border-d-border-light dark:text-d-text-secondary dark:hover:border-d-text-faint dark:hover:text-d-text"
              :class="kiosk ? 'py-4 text-lg' : 'py-3 text-[0.9375rem]'"
              @click="closeModal"
            >
              Cancel
            </button>
            <button
              type="button"
              class="flex-1 cursor-pointer rounded-xl border-0 bg-terracotta font-semibold text-white transition enabled:hover:bg-terracotta-dark enabled:active:scale-98 disabled:cursor-not-allowed disabled:opacity-45 dark:bg-d-terracotta dark:enabled:hover:bg-d-terracotta-hover"
              :class="kiosk ? 'py-4 text-lg' : 'py-3 text-[0.9375rem]'"
              :disabled="!canSubmit"
              @click="submitItem"
            >
              Add Item
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* Modal transitions */
.modal-enter-active { transition: opacity 0.3s var(--ease-out-quart); }
.modal-enter-active [role="dialog"] { transition: transform 0.4s var(--ease-out-quint), opacity 0.3s var(--ease-out-quart); }
.modal-leave-active { transition: opacity 0.2s var(--ease-out-quart); }
.modal-leave-active [role="dialog"] { transition: transform 0.2s var(--ease-out-quart), opacity 0.15s var(--ease-out-quart); }
.modal-enter-from { opacity: 0; }
.modal-enter-from [role="dialog"] { transform: translateY(1.5rem); opacity: 0; }
.modal-leave-to { opacity: 0; }
.modal-leave-to [role="dialog"] { transform: translateY(0.75rem); opacity: 0; }

/* Dropdown transitions */
.dropdown-enter-active { transition: all 0.2s var(--ease-out-quart); }
.dropdown-leave-active { transition: all 0.15s var(--ease-out-quart); }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
