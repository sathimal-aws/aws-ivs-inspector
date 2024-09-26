import { defineStore } from "pinia";
import {
  signIn,
  getCurrentUser,
  fetchAuthSession,
  signOut,
} from "aws-amplify/auth";
import { computed } from "vue";
import { useCommonStore } from "./store-common";

const commonStore = useCommonStore();
const ivsRegions = computed(() => commonStore.regions);

export const useAuthStore = defineStore("AuthStore", {
  state: () => ({
    userSignedIn: false,
    userState: null,
    user: null,
    accessToken: null,
  }),

  actions: {
    async isUserSignedIn() {
      try {
        return await getCurrentUser().then(async (userRes) => {
          // console.log("user Response:", userRes);
          if (userRes.userId) {
            return await fetchAuthSession().then((fetchAuthSessionRes) => {
              this.accessToken =
                fetchAuthSessionRes.tokens?.idToken?.toString();
              this.user = userRes;
              this.userSignedIn = true;
              return true;
            });
          }
        });
      } catch (err) {
        console.log("err: ", err.message);
        this.router.push({
          name: "Auth",
        });
        return err;
      }
    },

    async userSignIn(payload) {
      try {
        const signInResponse = await signIn({
          username: payload.email,
          password: payload.password,
        });

        console.log(signInResponse.isSignedIn);
        if (signInResponse.isSignedIn) {
          getCurrentUser().then((res) => {
            console.log(res);
            this.user = res;
            console.log("redirect:", this.route?.query?.redirect);
            this.router.push(
              this.route?.query?.redirect || {
                name: "Dashboard",
                params: {
                  account_id: "740024244647",
                  region: ivsRegions.value[0],
                },
              }
            );
          });
        }

        return true;
      } catch (error) {
        console.log("error signing in", error);
      }

      return true;
    },

    async userSignOut() {
      console.log("user sign out called");
      try {
        return signOut().then(() => {
          this.user = null;
          return true;
        });
      } catch (error) {
        console.log("error sign out", error);
        return error;
      }
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
