import { route } from "quasar/wrappers";
import {
  createRouter,
  createMemoryHistory,
  createWebHistory,
  createWebHashHistory,
} from "vue-router";
import routes from "./routes";
import { useAuthStore } from "src/stores/store-auth";

// - AMPLIFY -
import { Amplify } from "aws-amplify";
import { AmplifyConfig } from "../config/amplify-config"; // NO TOUCHY
Amplify.configure(AmplifyConfig);

export default route(async function ({ store }) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === "history"
    ? createWebHistory
    : createWebHashHistory;

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });

  const authStore = useAuthStore(store);

  Router.beforeEach((to, from, next) => {
    if (to.name !== "Auth" && !authStore.userSignedIn)
      next({
        name: "Auth",
        query: {
          redirect: to.name,
          account_id: to.params.account_id,
          region: to.params.region,
          channel_id: to.params.channel_id,
          session_id: to.params.session_id,
        },
      });
    else if (to.name === "MainLayout") {
      console.log("to.params:", to.params);

      next({
        name: "Dashboard",
        params: {
          account_id: to.params.account_id,
          region: to.params.region,
        },
      });
    } else if (to.name == "Auth") {
      next();
    } else {
      authStore.isUserSignedIn().then((res) => {
        // console.log("isUserSignedIn res:", res);
        next();
      });
    }
  });

  return Router;
});
