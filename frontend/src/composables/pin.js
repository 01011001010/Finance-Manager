// TODO change the whole pinned logic into a boolean in the transition table, not a separate table

// Custom utils
import { customToaster } from "@/composables/customToast";
import { getData, apiPost } from "@/composables/api";

export function pinUtils() {
  // Set-up
  const { successToast, neutralToast, errorToast } = customToaster();
  const { reloadLogTransactions, loadPinned, loadDeltas } = getData();
  const { post } = apiPost();

  const isPinned = (transactionObj) => transactionObj.pinned;

  const togglePin = async (transactionObj) => {
    // console.log(transactionObj);
    const id = transactionObj.id_t;
    const pin = !isPinned(transactionObj);
    const messagePrefix = pin ? "" : "un";
    const payload = JSON.stringify({ id_t: id, newPin: pin });
    // console.log(
    //   `Transaction ${id} ${messagePrefix}pin started\nPayload: `,
    //   payload,
    // );
    const response = await post("/api/update/pin", payload);
    // console.log(response); // DEV
    if (response.ok) {
      // console.log("ok Toast"); // DEV
      successToast(`Transaction ${messagePrefix}pinned`);
      await reloadLogTransactions(); // TODO unnecessary full load, think about separating the list of pinned id_t
    } else {
      // console.log("something went wrong Toast"); // DEV
      // console.log(response);
      errorToast(`The transaction could not be ${messagePrefix}pinned`);
    }
  };

  return {
    isPinned,
    togglePin,
  };
}
