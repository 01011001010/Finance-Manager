<script setup>
import { ref } from "vue";
import Drawer from "primevue/drawer";
import Menubar from "primevue/menubar";
import Panel from "primevue/panel";
import ScrollPanel from "primevue/scrollpanel";

// Custom components
import NewTag from "@/components/NewTag.vue";
import NewAccount from "@/components/NewAccount.vue";
import HideAccounts from "@/components/HideAccounts.vue";
import HideTags from "@/components/HideTags.vue";
// import BulkUpload from "@/components/BulkUpload.vue";

// Drawer states
const showBulkDataPanel = ref(false);
const showTagPanel = ref(false);
const showAccountPanel = ref(false);

// Menu items
const setupItems = ref([
  {
    label: "Accounts",
    icon: "pi pi-wallet",
    command: async () => {
      showAccountPanel.value = true;
    },
  },
  {
    separator: true,
  },
  {
    label: "Tags",
    icon: "pi pi-tags",
    command: async () => {
      showTagPanel.value = true;
    },
  },
  {
    separator: true,
  },
  {
    label: "Bulk Import",
    icon: "pi pi-file-arrow-up",
    command: async () => {
      showBulkDataPanel.value = true;
    },
  },
]);
</script>

<template>
  <Teleport to="#secondary-menu-target">
    <Menubar :model="setupItems" class="border-none bg-transparent" />
  </Teleport>

  <Drawer
    v-model:visible="showAccountPanel"
    position="right"
    :blockScroll="true"
    class="w-full sm:w-96"
  >
    <template #container="{ closeCallback }">
      <div class="w-full h-full flex flex-col gap-4 p-4">
        <div class="flex-none">
          <Panel header="Add Accounts">
            <NewAccount />
          </Panel>
        </div>
        <div class="flex-1 min-h-0">
          <Panel
            header="Hide Accounts"
            class="h-full flex flex-col"
            :pt="{
              contentContainer: { class: 'flex-grow min-h-0' },
              content: { class: 'h-full' },
            }"
          >
            <HideAccounts />
          </Panel>
        </div>
      </div>
    </template>
  </Drawer>

  <Drawer
    v-model:visible="showTagPanel"
    position="right"
    :blockScroll="true"
    class="w-full sm:w-96"
  >
    <template #container="{ closeCallback }">
      <div class="w-full h-full flex flex-col gap-4 p-4">
        <div class="flex-none">
          <Panel header="Add Tags">
            <NewTag />
          </Panel>
        </div>
        <div class="flex-1 min-h-0">
          <Panel
            header="Hide Tags"
            class="h-full flex flex-col"
            :pt="{
              contentContainer: { class: 'flex-grow min-h-0' },
              content: { class: 'h-full' },
            }"
          >
            <HideTags />
          </Panel>
        </div>
      </div>
    </template>
  </Drawer>

  <Drawer
    v-model:visible="showBulkDataPanel"
    header="Bulk data import"
    position="right"
    :blockScroll="true"
    class="w-full sm:w-96"
  >
    <!-- <BulkUpload /> -->
  </Drawer>
</template>
