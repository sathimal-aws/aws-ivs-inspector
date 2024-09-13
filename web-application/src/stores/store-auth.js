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
const accountId = computed(() => commonStore.account_id);
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
          console.log("user Response:", userRes);
          if (userRes.userId) {
            return await fetchAuthSession().then((fetchAuthSessionRes) => {
              this.accessToken =
                fetchAuthSessionRes.tokens?.idToken?.toString();
              // console.log(this.accessToken);
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
      // return fetchAuthSession()
      //   .then((data) => {
      //     console.log("current session: ", data);
      //     return Auth.currentAuthenticatedUser()
      //       .then((res) => {
      //         // res.attributes.status = "loggedIn";
      //         console.log("sign-in attributes: ", res.attributes);
      //         commit("setUser", res.attributes);
      //         this.router.push("/dashboard");
      //       })
      //       .catch((error) => {
      //         console.log("error: ", error);
      //         if (error == "The user is not authenticated") {
      //           this.router.push("/login");
      //           dispatch("clearUserState");
      //         }
      //       });
      //     // .then(() => {
      //     //   return true;
      //     // });
      //   })
    },

    async currentSession() {
      try {
        const { accessToken, idToken } =
          (await fetchAuthSession()).tokens ?? {};

        console.log(accessToken);
      } catch (err) {
        console.log(err);
      }
    },

    async userSignIn(payload) {
      // console.log( "user cred", payload);

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

          // this.router.beforeEach(async (from, to) => {
          //   console.log(from, to);
          //   return true;
          // });
          // this.router.push({ name: "Auth" });
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
