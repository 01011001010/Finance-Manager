<!-- TODO
tag and account management
-> account hiding
-> tag hiding

possibly allow during application setup to choose the default currency (new accounts) and other default choices anf formatting


log list styling
-> group if neighbouring are the same transaction??
-> pinned transactions hide deltas into a rolldown (see PrimeVue Tree)
-->

<script setup>
import { onMounted } from "vue";
import Fieldset from "primevue/fieldset";
import Button from "primevue/button";

// Custom components
import NewDelta from "@/components/NewDelta.vue";
import DrawerMenuLog from "@/components/DrawerMenuLog.vue";

// Custom utils
import { customToaster } from "@/composables/customToast";
import { dataLoaders, apiPost } from "@/composables/api";
import { transactionSelector } from "@/composables/deltaLog";

// Set-up
const { successToast, neutralToast, errorToast } = customToaster();
const {
  transactions,
  pinnedId_t,
  pinnedTransactions,
  loadTransactions,
  loadAccounts,
  loadTags,
  loadPinned,
} = dataLoaders();
const { post } = apiPost();
const { clearSelection, selectedTransaction } = transactionSelector();

// Pinned transactions  // TODO separate with pinned-list components
const isPinned = (id) => pinnedId_t.value.includes(id);
const pinTransaction = async (id) => {
  // TODO, decide if frontend or backend should check this condition (-> database with unique, and HTTPS error when duplicate (like duplicate tag creation))
  if (!pinnedId_t.value.includes(id)) {
    const url = "/api/transactions/pin";
    const payload = JSON.stringify({ id_t: id });
    const response = await post(url, payload);
    console.log(response); // DEV
    if (response.ok) {
      console.log("ok Toast"); // DEV
      neutralToast("Transaction pinned");
      await loadPinned();
    } else {
      console.log("something went wrong Toast"); // DEV
      errorToast("The transaction could not be pinned");
    }
  }
};

const unpinTransaction = async (id) => {
  const url = "/api/transactions/unpin";
  const payload = JSON.stringify({ id_t: id });
  const response = await post(url, payload);
  console.log(response); // DEV
  if (response.ok) {
    console.log("ok Toast"); // DEV
    neutralToast("Transaction unpinned");
    await loadPinned();
  } else {
    console.log("something went wrong Toast"); // DEV
    errorToast("The transaction could not be unpinned");
  }
};

onMounted(() => {
  loadTransactions();
  loadAccounts();
  loadTags();
  loadPinned();
});
</script>

<template>
  <div class="w-full flex flex-row gap-4">
    <DrawerMenuLog />

    <div class="w-full">
      <Fieldset
        legend="Pined Transactions"
        :toggleable="true"
        :collapsed="false"
      >
        <button @click="clearSelection">Clear selected transaction</button>
        <table>
          <thead>
            <tr>
              <th>Select</th>
              <th>Pin</th>
              <th>Title</th>
              <th>Subtitle</th>
              <th>Amount</th>
              <th>Account</th>
              <th>Tag</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="t in pinnedTransactions" :key="t.id">
              <tr v-for="(d, idx) in t.deltas" :key="d.id">
                <td>
                  <input
                    type="radio"
                    name="t_select"
                    :value="t.id"
                    v-model="selectedTransaction"
                  />
                </td>
                <td>
                  <Button
                    icon="pi pi-times"
                    severity="secondary"
                    variant="text"
                    rounded
                    size="small"
                    @click="unpinTransaction(t.id)"
                  />
                </td>
                <td>{{ t.title }}</td>
                <td>{{ d.subtitle }}</td>
                <td>{{ d.amount }}</td>
                <td>{{ d.account }} ({{ d.currency }})</td>
                <td>{{ d.tag }}</td>
                <td>{{ d.ts }}</td>
              </tr>
            </template>
          </tbody>
        </table>
      </Fieldset>

      <Fieldset legend="Chronological log">
        <h2>Existing Transactions</h2>
        <button @click="clearSelection">Clear selected transaction</button>
        <table>
          <thead>
            <tr>
              <th>Select</th>
              <th>Pin</th>
              <th>Title</th>
              <th>Subtitle</th>
              <th>Amount</th>
              <th>Account</th>
              <th>Tag</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="t in transactions" :key="t.id">
              <tr v-for="(d, idx) in t.deltas" :key="d.id">
                <td>
                  <input
                    type="radio"
                    name="t_select"
                    :value="t.id"
                    v-model="selectedTransaction"
                  />
                </td>
                <td>
                  <Button
                    v-if="!isPinned(t.id)"
                    icon="pi pi-thumbtack"
                    severity="secondary"
                    variant="text"
                    rounded
                    size="small"
                    @click="pinTransaction(t.id)"
                  />

                  <Button
                    v-else
                    icon="pi pi-times"
                    severity="secondary"
                    variant="text"
                    rounded
                    size="small"
                    @click="unpinTransaction(t.id)"
                  />
                </td>
                <td>{{ t.title }}</td>
                <td>{{ d.subtitle }}</td>
                <td>{{ d.amount }}</td>
                <td>{{ d.account }} ({{ d.currency }})</td>
                <td>{{ d.tag }}</td>
                <td>{{ d.ts }}</td>
              </tr>
            </template>
          </tbody>
        </table>
      </Fieldset>
    </div>

    <div class="w-full sm:w-96">
      <Fieldset
        :legend="
          selectedTransaction ? 'Add to a Transaction' : 'New Transaction'
        "
      >
        <NewDelta />
      </Fieldset>
    </div>
  </div>
</template>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th,
td {
  border: 1px solid #7c7c7c;
  padding: 6px;
  text-align: left;
}

th {
  background: #a6a6a6;
}
</style>
