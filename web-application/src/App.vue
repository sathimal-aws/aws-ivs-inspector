<template>
  <router-view />
</template>

<script>
import { defineComponent, onMounted, ref } from "vue";
import { fetchUserAttributes } from "aws-amplify/auth";
import { useRouter } from "vue-router";

export default defineComponent({
  name: "App",

  setup() {
    const $router = useRouter();
    onMounted(() => {
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
