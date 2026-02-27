<!-- TODO transition to DataTable
          - rows with TITLE, SUBTITLE, AMOUNT, ACCOUNT, TAG, DATETIME, PIN/EDIT/DELETE buttons (not particularly in this order)
          - freeze row on select? -> unselect might be hard in a long list
          - see SORT, SCROLL, FILTER, EDIT, VIRTUAL SCROLL, LAZY LOADING

          Deltas sub-tables
          - left padding
          - sorting? (think how without headers)

          Month row divider?

          disable row selection for overview

          ...
-->

<script setup>
import { ref, watch } from "vue";
import Button from "primevue/button";
import DataTable from "primevue/datatable";
import Column from "primevue/column";

// Custom utils
import { getData } from "@/composables/api";
import { pinUtils } from "@/composables/pin";
import { customToaster } from "@/composables/customToast";

const props = defineProps({
  dataSource: { type: String, required: true },
  autoExpand: { type: Boolean, required: true },
});

// Set-up
const { deltas, pinnedTransactions, transactionOverview, selectedTransaction } =
  getData();
const { isPinned, togglePin } = pinUtils();
const { successToast, neutralToast, errorToast } = customToaster();

const expandedRows = ref({});
const items =
  props.dataSource == "pinned"
    ? pinnedTransactions
    : props.dataSource == "chronological"
      ? deltas
      : transactionOverview;

