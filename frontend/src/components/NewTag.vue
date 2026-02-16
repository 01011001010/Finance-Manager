<script setup>
import { ref, nextTick } from "vue";
import { Form } from "@primevue/forms";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import Message from "primevue/message";
import IftaLabel from "primevue/iftalabel";
import FocusTrap from "primevue/focustrap";
import IconField from "primevue/iconfield";
import InputIcon from "primevue/inputicon";

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

// Autofocus on clear
const tagInput = ref(null);
const clearError = async (formObj) => {
  if (formObj) {
    await nextTick();
    formObj.invalid = false;
    formObj.error = null;
    formObj.errors = [];
  }
};

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
    await loadTags();
    reset();
    await nextTick();
    if (tagInput.value) {
      const inputRef =
        tagInput.value.$el?.querySelector("input") ||
        tagInput.value.$el ||
        tagInput.value;
      if (inputRef.focus === "function") {
        inputRef.focus();
      }
    }
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
          <IconField>
            <InputText
              name="tag_name"
              type="text"
              ref="tagInput"
              placeholder="e.g., Groceries"
              fluid
              autofocus
              showClear
            />
            <InputIcon
              v-if="$form.tag_name?.value"
              class="pi pi-times cursor-pointer"
              @click="
                $form.tag_name.value = '';
                tagInput.$el.focus();
                clearError($form.tag_name);
              "
            />
          </IconField>
          <label for="tag_name" class="font-semibold">Tag Name</label>
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
