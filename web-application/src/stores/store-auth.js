import { defineStore } from "pinia";
import {
  signIn,
  signInWithRedirect,
  getCurrentUser,
  fetchAuthSession,
  autoSignIn,
  confirmSignIn,
  signOut,
} from "aws-amplify/auth";
import { computed, ref } from "vue";
import { useCommonStore } from "./store-common";

const commonStore = useCommonStore();
const accountId = computed(() => commonStore.account_id);
const ivsRegions = computed(() => commonStore.regions);

export const useAuthStore = defineStore("AuthStore", {
  state: () => ({
    userSignedIn: false,
    userState: null,
    user: null,
  }),

  actions: {
    async isUserSignedIn() {
      try {
        await getCurrentUser().then(async (userRes) => {
          console.log("user Response:", userRes);
          this.user = userRes;
          if (userRes.userId) {
            const session = await fetchAuthSession();
            console.log("session:", session);
            // await fetchAuthSession().then((fetchAuthSessionRes) => {
            //   console.log("fetchAuthSessionRes:", fetchAuthSessionRes);
            // });
          }
        });
        return true;
      } catch (err) {
        console.log("err: ", err);
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
      //         commit("setUserState", res.attributes);
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
        signOut().then(() => {
          this.user = null;

          // this.router.beforeEach(async (from, to) => {
          //   console.log(from, to);
          //   return true;
          // });
          this.router.push({ name: "Auth" });
        });
        return true;
      } catch (error) {
        console.log("error sign out", error);
        return error;
      }
    },

    setUserState(state) {
      this.userState = state;
    },

    clearUserState(state) {
      this.userState = null;
    },
  },
});
