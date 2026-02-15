<script setup>
import { ref } from "vue";
import { Form } from "@primevue/forms";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import Message from "primevue/message";
import IftaLabel from "primevue/iftalabel";
import FocusTrap from "primevue/focustrap";

// Custom utils
import { customToaster } from "@/composables/customToast";
import { dataLoaders, apiPost } from "@/composables/api";

// Set-up
const vFocustrap = FocusTrap;
const { successToast, neutralToast, errorToast } = customToaster();
const { loadTags } = dataLoaders();
const { post } = apiPost();

// Values
const initialValues = ref({
  tag_name: "",
});

// Resolver
const resolver = ({ values }) => {
  const errors = {};
  if (!values.tag_name) {
    errors.tag_name = [{ message: "Tag cannot be blank" }];
  }
  return { errors };
};

// Submit
const onFormSubmit = async ({ valid, states, reset }) => {
  if (!valid) {
    neutralToast("Check all fields to submit");
    return;
  }

  const url = "/api/add/tag";
  console.log(JSON.stringify(states)); //DEV
  console.log(states.tag_name.value); //DEV
  const payload = JSON.stringify({ tag_name: states.tag_name.value });
  console.log(payload);
  const response = await post(url, payload);
  console.log(response); // DEV
  if (response.ok) {
    console.log("ok Toast"); // DEV
    successToast(`Tag '${states.tag_name.value}' added`);
    reset();
    await loadTags();
  } else if (response.status === 409) {
    console.log("duplicate warning Toast"); // DEV
    neutralToast("Tag already exists");
    reset();
  } else {
    console.log("something went wrong Toast"); // DEV
    errorToast("The tag could not be added");
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
      class="flex flex-col gap-4 w-full sm:w-80"
    >
      <div class="flex flex-col gap-1">
        <IftaLabel>
          <label for="tag_name" class="font-semibold">Tag Name</label>
          <InputText
            name="tag_name"
            v-model="initialValues.tag_name"
            type="text"
            placeholder="e.g., Groceries"
            fluid
            autofocus
            showClear
          />
        </IftaLabel>
        <Message
          v-if="$form.tag_name?.invalid"
          severity="secondary"
          size="small"
          variant="simple"
        >
          {{ $form.tag_name.error?.message }}
        </Message>
      </div>

      <div class="flex gap-2">
        <Button type="submit" severity="secondary" label="Add Tag" />
      </div>
    </Form>
  </div>
</template>
