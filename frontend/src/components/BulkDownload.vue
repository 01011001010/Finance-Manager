<script setup>
import { ref } from "vue";
import Button from "primevue/button";

// Custom utils
import { customToaster } from "@/composables/customToast";

const isDownloading = ref(false);

const downloadBackup = async () => {
  // DEV Requires Chrome/Edge
  //     Alternative: blob link (addition pro: will not circumvent list of downloads of the browser)

  isDownloading.value = true;

  try {
    const response = await fetch("/api/finance/bulk/download", {
      method: "GET",
    });

    if (response.ok) {
      let filename = "export.zip"; // default
      const disposition = response.headers.get("content-disposition");

      if (disposition && disposition.includes("filename=")) {
        const match = /filename="([^"]+)"/.exec(disposition);
        if (match && match[1]) {
          filename = match[1];
        } else {
          const unquotedMatch = /filename=([^;]+)/.exec(disposition);
          if (unquotedMatch && unquotedMatch[1]) {
            filename = unquotedMatch[1].trim();
          }
        }
      }

      const blob = await response.blob();

      try {
        const fileHandle = await window.showSaveFilePicker({
          suggestedName: filename,
          types: [
            {
              description: "ZIP Archive",
              accept: { "application/zip": [".zip"] },
            },
          ],
        });

        const writable = await fileHandle.createWritable();
        await writable.write(blob);
        await writable.close();
      } catch (pickerError) {
        // User clicked "Cancel" on the dialog, or browser doesn't support it
        neutralToast("Download cancelled");
        console.log("Download cancelled by user or API not supported.");
      }
    } else {
      try {
        const errorData = await response.json();
        const errorDetail = errorData.detail || "Unknown server error";

        errorToast("Something went wrong");
        console.error(`Export failed. Detail: ${errorDetail}`);
      } catch (parseError) {
        errorToast("Something went horribly wrong");
        console.error(
          `Export failed with status ${response.status}, and the body wasn't valid JSON.`,
        );
      }
    }
  } catch (networkError) {
    errorToast("Something went wrong");
    console.error("Network error:", networkError);
  } finally {
    isDownloading.value = false;
  }
};
</script>

<template>
  <Button
    label="Export data (.zip)"
    icon="pi pi-download"
    :loading="isDownloading"
    @click="downloadBackup"
    fluid
  />
</template>
