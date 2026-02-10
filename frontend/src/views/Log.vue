<!-- TODO
transition to PrimeVue

tag and account management
-> account addition
-> account hiding
-> tag hiding

data validation on submit

styling
-> group if neighbouring are the same transaction??
-> pinned transactions hide deltas into a rolldown (see PrimeVue Tree)
-->

<script setup>
import { ref, onMounted, watch } from "vue";
import Drawer from "primevue/drawer";
import Menubar from "primevue/menubar";
import DatePicker from "primevue/datepicker";
import { customToaster } from "@/composables/customToast";
import { dataLoaders, apiPost } from "@/composables/api";

import NewTag from "@/components/NewTag.vue";

// const vFocustrap = FocusTrap;

// Toast
const { successToast, neutralToast, errorToast } = customToaster();

// Data loading
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

// API POST
const { post } = apiPost();

// Add transaction delta form  // TODO move to a separate component (and transition to PrimeVue)
const selectedTransaction = ref(null);
const clearSelection = () => {
  selectedTransaction.value = null;
};

let stashedTitle = null;
watch(selectedTransaction, (newId) => {
  if (newId === null) {
    form.value.title = stashedTitle;
    stashedTitle = null;
    return;
  }
  if (stashedTitle === null) {
    stashedTitle = form.value.title;
  }
  const transaction = transactions.value.find((t) => t.id === newId);
  if (!transaction) return;
  form.value.title = transaction.title;
});

const emptyForm = () => ({
  title: "",
  delta: {
    ts: new Date(),
    subtitle: "",
    amount: null,
    id_a: null,
    tag: null,
  },
});
const form = ref(emptyForm());
const resetForm = () => {
  form.value = emptyForm();
};

const submitAddTransaction = async () => {
  const url = selectedTransaction.value
    ? "/api/transactions/existing"
    : "/api/transactions/new";
  const delta = { ...form.value.delta, ts: form.value.delta.ts.toISOString() };
  const payload = JSON.stringify(
    selectedTransaction.value
      ? {
          id_t: selectedTransaction.value,
          delta,
        }
      : { ...form.value, delta },
  );
  console.log(payload); // DEV
  const response = await post(url, payload);
  console.log(response); // DEV
  if (response.ok) {
    console.log("ok Toast"); // DEV
    successToast("Transaction added");
    resetForm();
    await loadTransactions();
  } else {
    console.log("something went wrong Toast"); // DEV
    errorToast("Transaction could not be added");
  }
};

// Account form  // TODO move to a separate component (and transition to PrimeVue)
const newAccount = ref({
  name: "",
  currency: "",
  balance: "",
  ts: new Date(),
});

const submitNewAccount = async () => {
  const url = "/api/add/account"; // TODO implement
  const payload = JSON.stringify({
    ...newAccount.value,
    ts: newAccount.value.ts.toISOString(),
  });
  const response = await post(url, payload);
  console.log(response); // DEV
  if (response.ok) {
    console.log("ok Toast"); // DEV
    successToast(
      `Account '${newTag.value.name} (${newAccount.value.currency})' added`,
    );
    newAccount.value.name = null;
    newAccount.value.currency = null;
    newAccount.value.balance = null;
    await loadAccounts();
  } else {
    console.log("something went wrong Toast"); // DEV
    errorToast("The account could not be added");
  }
};

// Pinned transactions
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

// TODO move to a separate component
// Sliding side-panels
const showTagAddPanel = ref(false);
const showAccountPanel = ref(false);

// View specific menu items
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
  <div class="container">
    <Teleport to="#secondary-menu-target">
      <Menubar :model="setupItems" class="border-none bg-transparent" />
    </Teleport>

    <Drawer
      v-model:visible="showTagAddPanel"
      header="Add New Tags"
      position="right"
    >
      <NewTag />
    </Drawer>

    <Drawer
      v-model:visible="showAccountPanel"
      header="Accounts"
      position="right"
    >
      <input
        v-model="newAccount.name"
        ref="panelAccountNameInput"
        placeholder="Name"
      />
      <input v-model="newAccount.currency" placeholder="Currency" />
      <input v-model="newAccount.balance" placeholder="Balance" />
      <DatePicker
        v-model="newAccount.ts"
        inline
        showTime
        hourFormat="24"
        showButtonBar
      />
      <button @click="submitNewAccount">Add</button>
    </Drawer>

    <div class="left">
      <h2>Pined Transactions</h2>
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
    </div>

    <div class="right">
      <h2>Add Transaction</h2>
      <input
        v-model="form.title"
        placeholder="Name"
        :disabled="selectedTransaction !== null"
      />
      <input v-model="form.delta.subtitle" placeholder="Description" />
      <DatePicker
        v-model="form.delta.ts"
        inline
        showTime
        showButtonBar
        hourFormat="24"
      />
      <input v-model="form.delta.amount" placeholder="Amount" />
      <select v-model="form.delta.id_a">
        <option :value="null" disabled selected>Account</option>
        <option
          v-for="account in accounts"
          :key="account.id_a"
          :value="account.id_a"
        >
          {{ account.account }} ({{ account.currency }})
        </option>
      </select>
      <select v-model="form.delta.tag">
        <option :value="null" disabled selected>Tag</option>
        <option v-for="tag in tags" :key="tag.tag" :value="tag.tag">
          {{ tag.tag_name }}
        </option>
      </select>
      <button @click="submitAddTransaction">Submit</button>
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  gap: 40px;
  padding: 30px;
}

.left {
  flex: 1;
  background: #e2e2e2;
  color: rgb(0, 0, 0);
  padding: 20px;
  overflow-y: auto;
  max-height: 80vh;
}

.right {
  width: 320px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* input,
select,
button {
  padding: 8px;
} */

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
