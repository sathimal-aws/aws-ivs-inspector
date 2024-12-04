<template>
  <div class="col body-spacing">
    <div class="col">
      <div class="row q-col-gutter-md">
        <q-item-label class="col-12 col-sm text-h6">
          Channel: {{ channelState }}
        </q-item-label>

        <q-item-label class="col-12 col-sm-auto text-h6">
          Current CCV: {{ channelDetails?.ccv || 0 }}
        </q-item-label>
      </div>
    </div>

    <q-separator />

    <div class="col">
      <div class="row q-col-gutter-md">
        <div class="col q-pt-lg">
          <list-items
            :list="channelDetails?.channel"
            type="Details"
            :issue="null"
          />
        </div>
        <div class="col-auto">
          <q-table
            class="my-sticky-header-table"
            flat
            :rows="channelDetails?.streamSessions"
            :columns="columns"
            :row-key="channelDetails?.streamSessions?.streamId"
            :loading="loading"
            :pagination="initialPagination"
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
                  {{ dateManipulate(props.row.startTime) }}
                </q-td>
                <q-td key="endTime" :props="props">
                  {{ dateManipulate(props.row.endTime) }}
                </q-td>
                <q-td key="hasErrorEvent" :props="props">
                  {{ props.row.hasErrorEvent }}
                </q-td>
              </q-tr>
            </template>
          </q-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useChannelStore } from "src/stores/store-channel";
import { useCommonStore } from "src/stores/store-common";
import { date } from "quasar";
import ListItems from "src/components/Common/ListItems.vue";

export default defineComponent({
  name: "ChannelDetails",

  setup() {
    const channelStore = useChannelStore();
    const commonStore = useCommonStore();
    const $route = useRoute();
    const $router = useRouter();
    const awsAccountId = $route.params.account_id;
    const awsRegion = $route.params.region;
    const channelId = $route.params.channel_id;
    const channelArn = `arn:aws:ivs:${awsRegion}:${awsAccountId}:channel/${channelId}`;
    const channelDetails = computed(
      () => channelStore.channels[awsRegion][channelId]
    );
    const channelState = ref("inactive");

    const columns = [
      {
        name: "streamId",
        required: true,
        label: "Stream ID",
        align: "left",
        field: (row) => row.streamId,
        format: (val) => `${val}`,
        sortable: true,
      },

      {
        name: "startTime",
        required: true,
        label: "Start Time",
        align: "left",
        field: (row) => row.startTime,
        format: (val) => `${dateManipulate(val)}`,
        sortable: true,
      },

      {
        name: "endTime",
        required: true,
        label: "End Time",
        align: "left",
        field: (row) => row.endTime,
        format: (val) => `${dateManipulate(val)}`,
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

    const loading = ref(false);

    const dateManipulate = (dateToConvert) =>
      date.formatDate(dateToConvert, "DD/MMM/YYYY - hh:mm:ss");

    const goToSessionDetails = (session) => {
      console.log(session);
      $router.push({
        name: "Session Details",
        params: {
          account_id: awsAccountId,
          region: awsRegion,
          channel_id: channelId,
          session_id: session.streamId,
        },
      });
    };

    onMounted(() => {
      console.log(channelDetails.value);
      if (!channelDetails.value?.["playbackUrl"]) {
        loading.value = true;
        channelStore
          .getChannel(channelArn, channelId, awsRegion)
          .then((res) => {
            if (res)
              channelStore
                .listStreamSessions(channelArn, channelId, awsRegion)
                .then((res) => (loading.value = false));
          });
      }
    });

    return {
      channelStore,
      channelState,
      channelDetails,
      columns,
      loading,
      initialPagination: commonStore.initialPagination,

      dateManipulate,
      goToSessionDetails,
    };
  },

  components: { ListItems },
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
