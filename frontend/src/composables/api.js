import { ref, computed } from "vue";

// Data loading
const transactions = ref([]);
const accountsWithArchived = ref([]);
const tagsWithArchived = ref([]);
const pinnedId_t = ref([]);

const pinnedTransactions = computed(() =>
  transactions.value.filter((t) => pinnedId_t.value.includes(t.id)),
);

const accounts = computed(() =>
  accountsWithArchived.value.filter((a) => !a.hidden),
);
const tags = computed(() => tagsWithArchived.value.filter((t) => !t.hidden));

export function dataLoaders() {
  const loadTransactions = async () => {
    const res = await fetch("/api/deltaLog");
    transactions.value = await res.json();
  };

  const loadAccounts = async () => {
    const res = await fetch("/api/accounts");
    accountsWithArchived.value = await res.json();
  };

  const loadTags = async () => {
    const res = await fetch("/api/tags");
    tagsWithArchived.value = await res.json();
  };

  const loadPinned = async () => {
    const res = await fetch("/api/pinned");
    pinnedId_t.value = await res.json();
  };

  return {
    transactions,
    accounts,
    accountsWithArchived,
    tags,
    tagsWithArchived,
    pinnedId_t,
    pinnedTransactions,
    loadTransactions,
    loadAccounts,
    loadTags,
    loadPinned,
  };
}

// API POST handler
export function apiPost() {
  const post = async (url, payload) => {
    // console.log(`POST:${url}, payload:${payload}`); // DEV
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: payload,
    });
    return {
      status: response.status,
      ok: response.ok,
      data: await response.json(),
    };
  };

  return { post };
}
