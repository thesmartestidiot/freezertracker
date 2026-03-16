<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import RowComp from '@/components/RowComp.vue'
import AddItemModal from '@/components/AddItemModal.vue'
import type { Item, Tag } from '@/types'
import { fetchItems, fetchTags, createItem, updateItem, deleteItem } from '@/api'

const items = ref<Item[]>([])
const tags = ref<Tag[]>([])
const activeTag = ref<string | null>(null)
const loaded = ref(false)
const initialLoad = ref(true)

// Dark mode
const isDark = ref(
  localStorage.getItem('theme') === 'dark' ||
  (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches),
)

function applyTheme() {
  document.documentElement.classList.toggle('dark', isDark.value)
}
function toggleTheme() {
  isDark.value = !isDark.value
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  applyTheme()
}

// View mode
const urlMode = new URLSearchParams(window.location.search).get('mode')
const modeOverride = ref<'desktop' | 'kiosk' | null>(
  urlMode === 'desktop' || urlMode === 'kiosk' ? urlMode : null,
)
const windowWidth = ref(window.innerWidth)
function onResize() { windowWidth.value = window.innerWidth }

const mode = computed(() => {
  if (modeOverride.value) return modeOverride.value
  return windowWidth.value >= 1024 ? 'desktop' : 'kiosk'
})
const isKiosk = computed(() => mode.value === 'kiosk')

function toggleMode() {
  modeOverride.value = mode.value === 'kiosk' ? 'desktop' : 'kiosk'
}

// Personality
const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return 'Late night inventory'
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  if (h < 21) return 'Good evening'
  return 'Late night inventory'
})

const stockStatus = computed(() => {
  const count = items.value.length
  if (count === 0) return null
  if (count <= 3) return 'Running low'
  if (count <= 8) return 'Looking good'
  return 'Well stocked'
})

const emptyMessages = [
  { line1: 'Your freezer awaits', line2: 'Time to stock up on the good stuff' },
  { line1: 'Nothing on ice', line2: 'A blank canvas for your next grocery run' },
  { line1: 'Fresh start', line2: 'Add your first item to get going' },
  { line1: 'All clear', line2: 'The freezer is ready for new arrivals' },
]

const emptyTagMessages = [
  'Nothing here with that tag',
  'No matches for this filter',
  'Try a different tag',
]

function pickRandom<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]!
}

const currentEmptyMessage = ref(pickRandom(emptyMessages))
const currentEmptyTagMessage = ref(pickRandom(emptyTagMessages))

// Data
const sortedItems = computed(() =>
  [...items.value].sort((a, b) => a.name.localeCompare(b.name)),
)
const filteredItems = computed(() => {
  if (!activeTag.value) return sortedItems.value
  return sortedItems.value.filter((item) =>
    item.tags.some((t) => t.name.toLowerCase() === activeTag.value!.toLowerCase()),
  )
})

function staggerDelay(index: number): string {
  if (!initialLoad.value) return '0ms'
  return `${index * 50}ms`
}

