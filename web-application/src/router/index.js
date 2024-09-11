import { route } from "quasar/wrappers";
import {
  createRouter,
  createMemoryHistory,
  createWebHistory,
  createWebHashHistory,
} from "vue-router";
import routes from "./routes";

// - AMPLIFY -
import { Amplify } from "aws-amplify";
import { fetchAuthSession } from "aws-amplify/auth";
import { AmplifyConfig } from "../config/amplify-config"; // NO TOUCHY
Amplify.configure(AmplifyConfig);

// console.log(Amplify.getConfig());

export default route(function ({ store }) {
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

  Router.beforeResolve((to, from, next) => {
    const commonStore = store.state.value.CommonStore;
    // console.log("commonStore:", commonStore);

    if (to.meta.auth) {
      console.log("this route is protected!", to.fullPath);

      fetchAuthSession()
        .then((res) => {
          if (res.credentials) {
            console.log("accessToken:", res.tokens?.idToken?.toString());
            commonStore.access_token = res.tokens?.idToken?.toString();
            next();
          }
        })
        .catch(() => {
          console.log("User is not authenticated");
          next({
            name: "Auth",
          });
        });
    } else next();
  });

  return Router;
});
