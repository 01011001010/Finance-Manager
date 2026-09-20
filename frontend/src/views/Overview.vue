<!-- TODO
     month dividers?

     solve expand of all transaction copies

     total per transaction

     revisit onMounted or move to the level above (App.vue)-->
<script setup>
import { onMounted } from "vue";
import Fieldset from "primevue/fieldset";

// Custom components
import TransactionList from "@/components/TransactionList.vue";

// Custom utils
import { getData } from "@/composables/api";

// Set-up
const { loadOverview } = getData();

onMounted(async () => {
  loadOverview();
});
</script>

<template>
  <div class="w-full h-full flex flex-row gap-4">
    <div class="w-full h-full flex flex-col flex-1 min-h-0 gap-4">
      <Fieldset
        legend="Transactions"
        :pt="{
          root: { class: 'flex flex-col flex-1 min-h-0' },
          contentContainer: { class: 'flex flex-col flex-1 min-h-0' },
          contentWrapper: { class: 'flex flex-col flex-1 min-h-0 h-full' },
          content: { class: 'flex flex-col flex-1 min-h-0 h-full p-0' },
        }"
      >
        <div class="flex-1 min-h-0 h-full flex flex-col">
          <TransactionList :dataSource="'overview'" :autoExpand="false" />
        </div>
      </Fieldset>
    </div>
  </div>
</template>
