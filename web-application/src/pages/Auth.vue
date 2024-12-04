<template>
  <div class="col body-spacing">
    <authenticator initial-state="signIn" :form-fields="formFields">
      <template v-slot:header>
        <div style="padding: var(--amplify-space-small); text-align: center">
          <q-img width="100px" alt="Amplify logo" src="/icons/ivs.png" />
        </div>
      </template>
    </authenticator>
  </div>
</template>

<script>
import { defineComponent, toRefs, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Authenticator, useAuthenticator } from "@aws-amplify/ui-vue";
import { useCommonStore } from "src/stores/store-common";
import { useAuthStore } from "src/stores/store-auth";
import "@aws-amplify/ui-vue/styles.css";

export default defineComponent({
  name: "UserAuthentication",
  components: { Authenticator },
  setup() {
    const commonStore = useCommonStore();
    const authStore = useAuthStore();
    const { user } = toRefs(useAuthenticator());
    const $router = useRouter();
    const $route = useRoute();

    const formFields = {
      signUp: {
        given_name: {
          order: 1,
        },
        family_name: {
          order: 2,
        },
        email: {
          order: 3,
        },
        password: {
          order: 4,
        },
        confirm_password: {
          order: 5,
        },
      },
    };

    watch(user, (currentValue, oldValue) => {
      if (currentValue?.userId) {
        authStore.setUser(currentValue);

        if ($route.query.redirect && $route.query.redirect !== "MainLayout") {
          const params = {
            account_id: $route.query.account_id,
            region: $route.query.region,
            channel_id: $route.query.channel_id,
            session_id: $route.query.session_id,
          };

          $router.push({
            name: $route.query.redirect,
            params: params,
          });
        } else {
          $router.push(
            `account/${commonStore.account_id}/region/${commonStore.regions[0]}/dashboard`
          );
        }
      }
    });

    return {
      formFields,
      commonStore,
    };
  },
});
</script>

<style>
.amplify-button--primary {
  background: #ff9900;
}

.amplify-tabs__active {
  border-color: #ff9900;
}
</style>
