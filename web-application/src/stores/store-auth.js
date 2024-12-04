import { defineStore } from "pinia";
import {
  signIn,
  getCurrentUser,
  fetchAuthSession,
  signOut,
} from "aws-amplify/auth";
import { useRouter } from "vue-router";
import { useCommonStore } from "./store-common";
import { Notify } from "quasar";

const logger = console; // Use console for logging for now
const commonStore = useCommonStore();
const account_id = commonStore.account_id; // No need for computed here
const ivsRegions = commonStore.regions; // No need for computed here

export const useAuthStore = defineStore("AuthStore", {
  state: () => ({
    userSignedIn: false,
    user: null,
    accessToken: null,
  }),

  actions: {
    async isUserSignedIn() {
      try {
        const userRes = await getCurrentUser();
        if (userRes?.userId) {
          const fetchAuthSessionRes = await fetchAuthSession();
          this.accessToken = fetchAuthSessionRes.tokens?.idToken?.toString();
          this.user = userRes;
          this.userSignedIn = true;
          return true;
        }
      } catch (err) {
        logger.error("Error checking user sign-in status:", err.message);
        useRouter().push({ name: "Auth" });
      }
      return false;
    },

    async userSignIn(payload) {
      try {
        const signInResponse = await signIn({
          username: payload.email,
          password: payload.password,
        });

        if (signInResponse.isSignedIn) {
          this.user = await getCurrentUser();
          const router = useRouter();
          router.push(
            router.currentRoute.value.query?.redirect || {
              name: "Dashboard",
              params: {
                account_id: account_id, // Consider making this dynamic
                region: ivsRegions[0],
              },
            }
          );
        }
        return true;
      } catch (error) {
        logger.error("Error signing in:", error);
        Notify.create({
          color: "negative",
          position: "top",
          message: error.message || "Sign-in failed", // Show specific error if available
          icon: "report_problem",
        });
      }
      return false;
    },

    async userSignOut() {
      try {
        await signOut();
        this.user = null;
        this.userSignedIn = false;
        return true;
      } catch (error) {
        logger.error("Error signing out:", error);
      }
      return false;
    },

    setUser(user) {
      this.user = user;
      this.userSignedIn = true;
    },

    clearUser() {
      this.user = null;
      this.userSignedIn = false;
    },
  },
});
