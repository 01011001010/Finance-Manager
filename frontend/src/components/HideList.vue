<script setup>
import Button from "primevue/button";
import ScrollPanel from "primevue/scrollpanel";
import DataTable from "primevue/datatable";
import Column from "primevue/column";

// Custom utils
import { customToaster } from "@/composables/customToast";
import { apiPost } from "@/composables/api";

// Set-up
const { successToast, neutralToast, errorToast } = customToaster();
const { post } = apiPost();

// Component props
const props = defineProps({
  items: { type: Array, required: true },
  itemID: { type: String, required: true },
  apiUrl: { type: String, required: true },
  loadFn: { type: Function, required: true },
  toastName: { type: String, required: true },
});

const toggle = async (item) => {
  item.hidden = !item.hidden;

  const payload = JSON.stringify({
    id: item[props.itemID],
    newArchivedState: item.hidden,
  });
  // console.log(payload); // DEV
  const response = await post(props.apiUrl, payload);
  // console.log(response); // DEV
  if (response.ok) {
    // console.log("ok Toast"); // DEV
    successToast(
      account.hidden
        ? `${props.toastName} archived`
        : `${props.toastName} restored`,
    );
    await props.loadFn();
  } else {
    item.hidden = !item.hidden;
    // console.log("something went wrong Toast"); // DEV
    errorToast(
      account.hidden
        ? `${props.toastName} could not be archived`
        : `${props.toastName} could not be restored`,
    );
  }
};
</script>

<template>
  <div class="h-full flex-1 flex flex-col min-h-0">
    <DataTable
      :value="items"
      scrollable
      scrollHeight="flex"
      size="small"
      :showHeaders="false"
      class="flex-1"
    >
      <Column>
        <template #body="{ data }">
          <span
            :class="
              data.hidden
                ? 'text-surface-300 dark:text-surface-600'
                : 'text-surface-600 dark:text-surface-300'
            "
            ><slot :item="data">
              {{ data.tag_name || data.account }}
            </slot></span
          >
        </template>
      </Column>
      <Column class="text-right pr-4">
        <template #body="{ data }">
          <Button
            severity="secondary"
            variant="text"
            size="small"
            rounded
            class="group"
            @click="toggle(data)"
          >
            <template #icon>
              <div
                class="relative w-full h-full flex items-center justify-center"
              >
                <i
                  class="group-hover:opacity-0 transition-opacity duration-200"
                  :class="data.hidden ? 'pi pi-eye-slash' : 'pi pi-eye'"
                ></i>
                <i
                  class="absolute opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                  :class="data.hidden ? 'pi pi-eye' : 'pi pi-eye-slash'"
                ></i>
              </div>
            </template>
          </Button>
        </template>
      </Column>
    </DataTable>
  </div>
</template>
