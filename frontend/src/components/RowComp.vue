<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Item } from '@/types'

const props = defineProps<{
  item: Item
  kiosk: boolean
}>()
defineEmits<{
  updateQuantity: [value: number]
  delete: []
}>()

const qtyPulsing = ref(false)

watch(() => props.item.quantity, () => {
  qtyPulsing.value = false
  // Force reflow to restart animation
  void document.body.offsetHeight
  qtyPulsing.value = true
})

function onPulseEnd() {
  qtyPulsing.value = false
}
</script>

<template>
  <!-- ==================== KIOSK ROW ==================== -->
  <div
    v-if="kiosk"
    class="flex items-center gap-3 rounded-xl border border-border bg-surface px-4 py-3.5 dark:border-d-border dark:bg-d-surface"
  >
    <div class="min-w-0 flex-1">
      <span class="block truncate font-display text-2xl font-medium tracking-tight text-ink dark:text-d-text">
        {{ item.name }}
      </span>
      <span v-if="item.unit" class="text-xs font-medium uppercase tracking-widest text-ink-faint dark:text-d-text-faint">
        {{ item.unit }}
      </span>
    </div>

    <div class="flex items-center gap-1">
      <button
        type="button"
        aria-label="Decrease quantity"
        class="flex size-14 cursor-pointer items-center justify-center rounded-xl border-1.5 border-border-dark bg-cream transition-[border-color,background-color,color,transform] duration-150 active:scale-90 focus-visible:ring-2 focus-visible:ring-terracotta/30 focus-visible:outline-none dark:border-d-border-light dark:bg-d-bg dark:focus-visible:ring-d-terracotta/30"
        :class="item.quantity <= 1 ? 'active:border-terracotta-light active:bg-red-50 active:text-terracotta dark:active:border-d-terracotta dark:active:bg-red-950 dark:active:text-d-terracotta' : ''"
        @click="$emit('updateQuantity', item.quantity - 1)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-6 text-ink-light dark:text-d-text-secondary">
          <path fill-rule="evenodd" d="M4 10a.75.75 0 0 1 .75-.75h10.5a.75.75 0 0 1 0 1.5H4.75A.75.75 0 0 1 4 10Z" clip-rule="evenodd" />
        </svg>
      </button>

      <span
        class="w-14 text-center font-display text-3xl font-semibold tabular-nums text-ink dark:text-d-text"
        :class="{ 'qty-pulse': qtyPulsing }"
        @animationend="onPulseEnd"
      >
        {{ item.quantity }}
      </span>

      <button
        type="button"
        aria-label="Increase quantity"
        class="flex size-14 cursor-pointer items-center justify-center rounded-xl border-1.5 border-border-dark bg-cream transition-[border-color,background-color,color,transform] duration-150 active:scale-90 focus-visible:ring-2 focus-visible:ring-terracotta/30 focus-visible:outline-none dark:border-d-border-light dark:bg-d-bg dark:focus-visible:ring-d-terracotta/30"
        @click="$emit('updateQuantity', item.quantity + 1)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-6 text-ink-light dark:text-d-text-secondary">
          <path d="M10.75 4.75a.75.75 0 0 0-1.5 0v4.5h-4.5a.75.75 0 0 0 0 1.5h4.5v4.5a.75.75 0 0 0 1.5 0v-4.5h4.5a.75.75 0 0 0 0-1.5h-4.5v-4.5Z" />
        </svg>
      </button>

      <Transition name="fade">
        <button
          v-if="item.quantity === 0"
          type="button"
          aria-label="Delete item"
          class="ml-1 flex size-14 cursor-pointer items-center justify-center rounded-xl border-1.5 border-terracotta-light bg-red-50 text-terracotta transition-[border-color,background-color,color,transform] duration-150 active:scale-90 active:bg-terracotta active:text-white focus-visible:ring-2 focus-visible:ring-terracotta/40 focus-visible:outline-none dark:border-d-terracotta dark:bg-red-950 dark:text-d-terracotta dark:active:bg-d-terracotta dark:active:text-d-bg dark:focus-visible:ring-d-terracotta/40"
          @click="$emit('delete')"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-5">
            <path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 0 0 6 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 1 0 .23 1.482l.149-.022.841 10.518A2.75 2.75 0 0 0 7.596 19h4.807a2.75 2.75 0 0 0 2.742-2.53l.841-10.52.149.023a.75.75 0 0 0 .23-1.482A41.03 41.03 0 0 0 14 4.193V3.75A2.75 2.75 0 0 0 11.25 1h-2.5ZM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4ZM8.58 7.72a.75.75 0 0 0-1.5.06l.3 7.5a.75.75 0 1 0 1.5-.06l-.3-7.5Zm4.34.06a.75.75 0 1 0-1.5-.06l-.3 7.5a.75.75 0 1 0 1.5.06l.3-7.5Z" clip-rule="evenodd" />
          </svg>
        </button>
      </Transition>
    </div>
  </div>

  <!-- ==================== DESKTOP ROW ==================== -->
  <div
    v-else
    class="group flex items-center gap-4 rounded-xl border border-border bg-surface px-5 py-4 transition-[border-color,box-shadow] duration-200 hover:border-border-dark hover:shadow-sm dark:border-d-border dark:bg-d-surface dark:hover:border-d-border-light dark:hover:shadow-none"
    style="transition-timing-function: var(--ease-out-quart)"
  >
    <div class="flex min-w-0 flex-1 flex-col gap-1">
      <div class="flex items-baseline gap-2">
        <span class="truncate font-display text-xl font-medium tracking-tight text-ink dark:text-d-text">
          {{ item.name }}
        </span>
        <span v-if="item.unit" class="shrink-0 text-xs font-medium uppercase tracking-widest text-ink-faint dark:text-d-text-faint">
          {{ item.unit }}
        </span>
      </div>
      <div v-if="item.tags.length" class="flex flex-wrap gap-1.5">
        <span
          v-for="tag in item.tags"
          :key="tag.id"
          class="inline-block rounded-full border border-border bg-cream-dark px-2 py-0.5 text-[0.6875rem] font-medium tracking-wide text-ink-light dark:border-d-border dark:bg-d-surface-hover dark:text-d-text-secondary"
          :style="tag.color ? { backgroundColor: tag.color + '22', color: tag.color, borderColor: tag.color + '44' } : {}"
        >
          {{ tag.name }}
        </span>
      </div>
    </div>

    <div class="flex items-center gap-1">
      <button
        type="button"
        aria-label="Decrease quantity"
        class="flex size-11 cursor-pointer items-center justify-center rounded-lg border-1.5 border-border-dark bg-cream text-ink-light transition-[border-color,background-color,color,transform] duration-150 hover:border-ink-faint hover:bg-border hover:text-ink active:scale-93 focus-visible:ring-2 focus-visible:ring-terracotta/30 focus-visible:outline-none dark:border-d-border-light dark:bg-d-bg dark:text-d-text-secondary dark:hover:border-d-text-faint dark:hover:bg-d-surface-hover dark:hover:text-d-text dark:focus-visible:ring-d-terracotta/30"
        :class="item.quantity <= 1 ? 'hover:border-terracotta-light hover:bg-red-50 hover:text-terracotta dark:hover:border-d-terracotta dark:hover:bg-red-950 dark:hover:text-d-terracotta' : ''"
        style="transition-timing-function: var(--ease-out-quart)"
        @click="$emit('updateQuantity', item.quantity - 1)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4">
          <path fill-rule="evenodd" d="M4 10a.75.75 0 0 1 .75-.75h10.5a.75.75 0 0 1 0 1.5H4.75A.75.75 0 0 1 4 10Z" clip-rule="evenodd" />
        </svg>
      </button>

      <span
        class="w-12 text-center font-display text-2xl font-semibold tabular-nums text-ink dark:text-d-text"
        :class="{ 'qty-pulse': qtyPulsing }"
        @animationend="onPulseEnd"
      >
        {{ item.quantity }}
      </span>

      <button
        type="button"
        aria-label="Increase quantity"
        class="flex size-11 cursor-pointer items-center justify-center rounded-lg border-1.5 border-border-dark bg-cream text-ink-light transition-[border-color,background-color,color,transform] duration-150 hover:border-ink-faint hover:bg-border hover:text-ink active:scale-93 focus-visible:ring-2 focus-visible:ring-terracotta/30 focus-visible:outline-none dark:border-d-border-light dark:bg-d-bg dark:text-d-text-secondary dark:hover:border-d-text-faint dark:hover:bg-d-surface-hover dark:hover:text-d-text dark:focus-visible:ring-d-terracotta/30"
        style="transition-timing-function: var(--ease-out-quart)"
        @click="$emit('updateQuantity', item.quantity + 1)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4">
          <path d="M10.75 4.75a.75.75 0 0 0-1.5 0v4.5h-4.5a.75.75 0 0 0 0 1.5h4.5v4.5a.75.75 0 0 0 1.5 0v-4.5h4.5a.75.75 0 0 0 0-1.5h-4.5v-4.5Z" />
        </svg>
      </button>

      <Transition name="fade">
        <button
          v-if="item.quantity === 0"
          type="button"
          aria-label="Delete item"
          class="ml-2 flex size-11 cursor-pointer items-center justify-center rounded-lg border-1.5 border-terracotta-light bg-red-50 text-terracotta transition-[border-color,background-color,color,transform] duration-150 hover:border-terracotta hover:bg-terracotta hover:text-white active:scale-93 focus-visible:ring-2 focus-visible:ring-terracotta/40 focus-visible:outline-none dark:border-d-terracotta dark:bg-red-950 dark:text-d-terracotta dark:hover:bg-d-terracotta dark:hover:text-d-bg dark:focus-visible:ring-d-terracotta/40"
          style="transition-timing-function: var(--ease-out-quart)"
          @click="$emit('delete')"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4">
            <path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 0 0 6 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 1 0 .23 1.482l.149-.022.841 10.518A2.75 2.75 0 0 0 7.596 19h4.807a2.75 2.75 0 0 0 2.742-2.53l.841-10.52.149.023a.75.75 0 0 0 .23-1.482A41.03 41.03 0 0 0 14 4.193V3.75A2.75 2.75 0 0 0 11.25 1h-2.5ZM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4ZM8.58 7.72a.75.75 0 0 0-1.5.06l.3 7.5a.75.75 0 1 0 1.5-.06l-.3-7.5Zm4.34.06a.75.75 0 1 0-1.5-.06l-.3 7.5a.75.75 0 1 0 1.5.06l.3-7.5Z" clip-rule="evenodd" />
          </svg>
        </button>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active { transition: all 0.2s var(--ease-out-quart); }
.fade-leave-active { transition: all 0.15s var(--ease-out-quart); }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: scale(0.8); }
</style>
