import { ref } from "vue";

const selectedTransaction = ref(null);

export function transactionSelector() {
  const clearSelection = () => {
    selectedTransaction.value = null;
  };

  return { clearSelection, selectedTransaction };
}
