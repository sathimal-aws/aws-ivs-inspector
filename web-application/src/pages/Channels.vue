<template>
  <div class="col body-head-height">
    <div class="row full-height" v-if="channels">
      <!-- left column -->
      <div class="column col-auto border-right" style="min-width: 360px">
        <!-- header -->
        <div class="col-auto q-pt-sm">
          <q-item class="q-py-none">
            <q-item-section>
              <q-item-label class="text-h6"> Channels </q-item-label>
            </q-item-section>

            <q-item-section side>
              <q-btn
                :label="
                  channelsNextToken?.length
                    ? 'Load more'
                    : 'All channels loaded'
                "
                outline
                rounded
                no-caps
                :loading="loading"
                @click="getChannels"
                :disabled="!channelsNextToken?.length"
              />
            </q-item-section>
          </q-item>
        </div>

        <q-separator />

        <!-- search channel input -->
        <div class="col-auto q-pa-sm">
          <q-input
            dense
            rounded
            outlined
            v-model="searchChannel"
            placeholder="Search"
            class="text-theme"
            clearable
          >
            <template v-slot:append>
              <q-avatar>
                <q-icon size="sm" name="search" />
              </q-avatar>
            </template>
          </q-input>
        </div>

        <q-separator color="primary" />

        <!-- channel list -->
        <div class="col" v-if="true">
          <q-scroll-area class="full-height" :thumb-style="thumbStyle">
            <q-table
              class="col"
              grid
              hide-header
              :rows="Object.values(channels)"
              :columns="columns"
              row-key="channelId"
              :loading="loading"
              :filter="searchChannel"
              hide-pagination
              :rows-per-page-options="[0]"
            >
              <template v-slot:item="props">
                <q-item
                  :active="
                    currentChannel.channelId ==
                    props.row.channelConfig.channelId
                  "
                  active-class="bg-grey-2"
                  class="q-pa-none col-12"
                  style="max-width: 360px"
                  clickable
                  @click="showChannelDetails(props.row.channelConfig)"
                >
                  <div class="col">
                    <q-item class="col q-px-none">
                      <q-item-section class="q-px-sm text-left">
                        <q-item-label class="col text-theme text-caption">
                          Channel ID
                        </q-item-label>
                        <q-item-label lines="1" class="text-grey-9">
                          {{ props.row.channelConfig.channelId }}
                        </q-item-label>
                      </q-item-section>

                      <q-separator vertical />

                      <q-item-section class="col-auto q-px-sm text-center">
                        <q-item-label class="col text-theme text-caption">
                          Latency
                        </q-item-label>
                        <q-item-label lines="1" class="text-grey-9">
                          {{ props.row.channelConfig.latencyMode }}
                        </q-item-label>
                      </q-item-section>

                      <q-separator vertical />

                      <q-item-section class="col-auto q-px-sm text-right">
                        <q-item-label class="col text-theme text-caption">
                          Playback Auth
                        </q-item-label>
                        <q-item-label lines="1" class="text-grey-9">
                          {{ props.row.channelConfig.authorized }}
                        </q-item-label>
                      </q-item-section>
                    </q-item>

                    <q-separator />

                    <q-item class="col q-px-none">
                      <q-item-section class="col q-px-sm text-left">
                        <q-item-label class="col text-theme text-caption">
                          Channel Name
                        </q-item-label>
                        <q-item-label lines="1" class="text-grey-9">
                          {{ props.row.channelConfig.name }}
                        </q-item-label>
                      </q-item-section>

                      <q-separator vertical />

                      <q-item-section class="col-auto q-px-sm text-right">
                        <q-item-label class="col text-theme text-caption">
                          Type
                        </q-item-label>
                        <q-item-label lines="1" class="text-grey-9">
                          {{ props.row.channelConfig.type }}
                        </q-item-label>
                      </q-item-section>
                    </q-item>

                    <q-separator color="primary" />
                  </div>
                </q-item>
              </template>
            </q-table>
          </q-scroll-area>
        </div>
      </div>

      <!-- right column - channel config & sessions -->
      <q-scroll-area class="col full-height" :thumb-style="thumbStyle">
        <q-tab-panels
          keep-alive
          v-model="currentChannel.channelId"
          transition-prev="jump-up"
          transition-next="jump-up"
        >
          <q-tab-panel class="q-pb-sm" :name="currentChannel.channelId">
            <channel-details-summary :channel="currentChannel" />
          </q-tab-panel>
        </q-tab-panels>
      </q-scroll-area>
    </div>
  </div>
