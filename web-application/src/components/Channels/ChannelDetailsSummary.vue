<template>
  <div class="column col q-gutter-y-lg body-head-height">
    <div class="col-auto">
      <q-card flat>
        <q-card-section class="q-pa-sm">
          <q-item dense class="text-h6">
            <q-item-section>
              <q-item-label class="text-h6">
                Channel Configuration
              </q-item-label>
            </q-item-section>

            <q-item-section side v-if="channelDetails?.channelConfig?.state">
              <q-item-label caption> State </q-item-label>
              <q-item-label class="text-body1">
                {{ channelDetails?.channelConfig?.state }}
              </q-item-label>
            </q-item-section>
            <q-item-section side v-if="channelDetails?.channelConfig?.health">
              <q-item-label caption class="text-center"> Health </q-item-label>
              <q-item-label class="text-body1 text-center">
                {{ channelDetails?.channelConfig?.health }}
              </q-item-label>
            </q-item-section>
            <q-item-section
              side
              v-if="channelDetails?.channelConfig?.viewerCount"
            >
              <q-item-label caption> CCV </q-item-label>
              <q-item-label class="text-body1">
                {{ channelDetails?.channelConfig?.viewerCount }}
              </q-item-label>
            </q-item-section>
          </q-item>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-pa-none">
          <div class="flex q-gutter-sm">
            <q-item
              v-for="(item, key) in channelDetails?.channelConfig"
              :key="key"
              class="bg-grey-2"
            >
              <q-item-section>
                <q-item-label caption class="text-primary">
                  {{ key }}
                </q-item-label>
                <q-item-label>
                  {{ item }}
                </q-item-label>
              </q-item-section>
            </q-item>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Session List -->
    <div class="col">
      <q-card flat>
        <q-card-section class="q-pa-sm">
          <q-item class="text-h6">
            <q-item-section>
              <q-item-label class="text-h6"> Sessions </q-item-label>
            </q-item-section>

            <q-item-section side>
              <div class="row q-gutter-xs">
                <!-- search channel input -->
                <div class="col-auto">
                  <q-input
                    dense
                    rounded
                    outlined
                    color="primary"
                    v-model="searchSession"
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

                <div class="col">
                  <q-btn
                    padding="8px"
                    label="Load More Sessions"
                    outline
                    rounded
                    no-caps
                    :loading="loading"
                    @click="getSessions"
                    :disabled="!sessionsNextToken"
                  />
                </div>

                <div class="col-auto self-center">
                  <q-btn
                    color="primary"
                    round
                    dense
                    unelevated
                    icon="refresh"
                    @click="getSessions"
                  />
                </div>
              </div>
            </q-item-section>
          </q-item>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-pa-none">
          <q-table
            class="session-list-table"
            square
            flat
            :rows="filteredSessions"
            :row-key="(row) => row.streamId"
            :columns="columns"
            :loading="loadingSessions"
            hide-pagination
            :rows-per-page-options="[0]"
            no-data-label="No sessions"
          >
            <template v-slot:body="props">
              <q-tr
                :props="props"
                class="cursor-pointer"
                @click="goToSessionDetails(props.row)"
              >
                <q-td key="streamId" :props="props">
                  {{ props.row.streamId }}
                </q-td>
                <q-td key="startTime" :props="props">
                  {{ formatDate(props.row.startTime) }}
                </q-td>
                <q-td key="endTime" :props="props">
                  {{ formatDate(props.row.endTime) || "LIVE" }}
                </q-td>
                <q-td key="hasErrorEvent" :props="props">
                  {{ props.row.hasErrorEvent }}
                </q-td>
              </q-tr>
            </template>
          </q-table>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script>
import { defineComponent, computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useChannelStore } from "src/stores/store-channel";
import { date } from "quasar";

export default defineComponent({
  name: "ChannelDetails",

  props: { channel: { type: Object, default: null } },

  setup(props) {
    const channelStore = useChannelStore();
    const route = useRoute();
    const router = useRouter();
    const awsAccountId = route.params.account_id;
    const awsRegion = route.params.region;
    const channelId = props.channel.channelId;
    const channelArn = props.channel.arn || props.channel.channelArn;

    const channelDetails = computed(
      () => channelStore.channels[awsRegion]?.[channelId]
    );

    const loading = ref(false);
    const loadingSessions = ref(true);
    const searchSession = ref("");

    const columns = [
      {
        name: "streamId",
        required: true,
        label: "Stream ID",
        align: "left",
        field: "streamId",
        sortable: true,
      },
      {
        name: "startTime",
        required: true,
        label: "Start Time",
        align: "left",
        field: "startTime",
        format: (val) => formatDate(val),
        sortable: true,
      },
      {
        name: "endTime",
        required: true,
        label: "End Time",
        align: "left",
        field: "endTime",
        format: (val) => formatDate(val),
        sortable: true,
      },
      {
        name: "hasErrorEvent",
        label: "Has Error Event",
        field: "hasErrorEvent",
        align: "left",
        sortable: true,
      },
    ];

    const formatDate = (dateToConvert) =>
      dateToConvert
        ? date.formatDate(dateToConvert, "DD/MMM/YYYY - hh:mm:ss")
        : "";

    const goToSessionDetails = (session) => {
      router.push({
        name: "Session Details",
        params: {
          account_id: awsAccountId,
          region: awsRegion,
          channel_id: channelId,
          session_id: session.streamId,
        },
      });
    };

    const getSessions = async () => {
      loading.value = true;
      const success = await channelStore.listStreamSessions(
        channelArn,
        channelId,
        awsRegion
      );
      if (success) {
        console.log("Successfully loaded channel sessions.");
      }
      loading.value = false;
      loadingSessions.value = false;
    };

    const sessionsNextToken = computed(
      () => channelStore.sessionsNextToken[awsRegion]?.[channelId]
    );

    const filteredSessions = computed(() => {
      if (!searchSession.value) {
        return channelDetails.value?.streamSessions || [];
      }
      const filterValue = searchSession.value.toLowerCase();
      return (channelDetails.value?.streamSessions || []).filter((session) =>
        session.streamId.toLowerCase().includes(filterValue)
      );
    });

    onMounted(async () => {
      if (!channelDetails.value?.channelConfig?.playbackUrl) {
        loading.value = true;
        const success = await channelStore.getChannel(
          channelArn,
          channelId,
          awsRegion
        );
        if (success) {
          await getSessions();
        }
        loading.value = false;
      } else {
        await getSessions();
      }
    });

    return {
      sessionsNextToken,
      channelDetails,
      columns,
      loading,
      loadingSessions,
      awsRegion,
      formatDate,
      goToSessionDetails,
      getSessions,
      searchSession,
      filteredSessions,
    };
  },
});
</script>

<style lang="sass">
.session-list-table
  /* height or max-height is important */
  height: 100%

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
