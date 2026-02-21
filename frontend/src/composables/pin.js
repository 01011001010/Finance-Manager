// TODO change the whole pinned logic into a boolean in the transition table, not a separate table

// Custom utils
import { customToaster } from "@/composables/customToast";
import { getData, apiPost } from "@/composables/api";

export function pinUtils() {
  // Set-up
  const { successToast, neutralToast, errorToast } = customToaster();
  const { pinnedId_t, loadPinned } = getData();
  const { post } = apiPost();

  const isPinned = (id) => pinnedId_t.value.includes(id);

  const setPin = async (id, pin) => {
    const messagePrefix = pin ? "" : "un";
    const url = pin ? "/api/transactions/pin" : "/api/transactions/unpin";
    const payload = JSON.stringify({ id_t: id });
    const response = await post(url, payload);
    console.log(response); // DEV
    if (response.ok) {
      console.log("ok Toast"); // DEV
      successToast(`Transaction ${messagePrefix}pinned`);
      await loadPinned();
    } else {
      console.log("something went wrong Toast"); // DEV
      errorToast(`The transaction could not be ${messagePrefix}pinned`);
    }
  };

  const togglePin = async (id) => {
    setPin(id, !isPinned(id));
  };

  return {
    isPinned,
    togglePin,
  };
}
