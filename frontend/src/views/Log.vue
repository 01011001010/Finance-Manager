<!-- TODO
pinned transaction (and Overview.vue) should have different delta grouping and transaction order (backend change needed)

possibly allow during application setup to choose the default
  -> currency (new accounts)
  -> formatting
  -> ...

log list styling
  -> group if neighbouring are the same transaction??
  -> pinned transactions hide deltas into a rolldown (see PrimeVue Tree)
-->

<script setup>
import { onMounted } from "vue";
import Fieldset from "primevue/fieldset";

// Custom utils
import { getData } from "@/composables/api";

// Custom components
import NewDelta from "@/components/NewDelta.vue";
import DrawerMenuLog from "@/components/DrawerMenuLog.vue";
import TransactionList from "@/components/TransactionList.vue";

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

    <div class="w-full h-full flex flex-col">
      <Fieldset
        legend="Bookmarked Transactions"
        :toggleable="true"
        :collapsed="false"
      >
        <TransactionList :dataSource="'pinned'" :autoExpand="false" />
      </Fieldset>

      <Fieldset legend="Chronological Log">
        <TransactionList :dataSource="'chronological'" :autoExpand="true" />
      </Fieldset>
    </div>

    <div class="w-full sm:w-96">
      <div class="sticky top-2">
        <NewDelta />
      </div>
    </div>
  </div>
</template>
