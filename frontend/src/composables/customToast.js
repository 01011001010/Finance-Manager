// TODO unify toast type use, improve design
import { useToast } from "primevue/usetoast";

export function customToaster() {
  const toast = useToast();

  const bakeToast = (type, title, message) => {
    toast.add({
      severity: type,
      summary: title,
      detail: message,
      life: 1500,
    });
  };

  const successToast = (message) => bakeToast("success", null, message);
  const neutralToast = (message) => bakeToast("secondary", null, message);
  const errorToast = (message) =>
    bakeToast("error", "Something went wrong", message);

  return { successToast, neutralToast, errorToast };
}
