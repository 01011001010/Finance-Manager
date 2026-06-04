<script setup>
import FileUpload from "primevue/fileupload";

// Custom utils
import { customToaster } from "@/composables/customToast";
import { getData } from "@/composables/api";

// Set-up
const { reloadLogTransactions } = getData(); // TODO accounts, not transactions

// TODO give hint on hover about needed columns

const { successToast, neutralToast, errorToast } = customToaster();
const onUpload = async (event) => {
  // TODO TODAY
  try {
    const response = JSON.parse(event.xhr.response);

    const message = response.detail || "Accounts uploaded successfully";
    successToast(message);

    // await reloadLogTransactions();  // TODO accounts, not transactions

    console.log("Upload Success:", response);
  } catch (e) {
    errorToast("Upload failed");
    console.error("Upload error:", e);
  }
};

const onUploadError = (event) => {
  // TODO TODAY
  try {
    const errorResponse = JSON.parse(event.xhr.response);

    errorToast(errorResponse.detail);

    console.error("Backend Error:", errorResponse);
  } catch (e) {
    errorToast("A server error occurred during upload.");
    console.error("Error parsing logic:", e);
  }
};
</script>

<template>
  <FileUpload
    mode="basic"
    name="file"
    url="/api/finance/bulk/upload/accounts"
    accept=".csv"
    :maxFileSize="1000000"
    @upload="onUpload"
    @error="onUploadError"
    :multiple="false"
    :auto="true"
    chooseLabel="Import accounts (.csv)"
    chooseIcon="pi pi-upload"
    :chooseButtonProps="{ fluid: true }"
  />
  <!-- TODO Maybe use same icon from drawer menu for account creation-->
</template>
