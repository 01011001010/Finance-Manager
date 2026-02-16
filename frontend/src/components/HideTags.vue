<script setup>
import HideList from "./HideList.vue";

// Custom utils
import { dataLoaders } from "@/composables/api";

// Set-up
const { tagsWithArchived, loadTags } = dataLoaders();
</script>

<template>
  <HideList
    :items="tagsWithArchived"
    :loadFn="loadTags"
    itemID="tag"
    apiUrl="/api/archive/tag"
    toastName="Tag"
  >
    <template #default="{ item }">
      {{ item.tag_name }}
    </template>
  </HideList>
</template>
