import { ref, computed } from "vue";

// Data refs
const deltas = ref([]);
const transactionOverview = ref([]);
const accountsWithArchived = ref([]);
const tagsWithArchived = ref([]);
const selectedTransaction = ref(null);

const pinnedTransactions = ref([]);

const accounts = computed(() =>
  accountsWithArchived.value.filter((a) => !a.hidden),
);
const tags = computed(() => tagsWithArchived.value.filter((t) => !t.hidden));

export function getData() {
  const loadDeltas = async () => {
    const response = await fetch("/api/data/deltas");

    if (response.ok) {
      deltas.value = (await response.json()).data;
      // console.log('deltas loaded');  // DEV
      // console.log(deltas.value);  // DEV
    } else {
      deltas.value = null;
      console.error(
        "Loading deltas failed\nError detail:",
        (await response.json()).detail,
      );
    }
  };

  const loadOverview = async () => {
    const response = await fetch("/api/data/overview");

    if (response.ok) {
      transactionOverview.value = (await response.json()).data;
      // console.log('overview loaded');  // DEV
      // console.log(transactionOverview.value);  // DEV
    } else {
      transactionOverview.value = null;
      console.error(
        "Loading overview failed\nError detail:",
        (await response.json()).detail,
      );
    }
  };

  const loadAccounts = async () => {
    const response = await fetch("/api/data/accounts");

    if (response.ok) {
      accountsWithArchived.value = (await response.json()).data;
      // console.log('accounts loaded');  // DEV
      // console.log(accountsWithArchived.value);  // DEV
    } else {
      accountsWithArchived.value = null;
      console.error(
        "Loading accounts failed\nError detail:",
        (await response.json()).detail,
      );
    }
  };

  const loadTags = async () => {
    const response = await fetch("/api/data/tags");

    if (response.ok) {
      tagsWithArchived.value = (await response.json()).data;
      // console.log('tags loaded');  // DEV
      // console.log(tagsWithArchived.value);  // DEV
    } else {
      tagsWithArchived.value = null;
      console.error(
        "Loading tags failed\nError detail:",
        (await response.json()).detail,
      );
    }
  };

  const loadPinned = async () => {
    const response = await fetch("/api/data/pinned");

    if (response.ok) {
      pinnedTransactions.value = (await response.json()).data;
      // console.log('pinned loaded');  // DEV
      // console.log(pinnedTransactions.value);  // DEV
    } else {
      pinnedTransactions.value = null;
      console.error(
        "Loading pinned failed\nError detail:",
        (await response.json()).detail,
      );
    }
  };

  const reloadLogTransactions = async () => {
    await loadDeltas();
    await loadPinned();
  };

  return {
    deltas,
    accounts,
    transactionOverview,
    accountsWithArchived,
    tags,
    tagsWithArchived,
    pinnedTransactions,
    selectedTransaction,
    loadDeltas,
    loadOverview,
    loadAccounts,
    loadTags,
    loadPinned,
    reloadLogTransactions,
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
