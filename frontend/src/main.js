import { createApp } from "vue";
import Aura from "@primeuix/themes/aura";
import PrimeVue from "primevue/config";
import ToastService from "primevue/toastservice";
import { definePreset } from "@primeuix/themes";

import App from "@/App.vue";
import router from "@/router";

import "primeicons/primeicons.css";
import "@/style.css";

const app = createApp(App);

const customAura = definePreset(Aura, {
  semantic: {
    colorScheme: {
      light: {
        formField: {
          focusBorderColor: "{neutral.700}",
          invalidBorderColor: "{rose.800}",
          invalidPlaceholderColor: "{form.field.placeholder.color}",
        },
      },
      dark: {
        formField: {
          focusBorderColor: "{neutral.50}",
        },
      },
    },
  },
});

app.use(PrimeVue, {
  theme: {
    preset: customAura,
    options: {
      cssLayer: {
        name: "primevue",
        order: "tailwind-base, primevue, tailwind-utilities",
      },
    },
  },
  locale: {
    firstDayOfWeek: 1,
  },
});
app.use(ToastService);
app.use(router);
app.mount("#app");
