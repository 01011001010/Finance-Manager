<!-- TODO
tag and account management

data validation on submit

styling
-> group if neighbouring are the same transaction??
-> pinned transactions hide deltas into a rolldown


DONE
 - move the tag to delta from transaction (eg. rent, and bank fees as 2 separate deltas)
 - replace hardcoded accounts, ...
   + allow currency based on choice of account
 - when selecting a transaction, greying out is ok,
   but I want to stash the contents, replace them with the info from the selected transaction
   and if clear button used, then put back what was there
 - tag hardcoding removal
 - pin transaction
-->

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { VueDatePicker } from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";
import SlidePanel from "@/components/SlidePanel.vue";

// Data loading
const transactions = ref([]);
const accounts = ref([]);
const tags = ref([]);
const pinnedId_t = ref([]);

const pinnedTransactions = computed(() =>
  transactions.value.filter((t) => pinnedId_t.value.includes(t.id)),
);

const loadTransactions = async () => {
  const res = await fetch("/api/deltaLog");
  transactions.value = await res.json();
};

const loadAccounts = async () => {
  const res = await fetch("/api/accounts");
  accounts.value = await res.json();
};

const loadTags = async () => {
  const res = await fetch("/api/tags");
  tags.value = await res.json();
};

const loadPinned = async () => {
  const res = await fetch("/api/pinned");
  pinnedId_t.value = await res.json();
};

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

const post = async (url, body) => {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body,
  });
  return await response.json();
};

// Transaction form
const today = new Date().toISOString();
const form = ref({
  title: "",
  delta: {
    ts: today,
    subtitle: "",
    amount: null,
    id_a: null,
    tag: null,
  },
});
const submitAddTransaction = async () => {
  const url = selectedTransaction.value
    ? "/api/transactions/existing"
    : "/api/transactions/new";
  const payload = JSON.stringify(
    selectedTransaction.value
      ? {
          id_t: selectedTransaction.value,
          delta: form.value.delta,
        }
      : form.value,
  );
  const data = await post(url, payload); // TODO pop-up about success/fail
  form.value.title = null;
  form.value.delta.subtitle = null;
  form.value.delta.amount = null;
  form.value.delta.id_a = null;
  form.value.delta.tag = null;
  await loadTransactions();
};

// Tag form
const newTag = ref({
  tag: null,
});
const submitNewTag = async () => {
  const url = "/api/add/tag"; // TODO implement
  const payload = JSON.stringify(newTag.value);
  const data = await post(url, payload); // TODO pop-up about success/fail
  newTag.tag = null;
  await loadTags();
};

// Account form
const newAccount = ref({
  name: "",
  currency: "",
  balance: "",
});

const submitNewAccount = async () => {
  const url = "/api/add/account"; // TODO implement
  const body = JSON.stringify(newAccount.value);
  const data = await post(url, payload); // TODO pop-up about success/fail
  newAccount.name = null;
  newAccount.currency = null;
  newAccount.balance = null;
  await loadAccounts();
};

// Pinned transactions
const isPinned = (id) => pinnedId_t.value.includes(id);
const pinTransaction = async (id) => {
  // TODO, decide if frontend or backend should check this condition
  if (!pinnedId_t.value.includes(id)) {
    const url = "/api/transactions/pin";
    const body = JSON.stringify({ id_t: id });
    const data = await post(url, payload); // TODO pop-up about success/fail
    await loadPinned();
  }
};

const unpinTransaction = async (id) => {
  const url = "/api/transactions/unpin";
  const body = JSON.stringify({ id_t: id });
  const data = await post(url, payload); // TODO pop-up about success/fail
  await loadPinned();
};

// Sliding side-panels
const showTagPanel = ref(false);
const showAccountPanel = ref(false);

const panelTagInput = ref(null);
const panelAccountNameInput = ref(null);

const closePanels = () => {
  // Not necessarily needed, as the pull-out tabs of other panels are hidden under any open panel.
  // Kept for future-proofing and manual tempering with z-index
  showTagPanel.value = false;
  showAccountPanel.value = false;
};

onMounted(() => {
  loadTransactions();
  loadAccounts();
  loadTags();
  loadPinned();
});
</script>

<template>
  <div class="container">
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

      <VueDatePicker
        v-model="form.delta.ts"
        inline
        :time-config="{ timePickerInline: true }"
        auto-apply
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

    <SlidePanel
      v-model="showTagPanel"
      tabPosition="50px"
      tabLabel="Add Tags"
      @open="closePanels"
      @opened="panelTagInput?.focus()"
    >
      <h3>Add a tag</h3>
      <input v-model="newTag.tag" ref="panelTagInput" placeholder="Tag" />
      <button @click="submitNewTag">Add</button>
    </SlidePanel>
    <SlidePanel
      v-model="showAccountPanel"
      tabPosition="200px"
      tabLabel="Add Accounts"
      @open="closePanels"
      @opened="panelAccountNameInput?.focus()"
    >
      <h3>Add an account</h3>
      <input
        v-model="newAccount.name"
        ref="panelAccountNameInput"
        placeholder="Name"
      />
      <input v-model="newAccount.currency" placeholder="Currency" />
      <input v-model="newAccount.balance" placeholder="Balance" />
      <VueDatePicker
        v-model="newAccount.date"
        inline
        :time-config="{ timePickerInline: true }"
        auto-apply
      />
      <button @click="submitNewAccount">Add</button>
    </SlidePanel>
  </div>
</template>

<style>
.container {
  display: flex;
  gap: 40px;
  padding: 30px;
}

.vue3-datepicker {
  width: 100%;
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

input,
select,
button {
  padding: 8px;
}

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
