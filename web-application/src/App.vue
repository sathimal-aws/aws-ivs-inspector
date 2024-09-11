<template>
  <router-view />
</template>

<script>
import { defineComponent, onMounted, ref } from "vue";
// import { fetchUserAttributes } from "aws-amplify/auth";
import { useRouter } from "vue-router";
// import { useAuthStore } from "src/stores/store-auth";

export default defineComponent({
  name: "App",

  setup() {
    // const $router = useRouter();
    // const authStore = useAuthStore();
    onMounted(() => {
      // authStore
      //   .isUserSignedIn()
      //   .then((res) => console.log(console.log("isUserSignedIn Res", res)));
      // console.log("env var:", import.meta.env);
      // fetchUserAttributes().then((res) => {
      //   console.log("fetch User Attributes: ", res);
      //   if (!res.email) {
      //     $router.push({
      //       name: "Auth",
      //     });
      //   }
      // });
    });
  },
});
</script>
