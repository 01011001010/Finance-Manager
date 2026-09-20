<!-- TODO
possibly allow during application setup to choose the default
  -> currency (new accounts)
  -> formatting
  -> ...
-->
<!-- FIX ME
     ISSUE: quite slow load times (even row selection takes time)
     HYPOTHESIS: frontend (confirm with backend load time experiment)
     NEXT STEPS: investigate cause, potentially solve by streamed loading / showing partial data
-->
<!-- FIX ME
     ISSUE: <NewDelta /> stickiness stops working when scrolling past Chronological Log's top
-->

<script setup>
import { ref, onMounted } from "vue";
import Fieldset from "primevue/fieldset";
import Button from "primevue/button";

// Custom utils
import { getData } from "@/composables/api";

// Custom components
import NewDelta from "@/components/NewDelta.vue";
import DrawerMenuLog from "@/components/DrawerMenuLog.vue";
import TransactionList from "@/components/TransactionList.vue";

// Active Tab State
const activeTab = ref("pinned");

// Set-up
const { loadDeltas, loadAccounts, loadTags, loadPinned } = getData();

onMounted(() => {
  loadDeltas();
  loadAccounts();
  loadTags();
  loadPinned();
});
</script>

<template>
  <div class="w-full h-full flex flex-row gap-4">
    <DrawerMenuLog />

    <div class="w-full h-full flex flex-col flex-1 min-h-0 gap-4">
      <Fieldset
        :pt="{
          root: { class: 'flex flex-col flex-1 min-h-0' },
          contentContainer: { class: 'flex flex-col flex-1 min-h-0' },
          contentWrapper: { class: 'flex flex-col flex-1 min-h-0 h-full' },
          content: { class: 'flex flex-col flex-1 min-h-0 h-full p-0' },
        }"
      >
        <!-- Tabbed Legend -->
        <template #legend>
          <div class="flex items-center gap-1.5 -my-1">
            <button
              type="button"
              @click="activeTab = 'pinned'"
              :class="[
                'px-2.5 py-0.5 text-sm font-semibold rounded-md transition-all cursor-pointer select-none',
                activeTab === 'pinned'
                  ? 'border border-[var(--p-content-border-color)] bg-[var(--p-surface-0)] text-[var(--p-fieldset-legend-color,#000)] shadow-2xs'
                  : 'border border-transparent text-[var(--p-text-muted-color)] hover:text-[var(--p-fieldset-legend-color,#000)]',
              ]"
            >
              Bookmarked Transactions
            </button>
            <button
              type="button"
              @click="activeTab = 'chronological'"
              :class="[
                'px-2.5 py-0.5 text-sm font-semibold rounded-md transition-all cursor-pointer select-none',
                activeTab === 'chronological'
                  ? 'border border-[var(--p-content-border-color)] bg-[var(--p-surface-0)] text-[var(--p-fieldset-legend-color,#000)] shadow-2xs'
                  : 'border border-transparent text-[var(--p-text-muted-color)] hover:text-[var(--p-fieldset-legend-color,#000)]',
              ]"
            >
              Chronological Log
            </button>
          </div>
        </template>

        <!-- Bookmarked Transactions Tab -->
        <div
          v-show="activeTab === 'pinned'"
          class="flex-1 min-h-0 h-full flex flex-col"
        >
          <TransactionList :dataSource="'pinned'" :autoExpand="false" />
        </div>

        <!-- Chronological Log Tab -->
        <div
          v-show="activeTab === 'chronological'"
          class="flex-1 min-h-0 h-full flex flex-col"
        >
          <TransactionList :dataSource="'chronological'" :autoExpand="true" />
        </div>
      </Fieldset>
    </div>

    <div class="w-full sm:w-96">
      <div class="sticky top-2">
        <NewDelta />
      </div>
    </div>
  </div>
</template>
