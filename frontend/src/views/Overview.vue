<template>
  <div>
    <h1>Transactions</h1>
    <div v-if="loading">Loading…</div>
    <div v-else>
      <div v-for="tx in transactions" :key="tx.id" style="margin-bottom: 1em">
        <h2>{{ tx.title }}</h2>
        <div v-if="tx.subtitle">{{ tx.subtitle }}</div>
        <div>
          <em>{{ tx.tag }}</em>
        </div>
        <ul>
          <li v-for="d in tx.deltas" :key="d.id">
            {{ d.amount }} {{ d.currency }} —
            {{ d.account }}
            <span v-if="d.ts">({{ d.ts }})</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue";

const transactions = ref([]);
const loading = ref(true);

onMounted(async () => {
  const res = await fetch("/api/transactions");
  transactions.value = await res.json();
  loading.value = false;
});
</script>
