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
    <div class="w-full h-full flex flex-col">
      <Fieldset legend="Transactions">
        <TransactionList :dataSource="'overview'" :autoExpand="false" />
      </Fieldset>
    </div>
  </div>
</template>
