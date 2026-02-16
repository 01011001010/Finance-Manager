<script setup>
import { ref, watch, nextTick } from "vue";
import { Form } from "@primevue/forms";
import IftaLabel from "primevue/iftalabel";
import IconField from "primevue/iconfield";
import InputIcon from "primevue/inputicon";
import InputText from "primevue/inputtext";
import InputNumber from "primevue/inputnumber";
import DatePicker from "primevue/datepicker";
import AutoComplete from "primevue/autocomplete";
import Button from "primevue/button";
import Message from "primevue/message";
import FocusTrap from "primevue/focustrap";

// Custom utils
import { customToaster } from "@/composables/customToast";
import { dataLoaders, apiPost } from "@/composables/api";
import { transactionSelector } from "@/composables/deltaLog";

// Set-up
const vFocustrap = FocusTrap;
const { successToast, neutralToast, errorToast } = customToaster();
const { accounts, tags, transactions, loadTransactions } = dataLoaders();
const { post } = apiPost();
const { selectedTransaction } = transactionSelector();

// Values
const emptyForm = () => ({
  title: "",
  ts: new Date(),
  subtitle: "",
  amount: 0.0,
  accountObj: null,
  tagObj: null,
});
const initialValues = ref(emptyForm());
const resetForm = () => {
  initialValues.value = emptyForm();
};

const formRef = ref(null);
const clearField = (formName, refName, value = null) => {
  initialValues.value[refName] = value;
  if (formRef.value) {
    // console.log(formRef.value)  // DEV
    formRef.value.setFieldValue(formName, value);
  }
};
const clearError = async (formObj) => {
  if (formObj) {
    await nextTick();
    formObj.invalid = false;
    formObj.error = null;
    formObj.errors = [];
  }
};

// Transaction selection
let stashedTitle = null;
watch(selectedTransaction, async (newId) => {
  if (newId === null) {
    initialValues.value.title = stashedTitle;
    stashedTitle = null;
    return;
  }
  if (stashedTitle === null) {
    stashedTitle = initialValues.value.title;
  }
  const transaction = transactions.value.find((t) => t.id === newId);
  if (!transaction) return;
  initialValues.value.title = transaction.title;

  if (formRef.value) {
    if (formRef.value.states.title) {
      clearError(formRef.value.states.title);
    }
  }
});

// Dropdown filtering
const nonConsecutiveMatch = (query, text) => {
  // Escape special characters and create a pattern: "a.*b.*c.*d"
  const pattern = query
    .split("")
    .map(
      (char) => char.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), // Escape regex chars
    )
    .join(".*");

  const re = new RegExp(pattern, "i"); // "i" for case-insensitive
  return re.test(text);
};

// Accounts
const filteredAccounts = ref([]);
const filterAccounts = (e) => {
  // const query = e.query.toLowerCase();
  // filteredAccounts.value = accounts.value.filter(accountObj => (`${accountObj.account} ${accountObj.currency}`.toLowerCase().includes(query)));
  const query = e.query.trim();
  if (!query) {
    filteredAccounts.value = [...accounts.value];
    return;
  }

  filteredAccounts.value = accounts.value.filter((accountObj) =>
    nonConsecutiveMatch(
      query,
      `${accountObj.account} (${accountObj.currency})`,
    ),
  );
};
const getAccountLabel = (accountObj) => {
  if (!accountObj) return "";
  return `${accountObj.account} (${accountObj.currency})`;
};

// Tags
const filteredTags = ref([]);
const filterTags = (e) => {
  // const query = e.query.toLowerCase();
  // filteredTags.value = tags.value.filter(tagObj => (tagObj.tag_name.toLowerCase().includes(query)));
  const query = e.query.trim();
  if (!query) {
    filteredTags.value = [...tags.value];
    return;
  }

  filteredTags.value = tags.value.filter((tagObj) =>
    nonConsecutiveMatch(query, tagObj.tag_name),
  );
};
const getTagLabel = (tagObj) => {
  if (!tagObj) return "";
  return tagObj.tag_name;
};

// Focus on clear
const titleInput = ref(null);
const subtitleInput = ref(null);
const amountInput = ref(null);
const accountInput = ref(null);
const tagInput = ref(null);