async function loadData() {
  const [itemData, tagData] = await Promise.all([fetchItems(), fetchTags()])
  items.value = itemData
  tags.value = tagData
  loaded.value = true
  // Clear initial load flag after entrance animations complete
  if (initialLoad.value) {
    setTimeout(() => { initialLoad.value = false }, itemData.length * 50 + 500)
  }
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

onMounted(() => {
  applyTheme()
  loadData()
  window.addEventListener('resize', onResize)
})
onUnmounted(() => {
  window.removeEventListener('resize', onResize)
})
</script>

<template>
  <!-- ==================== KIOSK VIEW ==================== -->
  <div v-if="isKiosk" class="flex h-dvh w-full flex-col overflow-hidden bg-cream dark:bg-d-bg">
    <!-- Top bar -->
    <header class="flex shrink-0 items-center justify-between border-b border-border px-5 py-4 dark:border-d-border">
      <div class="flex items-center gap-4">
        <h1 class="font-display text-3xl font-semibold tracking-tight text-ink dark:text-d-text">Freezer</h1>
        <span class="text-base text-ink-faint dark:text-d-text-faint">
          {{ filteredItems.length }}<template v-if="stockStatus && !activeTag"> &middot; {{ stockStatus }}</template>
        </span>
      </div>
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="flex size-9 cursor-pointer items-center justify-center rounded-lg border-1.5 border-border-dark text-ink-faint transition-colors duration-150 hover:text-ink focus-visible:ring-2 focus-visible:ring-terracotta/30 focus-visible:outline-none dark:border-d-border-light dark:text-d-text-faint dark:hover:text-d-text dark:focus-visible:ring-d-terracotta/30"
          :title="isDark ? 'Switch to light theme' : 'Switch to dark theme'"
          :aria-label="isDark ? 'Switch to light theme' : 'Switch to dark theme'"
          @click="toggleTheme"
        >
          <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4">
            <path d="M10 2a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0v-1.5A.75.75 0 0 1 10 2ZM10 15a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0v-1.5A.75.75 0 0 1 10 15ZM10 7a3 3 0 1 0 0 6 3 3 0 0 0 0-6ZM15.657 5.404a.75.75 0 1 0-1.06-1.06l-1.061 1.06a.75.75 0 0 0 1.06 1.06l1.06-1.06ZM6.464 14.596a.75.75 0 1 0-1.06-1.06l-1.06 1.06a.75.75 0 0 0 1.06 1.06l1.06-1.06ZM18 10a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1 0-1.5h1.5A.75.75 0 0 1 18 10ZM5 10a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1 0-1.5h1.5A.75.75 0 0 1 5 10ZM14.596 15.657a.75.75 0 0 0 1.06-1.06l-1.06-1.061a.75.75 0 1 0-1.06 1.06l1.06 1.06ZM5.404 6.464a.75.75 0 0 0 1.06-1.06l-1.06-1.06a.75.75 0 1 0-1.06 1.06l1.06 1.06Z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4">
            <path fill-rule="evenodd" d="M7.455 2.004a.75.75 0 0 1 .26.77 7 7 0 0 0 9.958 7.967.75.75 0 0 1 1.067.853A8.5 8.5 0 1 1 6.647 1.921a.75.75 0 0 1 .808.083Z" clip-rule="evenodd" />
          </svg>
        </button>
        <button
          type="button"
          class="flex size-9 cursor-pointer items-center justify-center rounded-lg border-1.5 border-border-dark text-ink-faint transition-colors duration-150 hover:text-ink focus-visible:ring-2 focus-visible:ring-terracotta/30 focus-visible:outline-none dark:border-d-border-light dark:text-d-text-faint dark:hover:text-d-text dark:focus-visible:ring-d-terracotta/30"
          title="Switch to desktop view"
          aria-label="Switch to desktop view"
          @click="toggleMode"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4">
            <path fill-rule="evenodd" d="M2 4.25A2.25 2.25 0 0 1 4.25 2h11.5A2.25 2.25 0 0 1 18 4.25v8.5A2.25 2.25 0 0 1 15.75 15h-3.105a3.501 3.501 0 0 1 1.1 1.677A.75.75 0 0 1 13.026 17H6.974a.75.75 0 0 1-.719-.538 3.501 3.501 0 0 1 1.1-1.677H4.25A2.25 2.25 0 0 1 2 12.75v-8.5Z" clip-rule="evenodd" />
          </svg>
        </button>
        <AddItemModal :tags="tags" :kiosk="true" @add-item="handleAddItem" />
      </div>
    </header>

    <!-- Tag filters -->
    <nav v-if="tags.length" class="hide-scrollbar flex shrink-0 gap-2 overflow-x-auto border-b border-border px-5 py-3 dark:border-d-border">
      <button
        v-for="tag in tags"
        :key="tag.id"
        type="button"
        class="shrink-0 cursor-pointer rounded-full border-1.5 px-5 py-2 text-[0.9375rem] font-medium tracking-wide transition-[border-color,background-color,color,transform] duration-200 active:scale-95"
        style="transition-timing-function: var(--ease-out-quart)"
        :class="
          activeTag === tag.name
            ? 'border-ink bg-ink text-cream dark:border-d-text dark:bg-d-text dark:text-d-bg'
            : 'border-border-dark text-ink-light dark:border-d-border-light dark:text-d-text-secondary'
        "
        @click="toggleTag(tag.name)"
      >
        {{ tag.name }}
      </button>
    </nav>

    <!-- Items -->
    <main class="hide-scrollbar min-h-0 flex-1 overflow-y-auto p-3">
      <TransitionGroup name="list" tag="div" class="space-y-2">
        <div
          v-for="(item, index) in filteredItems"
          :key="item.id"
          :class="{ 'stagger-in': initialLoad }"
          :style="initialLoad ? { animationDelay: staggerDelay(index) } : {}"
        >
          <RowComp
            :item="item"
            :kiosk="true"
            @update-quantity="handleUpdateQuantity(item.id, $event)"
            @delete="handleDeleteItem(item.id)"
          />
        </div>
      </TransitionGroup>

      <div v-if="loaded && filteredItems.length === 0" class="flex h-full flex-col items-center justify-center gap-2">
        <div class="breathe font-display text-5xl text-ink-faint dark:text-d-text-faint">~</div>
        <p class="text-xl text-ink-light dark:text-d-text-secondary">
          {{ activeTag ? currentEmptyTagMessage : currentEmptyMessage.line1 }}
        </p>
        <p v-if="!activeTag" class="text-sm text-ink-faint dark:text-d-text-faint">
          {{ currentEmptyMessage.line2 }}
        </p>
      </div>
    </main>
  </div>

  <!-- ==================== DESKTOP VIEW ==================== -->
  <div v-else class="flex h-screen w-full bg-cream dark:bg-d-bg">
    <!-- Sidebar -->
    <aside class="flex w-[17rem] shrink-0 flex-col overflow-y-auto border-r border-border bg-surface p-6 dark:border-d-border dark:bg-d-surface">
      <!-- Brand -->
      <div class="mb-8">
        <h1 class="font-display text-3xl font-semibold tracking-tight text-ink dark:text-d-text">Freezer</h1>
        <p class="mt-1 text-sm text-ink-light dark:text-d-text-secondary">{{ greeting }}</p>
      </div>

      <!-- Tags -->
      <div class="min-h-0 flex-1">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-xs font-semibold uppercase tracking-widest text-ink-faint dark:text-d-text-faint">Tags</h2>
          <button
            v-if="activeTag"
            type="button"
            class="cursor-pointer text-xs text-terracotta transition-colors duration-150 hover:text-terracotta-dark focus-visible:outline-none focus-visible:underline dark:text-d-terracotta dark:hover:text-d-terracotta-hover"
            @click="activeTag = null"
          >
            Clear
          </button>
        </div>
        <div class="flex flex-col gap-1">
          <button
            v-for="tag in tags"
            :key="tag.id"
            type="button"
            class="flex w-full cursor-pointer items-center gap-2.5 rounded-lg border-0 bg-transparent px-3 py-2 text-left text-sm transition-[background-color,color] duration-200"
            style="transition-timing-function: var(--ease-out-quart)"
            :class="
              activeTag === tag.name
                ? 'bg-ink text-cream dark:bg-d-text dark:text-d-bg'
                : 'text-ink-light hover:bg-cream hover:text-ink dark:text-d-text-secondary dark:hover:bg-d-surface-hover dark:hover:text-d-text'
            "
            @click="toggleTag(tag.name)"
          >
            <span
              class="size-2 shrink-0 rounded-full transition-opacity duration-200"
              :class="activeTag === tag.name ? 'opacity-50' : ''"
              :style="{ backgroundColor: activeTag === tag.name ? (isDark ? 'var(--color-d-bg)' : 'var(--color-cream)') : (tag.color || 'var(--color-ink-faint)') }"
            />
            {{ tag.name }}
          </button>
        </div>
      </div>

      <!-- Footer -->
      <div class="mt-auto border-t border-border pt-6 dark:border-d-border">
        <div class="mb-4 flex items-center justify-between">
          <span class="text-sm text-ink-light dark:text-d-text-secondary">
            {{ filteredItems.length }} item{{ filteredItems.length !== 1 ? 's' : '' }}<template v-if="stockStatus && !activeTag"> &middot; {{ stockStatus }}</template>
          </span>
          <div class="flex items-center gap-1.5">
            <button
              type="button"
              class="flex size-8 cursor-pointer items-center justify-center rounded-lg border-1.5 border-border-dark text-ink-faint transition-[border-color,background-color,color] duration-150 hover:border-ink-faint hover:bg-cream-dark hover:text-ink focus-visible:ring-2 focus-visible:ring-terracotta/30 focus-visible:outline-none dark:border-d-border-light dark:text-d-text-faint dark:hover:border-d-text-faint dark:hover:bg-d-surface-hover dark:hover:text-d-text dark:focus-visible:ring-d-terracotta/30"
              :title="isDark ? 'Switch to light theme' : 'Switch to dark theme'"
              :aria-label="isDark ? 'Switch to light theme' : 'Switch to dark theme'"
              @click="toggleTheme"
            >
              <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-3.5">
                <path d="M10 2a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0v-1.5A.75.75 0 0 1 10 2ZM10 15a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0v-1.5A.75.75 0 0 1 10 15ZM10 7a3 3 0 1 0 0 6 3 3 0 0 0 0-6ZM15.657 5.404a.75.75 0 1 0-1.06-1.06l-1.061 1.06a.75.75 0 0 0 1.06 1.06l1.06-1.06ZM6.464 14.596a.75.75 0 1 0-1.06-1.06l-1.06 1.06a.75.75 0 0 0 1.06 1.06l1.06-1.06ZM18 10a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1 0-1.5h1.5A.75.75 0 0 1 18 10ZM5 10a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1 0-1.5h1.5A.75.75 0 0 1 5 10ZM14.596 15.657a.75.75 0 0 0 1.06-1.06l-1.06-1.061a.75.75 0 1 0-1.06 1.06l1.06 1.06ZM5.404 6.464a.75.75 0 0 0 1.06-1.06l-1.06-1.06a.75.75 0 1 0-1.06 1.06l1.06 1.06Z" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-3.5">
                <path fill-rule="evenodd" d="M7.455 2.004a.75.75 0 0 1 .26.77 7 7 0 0 0 9.958 7.967.75.75 0 0 1 1.067.853A8.5 8.5 0 1 1 6.647 1.921a.75.75 0 0 1 .808.083Z" clip-rule="evenodd" />
              </svg>
            </button>
            <button
              type="button"
              class="flex size-8 cursor-pointer items-center justify-center rounded-lg border-1.5 border-border-dark text-ink-faint transition-[border-color,background-color,color] duration-150 hover:border-ink-faint hover:bg-cream-dark hover:text-ink focus-visible:ring-2 focus-visible:ring-terracotta/30 focus-visible:outline-none dark:border-d-border-light dark:text-d-text-faint dark:hover:border-d-text-faint dark:hover:bg-d-surface-hover dark:hover:text-d-text dark:focus-visible:ring-d-terracotta/30"
              title="Switch to kiosk view"
              aria-label="Switch to kiosk view"
              @click="toggleMode"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-3.5">
                <path fill-rule="evenodd" d="M3.75 4.5a.75.75 0 0 1 .75-.75h11a.75.75 0 0 1 .75.75v7.5a.75.75 0 0 1-.75.75h-11a.75.75 0 0 1-.75-.75v-7.5Zm.75 8.75a.75.75 0 0 0 0 1.5h11a.75.75 0 0 0 0-1.5h-11Z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
        <AddItemModal :tags="tags" :kiosk="false" @add-item="handleAddItem" />
      </div>
    </aside>

    <!-- Main content -->
    <main class="min-w-0 flex-1 overflow-y-auto">
      <div class="mx-auto max-w-3xl px-10 py-8">
        <div class="mb-6 flex items-baseline justify-between">
          <h2 class="font-display text-2xl font-medium text-ink dark:text-d-text">
            {{ activeTag ? activeTag : 'All Items' }}
          </h2>
          <span class="text-sm text-ink-faint dark:text-d-text-faint">sorted A&ndash;Z</span>
        </div>

        <TransitionGroup name="list" tag="div" class="space-y-3">
          <div
            v-for="(item, index) in filteredItems"
            :key="item.id"
            :class="{ 'stagger-in': initialLoad }"
            :style="initialLoad ? { animationDelay: staggerDelay(index) } : {}"
          >
            <RowComp
              :item="item"
              :kiosk="false"
              @update-quantity="handleUpdateQuantity(item.id, $event)"
              @delete="handleDeleteItem(item.id)"
            />
          </div>
        </TransitionGroup>

        <div
          v-if="loaded && filteredItems.length === 0"
          class="flex flex-col items-center justify-center py-24 text-center"
        >
          <div class="breathe font-display text-6xl text-ink-faint dark:text-d-text-faint">~</div>
          <p class="mt-3 text-lg text-ink-light dark:text-d-text-secondary">
            {{ activeTag ? currentEmptyTagMessage : currentEmptyMessage.line1 }}
          </p>
          <p class="mt-1 text-sm text-ink-faint dark:text-d-text-faint">
            {{ activeTag ? 'Try a different filter' : currentEmptyMessage.line2 }}
          </p>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* List transitions - use ease-out-quart */
.list-enter-active { transition: all 0.35s var(--ease-out-quart); }
.list-leave-active { transition: all 0.25s var(--ease-out-quart); }
.list-enter-from { opacity: 0; transform: translateY(-8px); }
.list-leave-to { opacity: 0; transform: translateX(20px); }
.list-move { transition: transform 0.3s var(--ease-out-quart); }
</style>
