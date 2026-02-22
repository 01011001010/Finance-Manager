<!-- TODO complete rework, primevue use, revisit onMounted or move to the level above (App.vue)-->
<script setup>
import { ref, onMounted } from "vue";

// Custom utils
import { getData } from "@/composables/api";

// Set-up
const { transactionOverview, loadOverview } = getData();

const loading = ref(true);

onMounted(async () => {
  loadOverview();
  loading.value = false;
});
</script>

<template>
  <div>
    <h1>Transactions</h1>
    <div v-if="loading">Loading…</div>
    <div v-else>
      <div
        v-for="tx in transactionOverview"
        :key="tx.id_t"
        style="margin-bottom: 1em"
      >
        <h2>{{ tx.title }}</h2>
        <div v-if="tx.subtitle">{{ tx.subtitle }}</div>
        <div>
          <em>{{ tx.tag }}</em>
        </div>
        <ul>
          <li v-for="d in tx.deltas" :key="d.id_t">
            {{ d.amount }} {{ d.currency }} —
            {{ d.account }}
            <span v-if="d.ts">({{ d.ts }})</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