const onBalanceFocus = (event) => {
  setTimeout(() => {
    if (event.target && typeof event.target.select === "function") {
      event.target.select(); // Select contents on focus to prevent cursor starting at the end of the current value
    }
  }, 50);
};

// Resolver
const resolver = ({ values }) => {
  // console.log("RESOLVER");  // DEV
  // console.log(values);  // DEV
  const errors = {};

  if (!values.title?.trim() && !selectedTransaction.value) {
    errors.title = [{ message: "Provide a transaction title" }];
  }

  if (
    values.amount === null ||
    values.amount === undefined ||
    values.amount === 0
  ) {
    errors.amount = [{ message: "A non-zero amount is required" }];
  }

  if (typeof values.accountObj !== "object") {
    errors.accountObj = [
      { message: "Please select a valid account from the list" },
    ];
  } else if (!values.accountObj || !values.accountObj.id_a) {
    errors.accountObj = [{ message: "Select an account" }];
  }

  if (
    values.tagObj &&
    (typeof values.tagObj !== "object" || !values.tagObj.tag)
  ) {
    errors.tagObj = [{ message: "Please select a valid tag from the list" }];
  }

  if (!values.ts) {
    errors.ts = [{ message: "Select a date" }];
  }

  return { errors };
};

// Submit Handler
const onFormSubmit = async ({ valid, states, reset }) => {
  if (!valid) {
    neutralToast("Check all fields to submit");
    return;
  }

  const url = selectedTransaction.value
    ? "/api/transactions/existing"
    : "/api/transactions/new";

  const delta = {
    subtitle: states.subtitle.value,
    amount: states.amount.value,
    id_a: states.accountObj.value.id_a,
    tag: states.tagObj.value?.tag || null,
    ts: states.ts.value.toISOString(),
  };
  const payload = JSON.stringify(
    selectedTransaction.value
      ? {
          id_t: selectedTransaction.value,
          delta: delta,
        }
      : {
          title: states.title.value,
          delta: delta,
        },
  );
  // console.log(payload); // DEV
  const response = await post(url, payload);
  // console.log(response); // DEV

  if (response.ok) {
    // console.log("ok Toast"); // DEV
    successToast("Transaction added");
    resetForm();
    reset();
    await loadTransactions();
  } else {
    // console.log("something went wrong Toast"); // DEV
    errorToast("The transaction could not be added");
  }
};
</script>

