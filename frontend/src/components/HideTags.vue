<script setup>
// Custom components
import HideList from "@/components/HideList.vue";

// Custom utils
import { getData } from "@/composables/api";

// Set-up
const { tagsWithArchived, loadTags } = getData();
</script>

<template>
  <HideList
    :items="tagsWithArchived"
    :loadFn="loadTags"
    itemID="tag"
    apiUrl="/api/update/archive/tag"
    toastName="Tag"
  >
    <template #default="{ item }">
      {{ item.tag_name }}
    </template>
  </HideList>
</template>
