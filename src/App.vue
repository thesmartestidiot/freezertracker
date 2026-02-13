<script setup lang="ts">
import { computed, reactive } from "vue";
import RowComp from "@/components/RowComp.vue";
import AddItemModal from "@/components/AddItemModal.vue";

const rows = reactive([
  { id: 1, label: "Chuck Steak", quantity: 1 },
  { id: 2, label: "Ribeye", quantity: 2 },
  { id: 3, label: "T-Bone", quantity: 3 },
  { id: 4, label: "Sirloin", quantity: 4 },
  { id: 5, label: "Brisket", quantity: 5 },
  { id: 6, label: "Flank", quantity: 6 },
  { id: 7, label: "Skirt", quantity: 7 },
  { id: 8, label: "New Item", quantity: 1 },
]);

const sortedRows = computed(() => {
  return [...rows].sort((a, b) => a.label.localeCompare(b.label));
});

const updateQuantity = (id: number, quantity: number) => {
  const row = rows.find((r) => r.id === id);
  if (row) {
    row.quantity = Math.max(0, quantity);
  }
};

const addItem = (label: string) => {
  const newId = rows.length ? Math.max(...rows.map((r) => r.id)) + 1 : 1;
  rows.push({ id: newId, label, quantity: 0 });
};
</script>

<template>
  <div class="flex h-screen w-screen items-center justify-center bg-gray-900">
    <div class="w-full p-6 bg-gray-800 rounded-lg">
      <div class="space-y-4 h-64 overflow-y-auto">
        <RowComp
          v-for="row in sortedRows"
          :key="row.id"
          :row="row"
          @update:quantity="(value) => updateQuantity(row.id, value)"
        />
      </div>
      <AddItemModal @add-item="addItem" />
    </div>
  </div>
</template>