<template>
  <div v-focustrap class="card flex justify-center">
    <Form
      v-slot="$form"
      :initialValues
      :resolver
      :validateOnValueUpdate="false"
      :validateOnBlur="false"
      :validateOnMount="false"
      ref="formRef"
      @submit="onFormSubmit"
      class="flex flex-col gap-4 w-full sm:w-80"
    >
      <div class="flex flex-col gap-1">
        <IftaLabel>
          <IconField>
            <InputText
              name="title"
              ref="titleInput"
              id="titleID"
              v-model="initialValues.title"
              placeholder="e.g., Rent"
              fluid
              :disabled="selectedTransaction !== null"
              @input="clearError($form.title)"
              autofocus
            />
            <InputIcon
              v-if="initialValues.title && selectedTransaction === null"
              class="pi pi-times cursor-pointer"
              @click="
                clearField('title', 'title', '');
                titleInput.$el.focus();
              "
            />
          </IconField>
          <label for="titleID" class="font-semibold">Transaction title</label>
        </IftaLabel>
        <Message
          v-if="$form.title?.invalid && !$form.title?.focused"
          severity="secondary"
          size="small"
          variant="simple"
        >
          {{ $form.title.error?.message }}
        </Message>
      </div>

      <div class="flex flex-col gap-1">
        <IftaLabel>
          <IconField>
            <InputText
              name="subtitle"
              ref="subtitleInput"
              id="subtitleID"
              v-model="initialValues.subtitle"
              placeholder="e.g., January"
              fluid
              @input="clearError($form.subtitle)"
            />
            <InputIcon
              v-if="initialValues.subtitle"
              class="pi pi-times cursor-pointer"
              @click="
                clearField('subtitle', 'subtitle', '');
                subtitleInput.$el.focus();
              "
            />
          </IconField>
          <label for="subtitleID" class="font-semibold">Subtitle</label>
        </IftaLabel>
        <Message
          v-if="$form.subtitle?.invalid && !$form.subtitle?.focused"
          severity="secondary"
          size="small"
          variant="simple"
        >
          {{ $form.subtitle.error?.message }}
        </Message>
      </div>

      <div class="flex flex-col gap-1">
        <IftaLabel>
          <IconField>
            <InputNumber
              name="amount"
              inputId="amount"
              ref="amountInput"
              v-model="initialValues.amount"
              mode="currency"
              autocomplete="off"
              :currency="initialValues.accountObj?.currency || 'CHF'"
              locale="en-CH"
              fluid
              @input="
                (e) => {
                  initialValues.amount = e.value;
                  clearError($form.amount);
                }
              "
              @focus="onBalanceFocus"
            />
            <InputIcon
              v-if="
                initialValues.amount !== 0.0 && initialValues.amount !== null
              "
              class="pi pi-times cursor-pointer"
              @click="
                clearField('amount', 'amount');
                amountInput.$el.querySelector('input').focus();
              "
            />
          </IconField>
          <label for="balance" class="font-semibold">Amount</label>
        </IftaLabel>
        <Message
          v-if="$form.amount?.invalid && !$form.amount?.focused"
          severity="secondary"
          size="small"
          variant="simple"
        >
          {{ $form.amount.error?.message }}
        </Message>
      </div>

      <div class="flex flex-col gap-1">
        <IftaLabel>
          <IconField>
            <AutoComplete
              inputId="account"
              name="accountObj"
              ref="accountInput"
              v-model="initialValues.accountObj"
              :suggestions="filteredAccounts"
              @keydown.enter.prevent
              @complete="filterAccounts"
              @change="clearError($form.accountObj)"
              :optionLabel="getAccountLabel"
              dropdown
              fluid
            />
            <InputIcon
              v-if="initialValues.accountObj"
              class="pi pi-times cursor-pointer absolute right-12 top-1/2 -translate-y-1/2"
              @click="
                clearField('accountObj', 'accountObj');
                accountInput.$el.querySelector('input').focus();
              "
            />
          </IconField>
          <label for="account" class="font-semibold">Account</label>
        </IftaLabel>
        <Message
          v-if="$form.accountObj?.invalid && !$form.accountObj?.focused"
          severity="secondary"
          size="small"
          variant="simple"
        >
          {{ $form.accountObj.error?.message }}
        </Message>
      </div>

      <div class="flex flex-col gap-1">
        <IftaLabel>
          <IconField>
            <AutoComplete
              inputId="tag"
              name="tagObj"
              ref="tagInput"
              v-model="initialValues.tagObj"
              :suggestions="filteredTags"
              @keydown.enter.prevent
              @complete="filterTags"
              @change="clearError($form.tagObj)"
              :optionLabel="getTagLabel"
              dropdown
              fluid
            />
            <InputIcon
              v-if="initialValues.tagObj"
              class="pi pi-times cursor-pointer absolute right-12 top-1/2 -translate-y-1/2"
              @click="
                clearField('tagObj', 'tagObj');
                tagInput.$el.querySelector('input').focus();
              "
            />
          </IconField>
          <label for="tag" class="font-semibold">Tag</label>
        </IftaLabel>
        <Message
          v-if="$form.tagObj?.invalid && !$form.tagObj?.focused"
          severity="secondary"
          size="small"
          variant="simple"
        >
          {{ $form.tagObj.error?.message }}
        </Message>
      </div>

      <div class="flex flex-col gap-1">
        <IftaLabel>
          <IconField>
            <DatePicker
              name="ts"
              v-model="initialValues.ts"
              inputId="date"
              fluid
              showTime
              hourFormat="24"
              @date-select="clearError($form.ts)"
            />
            <InputIcon
              class="pi pi-calendar-times cursor-pointer"
              @click="clearField('ts', 'ts', new Date())"
            />
          </IconField>
          <label for="date" class="font-semibold">Date</label>
        </IftaLabel>
        <Message
          v-if="$form.ts?.invalid && !$form.ts?.focused"
          severity="secondary"
          size="small"
          variant="simple"
        >
          {{ $form.ts.error?.message }}
        </Message>
      </div>
      <div class="flex gap-2">
        <Button type="submit" severity="secondary" label="Add Transaction" />
      </div>
    </Form>
  </div>
</template>