</template>

<script>
import { date } from "quasar";
import { defineComponent, computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useChannelStore } from "src/stores/store-channel";
import { useCommonStore } from "src/stores/store-common";
import ChannelDetailsSummary from "src/components/Channels/ChannelDetailsSummary.vue";

export default defineComponent({
  name: "ChannelList",

  setup() {
    const channelStore = useChannelStore();
    const commonStore = useCommonStore();
    const $route = useRoute();
    const $router = useRouter();
    const awsRegion = $route.params.region;
    const awsAccountId = $route.params.account_id;

    //     interface channelList{
    // channelConfig:map
    //     }

    const channels = computed(() => channelStore.channels[awsRegion]);
    // console.log("channels:", channels.value);
    // const channelList = computed(() => Object.values(channels.value));
    const channelsNextToken = computed(
      () => channelStore.channelsNextToken[awsRegion]
    );

    const columns = [
      {
        name: "channelId",
        required: true,
        label: "Channel ID",
        align: "left",
        field: (row) => row["channelConfig"].channelId,
        format: (val) => `${val}`,
        sortable: true,
      },

      {
        name: "name",
        required: true,
        label: "Channel Name",
        align: "left",
        field: (row) => row["channelConfig"].name,
        format: (val) => `${val}`,
        sortable: true,
      },

      {
        name: "authorized",
        required: true,
        label: "Authorized",
        align: "left",
        field: (row) => row["channelConfig"].authorized,
        format: (val) => `${val}`,
        sortable: true,
      },

      {
        name: "latencyMode",
        required: true,
        label: "Latency Mode",
        align: "left",
        field: (row) => row["channelConfig"].latencyMode,
        format: (val) => `${val}`,
        sortable: true,
      },

      {
        name: "insecureIngest",
        label: "Insecure Ingest",
        field: "insecureIngest",
        align: "left",
        sortable: true,
      },

      {
        name: "arn",
        label: "Channel ARN",
        field: "arn",
        align: "left",
        sortable: true,
      },

      {
        name: "type",
        label: "Channel Type",
        field: (row) => row["channelConfig"].type,
        align: "left",
        sortable: true,
      },
    ];

    const loading = ref(false);

    const dateManipulate = (dateToConvert) =>
      date.formatDate(dateToConvert, "DD/MMM/YYYY - hh:mm:ss");

    const goToChannelDetails = (channel) => {
      console.log(channel);
      const channelId = channel.arn.split("/")[1];
      $router.push({
        name: "ChannelDetails",

        params: {
          account_id: awsAccountId,
          region: awsRegion,
          channel_id: channelId,
        },
      });
    };

    const currentChannel = ref("");

    const showChannelDetails = (data) => {
      currentChannel.value = data;
    };

    const getChannels = () => {
      loading.value = true;
      channelStore.getChannels(awsRegion).then((res) => {
        if (res) console.log("channels successfully listed!");
        loading.value = false;
      });
    };

    onMounted(() => {
      console.log("channels:", channels.value);
      if (
        !channels.value ||
        (channels.value && Object.keys(channels.value) < 2)
      ) {
        getChannels();
      }
    });

    return {
      channels,
      // channelList: Object.values(channels.value),
      channelsNextToken,
      columns,
      loading,

      initialPagination: commonStore.initialPagination,
      thumbStyle: commonStore.thumbStyle,

      searchChannel: ref(""),
      currentChannel,

      dateManipulate,
      goToChannelDetails,
      showChannelDetails,
      getChannels,
    };
  },

  components: { ChannelDetailsSummary },
});
</script>

<style lang="sass">
.my-sticky-header-table
  /* height or max-height is important */
  height: calc( 100vh - 120px )

  .q-table__top,
  .q-table__bottom,
  thead tr:first-child th
    /* bg color is important for th; just specify one */
    background-color: #fff

  thead tr th
    position: sticky
    z-index: 1
  thead tr:first-child th
    top: 0

  /* this is when the loading indicator appears */
  &.q-table--loading thead tr:last-child th
    /* height of all previous header rows */
    top: 48px

  /* prevent scrolling behind sticky top row on focus */
  tbody
    /* height of all previous header rows */
    scroll-margin-top: 48px
    background-color: $grey-2
</style>
