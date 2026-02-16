<script setup>
import { ref } from "vue";
import Drawer from "primevue/drawer";
import Menubar from "primevue/menubar";

// Custom components
import NewTag from "@/components/NewTag.vue";
import NewAccount from "@/components/NewAccount.vue";
import HideAccounts from "@/components/HideAccounts.vue";
import HideTags from "@/components/HideTags.vue";

// Drawer states
const showTagAddPanel = ref(false);
const showAccountAddPanel = ref(false);
const showTagHidePanel = ref(false);
const showAccountHidePanel = ref(false);

// Menu items
const setupItems = ref([
  {
    label: "Tags",
    icon: "pi pi-tags",
    items: [
      {
        label: "Add",
        icon: "pi pi-plus",
        command: async () => {
          showTagAddPanel.value = true;
        },
      },
      {
        label: "Hide",
        icon: "pi pi-eye-slash",
        command: () => {
          showTagHidePanel.value = true;
        },
      },
    ],
  },
  {
    separator: true,
  },
  {
    label: "Accounts",
    icon: "pi pi-wallet",
    items: [
      {
        label: "Add",
        icon: "pi pi-plus",
        command: async () => {
          showAccountAddPanel.value = true;
        },
      },
      {
        label: "Hide",
        icon: "pi pi-eye-slash",
        command: () => {
          showAccountHidePanel.value = true;
        },
      },
    ],
  },
]);
</script>

<template>
  <Teleport to="#secondary-menu-target">
    <Menubar :model="setupItems" class="border-none bg-transparent" />
  </Teleport>

  <Drawer
    v-model:visible="showTagAddPanel"
    header="Add Tags"
    position="right"
    class="w-full sm:w-96"
  >
    <NewTag />
  </Drawer>

  <Drawer
    v-model:visible="showAccountAddPanel"
    header="Add Accounts"
    position="right"
    class="w-full sm:w-96"
  >
    <NewAccount />
  </Drawer>

  <Drawer
    v-model:visible="showAccountHidePanel"
    header="Hide Accounts"
    position="right"
    class="w-full sm:w-96"
  >
    <HideAccounts />
  </Drawer>

  <Drawer
    v-model:visible="showTagHidePanel"
    header="Hide Tags"
    position="right"
    class="w-full sm:w-96"
  >
    <HideTags />
  </Drawer>
</template>
