<template>
  <q-layout view="lHh LpR lFf" class="Layout">
    <q-header bordered class="bg-white text-grey-9">
      <q-toolbar class="q-pr-none">
        <q-item-section avatar>
          <q-img src="icons/ivs.png" />
        </q-item-section>

        <q-item-section>
          <q-item-label
            lines="1"
            title
            :class="$q.screen.gt.sm ? 'text-h5' : 'text-body1'"
          >
            IVS - {{ $route.name }}
          </q-item-label>
        </q-item-section>

        <q-item-section class="col-auto gt-xs">
          <div class="row">
            <q-input
              class="col-auto"
              v-model="accountId"
              filled
              square
              label="Account ID"
            >
            </q-input>

            <q-separator vertical />

            <q-select
              class="col-auto"
              style="width: 160px"
              v-model="region"
              dropdown-icon="keyboard_arrow_down"
              filled
              square
              :options="ivsRegions"
              label="Region"
              @update:model-value="changeRegion"
            />
          </div>
        </q-item-section>

        <q-btn
          class="lt-sm"
          dense
          flat
          round
          icon="menu"
          @click="toggleLeftDrawer"
        />
      </q-toolbar>
    </q-header>

    <q-drawer
      show-if-above
      :mini="miniState"
      @mouseover="miniState = false"
      @mouseout="miniState = true"
      v-model="drawer"
      :width="200"
      side="left"
      :behavior="$q.screen.lt.sm ? 'mobile' : 'desktop'"
      bordered
    >
      <q-list class="column col full-height">
        <q-item clickable class="col-auto q-px-md q-py-sm" style="height: 56px">
          <q-item-section avatar>
            <q-icon name="o_account_circle" />
          </q-item-section>

          <q-item-section>
            <q-item-label> {{ user?.username }} </q-item-label>
            <q-item-label caption lines="1">
              {{ user?.signInDetails?.loginId }}
            </q-item-label>
          </q-item-section>
        </q-item>

        <q-separator />

        <div class="col">
          <navigation
            class="col"
            v-for="link in navigation"
            :key="link.title"
            v-bind="link"
          />
        </div>

        <q-separator />

        <q-item
          clickable
          class="col-auto q-pa-md"
          @click="signOutAndRedirectTo"
        >
          <q-item-section avatar>
            <q-icon name="logout" />
          </q-item-section>

          <q-item-section>
            <q-item-label> Logout </q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { computed, defineComponent, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAccountStore } from "src/stores/store-account";
import { useCommonStore } from "src/stores/store-common";
import { useAuthStore } from "src/stores/store-auth";

import Navigation from "src/components/HomeComponents/Navigation.vue";

export default defineComponent({
  name: "MainLayout",

  components: {
    Navigation,
  },

  setup() {
    const authStore = useAuthStore();
    const accountStore = useAccountStore();
    const commonStore = useCommonStore();
    const user = computed(() => authStore.user);

    const navigationList = computed(() => [
      {
        title: "Dashboard",
        icon: "dashboard",
        link: `/account/${accountId.value}/region/${region.value}/dashboard`,
      },
      {
        title: "Channels",
        icon: "ballot",
        link: `/account/${accountId.value}/region/${region.value}/channels`,
      },

      {
        title: "Live Channels",
        icon: "settings_input_antenna",
        link: `/account/${accountId.value}/region/${region.value}/live_channels`,
      },
    ]);

    const $route = useRoute();
    const $router = useRouter();
    const drawer = ref(false);

    const accountId = computed(() => commonStore.account_id);
    const region = ref($route.params.region);
    const channelId = ref(null);
    const ivsRegions = computed(() => commonStore.regions);

    const goToChannel = () => {
      if (channelId.value.length) {
        $router.push({
          name: "ChannelDetails",
          params: { channel_id: channelId.value },
        });
      }
    };

    const changeRegion = (newRegion) => {
      $router.push({
        name: "Dashboard",
        params: {
          account_id: accountId.value,
          region: region.value,
        },
      });

      $router.beforeResolve((to, from, next) => {
        const metrics = computed(() => accountStore.metrics[newRegion]);

        if (!metrics.value?.length) {
          accountStore.getMetrics(newRegion);
        }

        const quotasProvisioned = computed(
          () => accountStore.accountQuotas[newRegion]
        );

        if (!quotasProvisioned.value?.length) {
          accountStore.getQuotaProvisioned("ivs", newRegion);
        }

        next();
      });
    };

    const redirectTo = (page) => {
      $router.push({ name: page });
    };

    const signOutAndRedirectTo = () => {
      authStore.userSignOut().then((userSignOutRes) => {
        console.log("userSignedOut", userSignOutRes);
        if (userSignOutRes) {
          $router.push({ name: "Auth" });
        }
      });
    };

    return {
      user,
      navigation: navigationList,
      miniState: ref(true),
      drawer,
      toggleLeftDrawer() {
        drawer.value = !drawer.value;
      },

      accountId,
      region,
      channelId,
      ivsRegions,

      goToChannel,
      changeRegion,
      redirectTo,
      signOutAndRedirectTo,
    };
  },
});
</script>

<style lang="sass">
.Layout
  width: 100%
  height: 100vh
  background-color: white
  color: $grey-9

.ivs-bg-grey
  background-color: $grey-2

.border
  border: 1px solid $grey-4

.border-right
  border-right: 1px solid $grey-3

.body-spacing
  padding: 15px 15px

.body-head-height
  height: calc( 100vh - 58px )

.animated
    animation-duration: 1s
    animation-fill-mode: both
    -webkit-animation-duration: 1s
    -webkit-animation-fill-mode: both
</style>
