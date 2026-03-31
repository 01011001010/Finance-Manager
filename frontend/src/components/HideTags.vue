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
    apiUrl="/api/finance/tags/archive"
    toastName="Tag"
  >
    <template #default="{ item }">
      <div class="flex items-center gap-1">
        <span>{{ item.tag_name }}</span>
        <span v-if="item.parent_name != ''" class="text-xs opacity-60">
          ({{ item.parent_name }})
        </span>
      </div>
    </template>
  </HideList>
</template>
