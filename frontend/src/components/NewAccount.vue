<script setup>
import { ref, nextTick } from "vue";
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
import { getData, apiPost } from "@/composables/api";

// Set-up
const vFocustrap = FocusTrap;
const { successToast, neutralToast, errorToast } = customToaster();
const { loadAccounts } = getData();
const { post } = apiPost();

// Values
// Note: It is not advised to use Form v-slot with v-model for the individual inputs.
//       Unfortunately, the formatting of monetary or date inputs is not working without v-model at the moment.
//       A hybrid approach was chosen for as the best option for now
const initialValues = ref({
  name: "",
  currency: "CHF",
  balance: 0.0,
  ts: new Date(),
});
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

// Currencies
const allCurrencies = Intl.supportedValuesOf("currency");
const filteredCurrencies = ref([]);
const filterCurrency = (e) => {
  const query = e.query.toUpperCase();
  filteredCurrencies.value = allCurrencies.filter((c) => c.includes(query));
};

// Autofocus on clear
const nameInput = ref(null);
// const balanceInput = ref(null);  // clear sets to 0.0 and does not put focus on the field
const currencyInput = ref(null);

const onBalanceFocus = (event) => {
  setTimeout(() => {
    if (event.target && typeof event.target.select === "function") {
      // Select contents on focus to prevent cursor starting at the end of existing value
      event.target.select();
    }
  }, 50);
};

// Resolver
const resolver = ({ values }) => {
  console.log("RESOLVER"); // DEV
  console.log(values); // DEV
  const errors = {};

  if (!values.name?.trim()) {
    errors.name = [{ message: "Account name is required" }];
  }

  if (values.balance === null || values.balance === undefined) {
    errors.balance = [{ message: "Initial balance is required" }];
  }

  if (!values.currency) {
    errors.currency = [{ message: "Currency is required" }];
  } else if (
    values.currency.length === 3 &&
    !allCurrencies.includes(values.currency.toUpperCase())
  ) {
    errors.currency = [{ message: "Invalid currency code" }];
  }

  if (!values.ts) {
    errors.ts = [{ message: "Opening date is required" }];
  }

  return { errors };
};

// Submit Handler
const onFormSubmit = async ({ valid, states, reset }) => {
  if (!valid) {
    neutralToast("Check all fields to submit");
    return;
  }

  const url = "/api/add/account";

  const midnight = new Date(states.ts.value);
  midnight.setHours(0, 0, 0, 0);

  const payload = {
    name: states.name.value,
    currency: states.currency.value,
    balance: states.balance.value,
    ts: midnight.toISOString(),
  };

  // console.log(payload); // DEV
  const response = await post(url, JSON.stringify(payload));
  // console.log(response); // DEV

  if (response.ok) {
    // console.log("ok Toast"); // DEV
    successToast(`Account '${payload.name} (${payload.currency})' added`);
    await loadAccounts();
    initialValues.value.name = "";
    initialValues.value.balance = 0.0;
    reset();
    await nextTick();
    if (nameInput.value) {
      const inputRef =
        nameInput.value.$el?.querySelector("input") ||
        nameInput.value.$el ||
        nameInput.value;
      if (inputRef.focus === "function") {
        inputRef.focus();
      }
    }
  } else if (response.status === 409) {
    // console.log("duplicate warning Toast"); // DEV
    neutralToast("An account with this name and currency already exists");
  } else {
    // console.log("something went wrong Toast"); // DEV
    errorToast("The account could not be added");
  }
};
</script>

<template>
  <div v-focustrap class="card flex justify-center">
    <Form
      v-slot="$form"
      :initialValues
      :resolver
      @submit="onFormSubmit"
      :validateOnValueUpdate="false"
      :validateOnBlur="false"
      :validateOnMount="false"
      class="flex flex-col gap-4 w-full sm:w-80"
    >
      <div class="flex flex-col gap-1">
        <IftaLabel>
          <IconField>
            <DatePicker
              name="ts"
              v-model="initialValues.ts"
              inputId="date"
              fluid
              dateFormat="dd/mm/yy"
              @date-select="clearError($form.ts)"
            />
            <InputIcon
              class="pi pi-calendar-times cursor-pointer"
              @click="clearField('ts', 'ts', new Date())"
            />
          </IconField>
          <label for="date" class="font-semibold">Opening Date</label>
        </IftaLabel>
        <Message
          v-if="$form.ts?.invalid"
          severity="secondary"
          size="small"
          variant="simple"
        >
          {{ $form.ts.error?.message }}
        </Message>
      </div>
      <div class="flex flex-col gap-1">
        <IftaLabel>
          <IconField>
            <InputText
              name="name"
              ref="nameInput"
              id="nameID"
              v-model="initialValues.name"
              placeholder="e.g., Cash"
              fluid
              autofocus
              @input="clearError($form.name)"
            />
            <InputIcon
              v-if="initialValues.name"
              class="pi pi-times cursor-pointer"
              @click="
                clearField('name', 'name');
                nameInput.$el.focus();
              "
            />
          </IconField>
          <label for="nameID" class="font-semibold">Account Name</label>
        </IftaLabel>
        <Message
          v-if="$form.name?.invalid"
          severity="secondary"
          size="small"
          variant="simple"
        >
          {{ $form.name.error?.message }}
        </Message>
      </div>
      <div class="flex flex-col gap-1">
        <IftaLabel>
          <IconField>
            <AutoComplete
              inputId="currency"
              name="currency"
              ref="currencyInput"
              v-model="initialValues.currency"
              :suggestions="filteredCurrencies"
              @keydown.enter.prevent
              @complete="filterCurrency"
              @change="clearError($form.currency)"
              @input="
                initialValues.currency = initialValues.currency.toUpperCase();
                $form.currency.value = initialValues.currency;
              "
              placeholder="e.g., CHF"
              fluid
            />
            <InputIcon
              v-if="initialValues.currency"
              class="pi pi-times cursor-pointer"
              @click="
                clearField('currency', 'currency');
                currencyInput.$el.querySelector('input').focus();
              "
            />
          </IconField>
          <label for="currency" class="font-semibold">Currency</label>
        </IftaLabel>
        <Message
          v-if="$form.currency?.invalid"
          severity="secondary"
          size="small"
          variant="simple"
        >
          {{ $form.currency.error?.message }}
        </Message>
      </div>

      <div class="flex flex-col gap-1">
        <IftaLabel>
          <IconField>
            <InputNumber
              name="balance"
              inputId="balance"
              ref="balanceInput"
              v-model="initialValues.balance"
              mode="currency"
              autocomplete="off"
              :currency="
                initialValues.currency?.length === 3
                  ? initialValues.currency
                  : 'CHF'
              "
              locale="en-CH"
              fluid
              @input="
                (e) => {
                  initialValues.balance = e.value;
                  clearError($form.balance);
                }
              "
              @focus="onBalanceFocus"
            />
            <InputIcon
              v-if="
                initialValues.balance !== 0.0 && initialValues.balance !== null
              "
              class="pi pi-times cursor-pointer"
              @click="clearField('balance', 'balance', 0.0)"
            />
          </IconField>
          <label for="balance" class="font-semibold">Initial Balance</label>
        </IftaLabel>
        <Message
          v-if="$form.balance?.invalid"
          severity="secondary"
          size="small"
          variant="simple"
        >
          {{ $form.balance.error?.message }}
        </Message>
      </div>

      <div class="flex gap-2">
        <Button type="submit" severity="secondary" label="Add Account" />
      </div>
    </Form>
  </div>
</template>
