<script setup>
import { ref } from "vue";
import { Form } from "@primevue/forms";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import Message from "primevue/message";
import FocusTrap from "primevue/focustrap";
// Custom
import { customToaster } from "@/composables/customToast";
import { dataLoaders, apiPost } from "@/composables/api";

// Focus Trap
const vFocustrap = FocusTrap;

// Toast
const { successToast, neutralToast, errorToast } = customToaster();

// Data loading
const { loadTags } = dataLoaders();

// API POST
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
  if (!valid) return;

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
      class="flex flex-col gap-4 w-full sm:w-56"
    >
      <div class="flex flex-col gap-1">
        <label for="tag_name" class="font-semibold">Tag Name</label>
        <InputText
          name="tag_name"
          type="text"
          placeholder="e.g., Groceries"
          fluid
          autofocus
          showClear
        />
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