// Data formatting
const formatCurrency = (value, currency) => {
  return value.toLocaleString("en-CH", {
    style: "currency",
    currency: currency,
  });
};
const formatDate = (value) => {
  if (!value) return "";

  return new Intl.DateTimeFormat("en-CH", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
};

// Row expansion and selection // TODO
const onRowSelect = (event) => {
  neutralToast("Row Selected");
  console.log("Row Selected");
  console.log(event.data);
};
const onRowUnselect = (event) => {
  neutralToast("Row Unselected");
  console.log("Row Unselected");
  console.log(event.data);
};
const onRowExpand = (event) => {
  neutralToast("Row Expanded");
  console.log("Row Expanded");
  console.log(event.data);
};
const onRowCollapse = (event) => {
  neutralToast("Row Collapsed");
  console.log("Row Collapsed");
  console.log(event.data);
};
const expandAll = () => {
  expandedRows.value = items.value.reduce(
    (acc, t) => (acc[t.id_t] = true) && acc,
    {},
  );
};
const collapseAll = () => {
  expandedRows.value = null;
};

// Utilities // TODO
const confirmDeleteTransaction = (transaction) => {
  console.log("TODO Trans. del. dialog");
  console.log(transaction);
  errorToast("Not implemented yet, sorry");
};
const editTransaction = (transaction) => {
  console.log("TODO Trans. edit");
  console.log(transaction);
  errorToast("Not implemented yet, sorry");
};
const confirmDeleteDelta = (delta) => {
  console.log("TODO Delta. del. dialog");
  console.log(delta);
  errorToast("Not implemented yet, sorry");
};
const editDelta = (delta) => {
  console.log("TODO Delta. edit");
  console.log(delta);
  errorToast("Not implemented yet, sorry");
};

// Expand rows when data loaded
const unwatch = watch(
  () => items.value,
  (newData) => {
    if (props.autoExpand && newData?.length > 0) {
      expandAll();
    }
  },
  { immediate: true },
);
if (!props.autoExpand) {
  unwatch();
}
</script>

<template>
  <DataTable
    :value="items"
    v-model:expandedRows="expandedRows"
    v-model:selection="selectedTransaction"
    selectionMode="single"
    :metaKeySelection="false"
    dataKey="id_t"
    scrollable
    scrollHeight="flex"
    :showHeaders="false"
    @rowExpand="onRowExpand"
    @rowCollapse="onRowCollapse"
    @rowSelect="onRowSelect"
    @rowUnselect="onRowUnselect"
    tableStyle="min-width: 50rem"
    size="small"
    :pt="{
      rowExpansionCell: { class: 'p-0' },
      bodyrow: ({ context }) => ({
        class: [
          { 'bg-[var(--p-surface-50)]': !context.selected },
          { 'hover:!bg-[var(--p-surface-200)]': !context.selected },
        ],
      }),
    }"
  >
    <template v-if="!autoExpand && items?.length > 0" #header>
      <div class="flex gap-2">
        <Button
          variant="text"
          size="small"
          class="!p-0.5 !text-[0.7rem]"
          icon="pi pi-plus"
          label="Expand All"
          @click="expandAll"
        />
        <Button
          variant="text"
          size="small"
          class="!p-0.5 !text-[0.7rem]"
          icon="pi pi-minus"
          label="Collapse All"
          @click="collapseAll"
        />
      </div>
    </template>
    <template #empty>
      <span class="text-xs opacity-60 flex items-center"
        >{{ props.dataSource == "pinned" ? "Bookmark" : "Add" }} transactions to
        fill it here</span
      >
    </template>
    <Column v-if="!autoExpand" expander class="w-8" />
    <Column field="title"></Column>
    <Column :exportable="false" class="w-64">
      <template #body="slotProps">
        <div class="flex justify-end">
          <Button
            variant="text"
            rounded
            size="small"
            class="!p-0.5 !w-7 !h-7 !text-[0.7rem] group"
            severity="secondary"
            @click="togglePin(slotProps.data)"
          >
            <template #icon>
              <div
                class="relative w-full h-full flex items-center justify-center"
              >
                <i
                  class="group-hover:opacity-0 transition-opacity duration-200"
                  :class="
                    isPinned(slotProps.data)
                      ? 'pi pi-bookmark-fill'
                      : 'pi pi-bookmark'
                  "
                ></i>
                <i
                  class="absolute opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                  :class="
                    isPinned(slotProps.data)
                      ? 'pi pi-bookmark'
                      : 'pi pi-bookmark-fill'
                  "
                ></i>
              </div>
            </template>
          </Button>
          <Button
            variant="text"
            rounded
            size="small"
            class="!p-0.5 !w-7 !h-7 !text-[0.7rem]"
            icon="pi pi-pencil"
            severity="secondary"
            @click="editTransaction(slotProps.data)"
          />
          <Button
            variant="text"
            rounded
            size="small"
            class="!p-0.5 !w-7 !h-7 !text-[0.7rem]"
            icon="pi pi-trash"
            severity="danger"
            @click="confirmDeleteTransaction(slotProps.data)"
          />
        </div>
      </template>
    </Column>

    <template #expansion="slotProps">
      <div>
        <DataTable
          :value="slotProps.data.deltas"
          :showHeaders="false"
          class="w-full text-sm"
          tableClass="table-fixed w-full"
          size="small"
          :pt="{
            tbody: {
              class: '[&>tr:last-child>td]:border-b-0',
            },
            bodyrow: {
              class: 'hover:!bg-[var(--p-datatable-row-background)]',
            },
          }"
        >
          <Column field="subtitle" class="w-[20%] pl-8 truncate"></Column>
          <Column field="tag" class="w-[13%] truncate"></Column>
          <Column
            field="amount"
            class="w-[14%] text-right pr-6 whitespace-nowrap"
          >
            <template #body="slotProps">
              <span class="font-mono">
                {{
                  formatCurrency(slotProps.data.amount, slotProps.data.currency)
                }}
              </span>
            </template>
          </Column>
          <Column field="account" class="w-[16%] pl-8 truncate"></Column>
          <Column
            field="balance_after"
            class="w-[17%] text-right pr-6 whitespace-nowrap"
          >
            <template #body="slotProps">
              <span class="font-mono">
                {{
                  formatCurrency(
                    slotProps.data.balance_after,
                    slotProps.data.currency,
                  )
                }}
              </span>
            </template>
          </Column>
          <Column field="ts" class="w-[20%] truncate">
            <template #body="slotProps">
              {{ formatDate(slotProps.data.ts) }}
            </template>
          </Column>
          <Column :exportable="false" class="w-28">
            <template #body="slotProps">
              <div class="flex justify-end">
                <Button
                  variant="text"
                  rounded
                  size="small"
                  class="!p-0.5 !w-7 !h-7 !text-[0.7rem]"
                  icon="pi pi-pencil"
                  severity="secondary"
                  @click="editDelta(slotProps.data)"
                />
                <Button
                  variant="text"
                  rounded
                  size="small"
                  class="!p-0.5 !w-7 !h-7 !text-[0.7rem]"
                  icon="pi pi-trash"
                  severity="danger"
                  @click="confirmDeleteDelta(slotProps.data)"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </template>
  </DataTable>
</template>
