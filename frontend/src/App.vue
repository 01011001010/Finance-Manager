<script setup>
import Toast from "primevue/toast";
import Menubar from "primevue/menubar";
import { ref } from "vue";

const menuItems = ref([
  {
    label: "Transactions",
    icon: "pi pi-list",
    route: "/",
  },
  {
    label: "Log",
    icon: "pi pi-plus-circle",
    route: "/log",
  },
]);
</script>

<template>
  <div class="card">
    <Menubar :model="menuItems">
      <template #start>
        <div class="flex items-center gap-2 mr-4">
          <i class="pi pi-chart-line text-primary text-2xl"></i>
          <span class="font-bold text-xl tracking-tight">Finance Manager</span>
        </div>
      </template>

      <template #item="{ item, props, hasSubmenu }">
        <router-link
          v-if="item.route"
          v-slot="{ href, navigate }"
          :to="item.route"
          custom
        >
          <a :href="href" v-bind="props.action" @click="navigate">
            <span :class="item.icon" />
            <span class="ml-2">{{ item.label }}</span>
          </a>
        </router-link>
        <a v-else :href="item.url" :target="item.target" v-bind="props.action">
          <span :class="item.icon" />
          <span class="ml-2">{{ item.label }}</span>
          <span v-if="hasSubmenu" class="pi pi-fw pi-angle-down ml-2" />
        </a>
      </template>

      <template #end>
        <div id="secondary-menu-target"></div>
      </template>
    </Menubar>

    <div class="p-4">
      <Toast position="bottom-left" />
      <router-view />
    </div>
  </div>
</template>
