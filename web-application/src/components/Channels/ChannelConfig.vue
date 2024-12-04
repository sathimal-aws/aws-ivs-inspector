<template>
  <div class="column q-gutter-y-lg body-head-height">
    <div class="col-auto">
      <div class="col">
        <q-item dense class="q-px-sm text-h6">
          <q-item-section>
            <q-item-label class="text-h6"> Channel Configuration </q-item-label>
          </q-item-section>

          <q-item-section avatar>
            <q-btn
              label="Session Details"
              icon-right="keyboard_arrow_right"
              outline
              rounded
              no-caps
              @click="
                goToSessionDetails(channelDetails?.channelConfig?.streamId)
              "
            />
          </q-item-section>
        </q-item>
      </div>
      <q-separator spaced />

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
    </div>
  </div>
</template>

<script>
import { defineComponent, computed, onMounted, ref, capitalize } from "vue";
import { useRoute, useRouter } from "vue-router";
import { date } from "quasar";
import { useChannelStore } from "src/stores/store-channel";
import { useCommonStore } from "src/stores/store-common";

export default defineComponent({
  name: "ChannelDetails",

  props: { channel: { type: Object, default: null } },

  setup(props) {
    const commonStore = useCommonStore();
    const channelStore = useChannelStore();
    const $route = useRoute();
    const $router = useRouter();
    const awsAccountId = $route.params.account_id;
    const awsRegion = $route.params.region;
    const channelId = props.channel.channelId;
    const channelArn = props.channel.arn || props.channel.channelArn;
    const channelDetails = computed(
      () => channelStore.channels[awsRegion]?.[channelId]
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

    const goToSessionDetails = (stream_id) => {
      $router.push({
        name: "Session Details",
        params: {
          account_id: awsAccountId,
          region: awsRegion,
          channel_id: channelId,
          session_id: stream_id,
        },
      });
    };

    onMounted(() => {
      console.log("channelDetails in store", channelStore.channels);
      console.log(channelId, channelDetails.value);
      if (!channelDetails.value?.["playbackUrl"]) {
        loading.value = true;
        channelStore
          .getChannel(channelArn, channelId, awsRegion)
          .then((res) => {
            console.log(res);
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
      searchSession: ref(""),

      dateManipulate,
      goToSessionDetails,
      capitalize,
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
