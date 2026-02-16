<script setup>
import HideList from "./HideList.vue";

// Custom utils
import { dataLoaders } from "@/composables/api";

// Set-up
const { accountsWithArchived, loadAccounts } = dataLoaders();
</script>

<template>
  <HideList
    :items="accountsWithArchived"
    :loadFn="loadAccounts"
    itemID="id_a"
    apiUrl="/api/archive/account"
    toastName="Account"
  >
    <template #default="{ item }">
      {{ item.account }}
      <span class="text-xs opacity-60">({{ item.currency }})</span>
    </template>
  </HideList>
</template>
