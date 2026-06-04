<script setup>
// Custom components
import BulkZip from "./BulkZip.vue";
import BulkTransactions from "@/components/BulkTransactions.vue";
import BulkTags from "@/components/BulkTags.vue";
import BulkAccounts from "@/components/BulkAccounts.vue";
</script>

<template>
  <div class="flex flex-col gap-4">
    <BulkZip />
    <BulkTransactions />
    <BulkTags />
    <BulkAccounts />
  </div>
</template>
