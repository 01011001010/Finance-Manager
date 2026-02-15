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
import { ref, onMounted, watch } from "vue";
import Drawer from "primevue/drawer";
import Menubar from "primevue/menubar";
import Fieldset from "primevue/fieldset";

// Custom components
import NewTag from "@/components/NewTag.vue";
import NewAccount from "@/components/NewAccount.vue";
import NewDelta from "../components/NewDelta.vue";

// Custom utils
import { customToaster } from "@/composables/customToast";
import { dataLoaders, apiPost } from "@/composables/api";
import { transactionSelector } from "@/composables/deltaLog";

// Set-up
const { successToast, neutralToast, errorToast } = customToaster();
const {
  transactions,
  accounts,
  tags,
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

// Sliding side-panels
const showTagAddPanel = ref(false);
const showAccountPanel = ref(false);

// View-specific menu items // TODO separate with the menu
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
        label: "Remove",
        icon: "pi pi-minus",
        command: () => {
          // showTagDeletePanel.value = true;  // TODO
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
          showAccountPanel.value = true;
        },
      },
      {
        label: "Hide",
        icon: "pi pi-eye-slash",
        command: () => {
          // showAccountHidePanel.value = true;  // TODO
        },
      },
    ],
  },
]);

onMounted(() => {
  loadTransactions();
  loadAccounts();
  loadTags();
  loadPinned();
});
</script>

<template>
  <div class="w-full flex flex-row gap-4">
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
      v-model:visible="showAccountPanel"
      header="Add Accounts"
      position="right"
      class="w-full sm:w-96"
    >
      <NewAccount />
    </Drawer>

    <div class="w-full">
      <Fieldset legend="Pined Transactions">
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
                  <button
                    @click="unpinTransaction(t.id)"
                    title="Unpin transaction"
                  >
                    ❌
                  </button>
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
      <Fieldset legend="Transaction deltas in chronological order">
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
                  <button
                    v-if="!isPinned(t.id)"
                    @click="pinTransaction(t.id)"
                    title="Pin transaction"
                  >
                    📌
                  </button>

                  <button
                    v-else
                    @click="unpinTransaction(t.id)"
                    title="Unpin transaction"
                  >
                    ❌
                  </button>
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
