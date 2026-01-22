<!-- TODO
data validation on submit

styling
-> group if neighbouring are the same transaction??

transaction pinning



DONE
 - move the tag to delta from transaction (eg. rent, and bank fees as 2 separate deltas)
 - replace hardcoded accounts, ...
   + allow currency based on choice of account
 - when selecting a transaction, greying out is ok,
   but I want to stash the contents, replace them with the info from the selected transaction
   and if clear button used, then put back what was there
 - tag hardcoding removal
-->

<script setup>
import { ref, onMounted, watch } from "vue";
import { VueDatePicker } from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";

const today = new Date().toISOString();
const form = ref({
  title: "",
  subtitle: "",
  delta: {
    ts: today,
    amount: null,
    id_a: null,
    tag: null,
    note: null,
  },
});

const transactions = ref([]);
const accounts = ref([]);
const tags = ref([]);

const loadTransactions = async () => {
  const res = await fetch("/api/transactions");
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

const selectedTransaction = ref(null);
const clearSelection = () => {
  selectedTransaction.value = null;
};

let stashedTitle = null;
let stashedSubtitle = null;
watch(selectedTransaction, (newId) => {
  if (newId === null) {
    form.value.title = stashedTitle;
    stashedTitle = null;
    form.value.subtitle = stashedSubtitle;
    stashedSubtitle = null;
    return;
  }

  if (stashedTitle === null) {
    stashedTitle = form.value.title;
    stashedSubtitle = form.value.subtitle;
  }

  const transaction = transactions.value.find((t) => t.id === newId);
  if (!transaction) return;

  form.value.title = transaction.title;
  form.value.subtitle = transaction.subtitle ?? " ";
});

const submit = async () => {
  if (selectedTransaction.value) {
    // console.log('adding to existing')
    // console.log(JSON.stringify({
    //     id_t: selectedTransaction.value,
    //     delta: form.value.delta
    //   }))
    const response = await fetch("/api/transactions/existing", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id_t: selectedTransaction.value,
        delta: form.value.delta,
      }),
    });

    const data = await response.json();
    // console.log(data)
    clearSelection();
  } else {
    // console.log('adding new')
    // console.log(JSON.stringify(form.value))
    const response = await fetch("/api/transactions/new", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form.value),
    });

    const data = await response.json();
    // console.log(data)
  }
  form.value.title = null;
  form.value.subtitle = null;
  form.value.delta.amount = null;
  form.value.delta.id_a = null;
  form.value.delta.tag = null;
  form.value.delta.note = null; // TODO note for deltas implement in db
  loadTransactions();
};

onMounted(() => {
  loadTransactions();
  loadAccounts();
  loadTags();
});
</script>

<template>
  <div class="container">
    <div class="left">
      <h2>Existing Transactions</h2>
      <button @click="clearSelection">Clear selected transaction</button>
      <table>
        <thead>
          <tr>
            <th>Select</th>
            <th>ID</th>
            <th>Title</th>
            <th>Subtitle</th>
            <th>Amount</th>
            <th>Currency</th>
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
              <td>{{ t.id }}</td>
              <td>{{ t.title }}</td>
              <td>{{ t.subtitle }}</td>
              <td>{{ d.amount }}</td>
              <td>{{ d.currency }}</td>
              <td>{{ d.account }}</td>
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
      <input
        v-model="form.subtitle"
        placeholder="Description"
        :disabled="selectedTransaction !== null"
      />

      <input v-model="form.delta.note" placeholder="Note" />
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
      <button @click="submit">Submit</button>
    </div>
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
