<template>
  <div class="col">
    <div class="row">
      <div class="column col-auto border-right" style="min-width: 360px">
        <!-- header -->
        <div class="col-auto q-pt-sm">
          <q-item class="q-py-none">
            <q-item-section>
              <q-item-label class="text-h6"> Live Channels </q-item-label>
            </q-item-section>

            <q-item-section side>
              <q-btn
                :label="streamsNextToken ? 'Load more' : 'All channels loaded'"
                outline
                rounded
                no-caps
                :loading="loading"
                @click="getChannels()"
                :disabled="!streamsNextToken"
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
        <div class="col" v-if="liveSessions">
          <q-scroll-area
            style="height: calc(100vh - 230px)"
            :thumb-style="thumbStyle"
          >
            <q-table
              class="col"
              grid
              bordered
              hide-header
              :rows="Object.values(liveSessions)"
              :columns="columns"
              row-key="channelId"
              :loading="loading"
              :filter="searchChannel"
              hide-pagination
              :rows-per-page-options="[0]"
            >
              <template v-slot:item="props">
                <q-item
                  :active="currentChannel.channelId == props.row.channelId"
                  active-class="bg-grey-2"
                  class="q-pa-none col-12"
                  style="max-width: 360px"
                  clickable
                  @click="showChannelDetails(props.row)"
                >
                  <div class="col">
                    <q-item class="col q-px-none">
                      <q-item-section class="q-px-sm text-left">
                        <q-item-label class="col text-theme text-caption">
                          Channel ID
                        </q-item-label>
                        <q-item-label lines="1" class="text-grey-9">
                          {{ props.row.channelId }}
                        </q-item-label>
                      </q-item-section>

                      <q-separator vertical />

                      <q-item-section class="col-auto q-px-sm text-right">
                        <q-item-label class="col text-theme text-caption">
                          Start Time
                        </q-item-label>
                        <q-item-label lines="1" class="text-grey-9">
                          {{
                            dateManipulate(
                              props.row.startTime,
                              "DD MMM YYYY, HH:mm:ss"
                            )
                          }}
                        </q-item-label>
                      </q-item-section>
                    </q-item>

                    <q-separator />

                    <q-item class="col q-px-none">
                      <q-item-section class="col q-px-sm text-left">
                        <q-item-label class="col text-theme text-caption">
                          Stream ID
                        </q-item-label>
                        <q-item-label lines="1" class="text-grey-9">
                          {{ props.row.streamId }}
                        </q-item-label>
                      </q-item-section>

                      <q-separator vertical />

                      <q-item-section class="col-auto q-px-sm text-right">
                        <q-item-label class="col text-theme text-caption">
                          State
                        </q-item-label>
                        <q-item-label lines="1" class="text-grey-9">
                          {{ props.row.state }}
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

      <!-- channel details summary -->
      <div class="col">
        <q-scroll-area
          style="height: calc(100vh - 75px)"
          :thumb-style="thumbStyle"
        >
          <q-tab-panels
            v-model="currentChannel.channelId"
            animated
            vertical
            transition-prev="jump-up"
            transition-next="jump-up"
          >
            <q-tab-panel
              class="q-py-sm q-px-none"
              :name="currentChannel.channelId"
            >
              <channel-config :channel="currentChannel" />
            </q-tab-panel>
          </q-tab-panels>
        </q-scroll-area>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useSessionStore } from "src/stores/store-session";
import { useCommonStore } from "src/stores/store-common";
import { date } from "quasar";
import ChannelConfig from "src/components/Channels/ChannelConfig.vue";

export default defineComponent({
  name: "LiveChannelList",

  setup() {
    const sessionStore = useSessionStore();
    const commonStore = useCommonStore();
    const $route = useRoute();
    const $router = useRouter();
    const awsRegion = $route.params.region;
    const awsAccountId = $route.params.account_id;

    const liveSessions = computed(() => sessionStore.liveSessions[awsRegion]);
    const streamsNextToken = computed(
      () => sessionStore.streamsNextToken[awsRegion]
    );

    const columns = [
      {
        name: "name",
        required: true,
        label: "Channel Name",
        align: "left",
        field: (row) => row.name,
        format: (val) => `${val}`,
        sortable: true,
      },

      {
        name: "authorized",
        required: true,
        label: "Authorized",
        align: "left",
        field: (row) => row.authorized,
        format: (val) => `${val}`,
        sortable: true,
      },

      {
        name: "latencyMode",
        required: true,
        label: "Latency Mode",
        align: "left",
        field: (row) => row.latencyMode,
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
    ];

    const loading = ref(false);

    const dateManipulate = (dateToConvert) =>
      date.formatDate(dateToConvert, "DD/MMM/YYYY - HH:mm:ss");

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

    onMounted(() => {
      sessionStore.getLiveStreams(awsRegion).then((res) => {
        console.log(res);
      });
      if (
        !liveSessions.value ||
        (liveSessions.value && Object.keys(liveSessions.value) < 2)
      ) {
        loading.value = true;
        sessionStore.listStreams(awsRegion).then((res) => {
          if (res) console.log("live channels successfully listed!");
          loading.value = false;
        });
      }
    });

    return {
      streamsNextToken,
      liveSessions,
      columns,
      searchChannel: ref(""),
      currentChannel,
      loading,
      initialPagination: commonStore.initialPagination,
      thumbStyle: commonStore.thumbStyle,

      dateManipulate,
      goToChannelDetails,
      showChannelDetails,
    };
  },

  components: { ChannelConfig },
});
</script>
