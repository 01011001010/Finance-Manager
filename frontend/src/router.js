import { createRouter, createWebHistory } from "vue-router";
import Overview from "./views/Overview.vue";
import Log from "./views/Log.vue";

const routes = [
  { path: "/", name: "Overview", component: Overview },
  { path: "/log", name: "LogAdd", component: Log },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
