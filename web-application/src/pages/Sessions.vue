<template>
  <div class="col body-spacing q-gutter-y-lg">
    <div class="col">
      <div class="row q-col-gutter-md text-h6">
        <q-item-section class="col-12 col-sm">
          <q-item-label> Session: {{ sessionState }} </q-item-label>
        </q-item-section>

        <q-item-section class="col-12 col-sm-auto">
          <q-item-label> Session CCV: {{ sessionCcv }} </q-item-label>
        </q-item-section>
      </div>
      <q-separator />
    </div>

    <div class="col" v-if="sessionMetrics?.length">
      <chart-bitrate :metrics="sessionMetrics" />
    </div>
    <div class="col">
      <div class="row q-col-gutter-md col-12 col-md-4 col-sm-6">
        <div class="col-lg-3 col-md-4 col-sm-6 col-xs-12">
          <list-items type="Channel" :list="sessionDetails?.channel" />
        </div>
        <div class="col-lg-3 col-md-4 col-sm-6 col-xs-12">
          <list-items
            type="Video"
            :list="sessionDetails?.ingestConfiguration?.video"
          />
        </div>
        <div class="col-lg-3 col-md-4 col-sm-6 col-xs-12">
          <list-items
            type="Audio"
            :list="sessionDetails?.ingestConfiguration?.audio"
          />
          <list-items
            v-if="sessionDetails?.recordingConfiguration"
            type="Recording"
            :list="sessionDetails?.recordingConfiguration"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useSessionStore } from "src/stores/store-session";
import ChartBitrate from "src/components/Charts/ChartIngestMetrics.vue";
import ListItems from "src/components/Common/ListItems.vue";

export default defineComponent({
  name: "sessionDetails",

  setup() {
    const sessionStore = useSessionStore();
    const $route = useRoute();
    const awsRegion = $route.params.region;
    const awsAccountId = $route.params.account_id;
    const channelId = $route.params.channel_id;
    const sessionId = $route.params.session_id;
    const channelArn = `arn:aws:ivs:${awsRegion}:${awsAccountId}:channel/${channelId}`;

    const sessionDetails = computed(() => sessionStore.sessions[sessionId]);
    const sessionMetrics = computed(
      () => sessionStore.sessionMetrics[sessionId]
    );
    const limits = computed(() =>
      sessionStore.quotas?.Quotas?.map((quota) => {
        return {
          key: quota.QuotaName,
          provisioned: quota.Value,
          usage: quota.Value,
        };
      })
    );
    const sessionState = computed(() =>
      sessionDetails.value?.stream
        ? `${sessionDetails.value?.stream?.state}:${sessionDetails.value?.stream?.health}`
        : "Inactive"
    );

    const sessionCcv = computed(
      () => sessionDetails.value?.stream?.viewerCount || "0"
    );

    onMounted(() => {
      if (!sessionDetails.value) {
        console.log("sessionId:", sessionId);
        if (!sessionDetails.value) {
          sessionStore.getSession(sessionId, channelArn);
          sessionStore.getStream(sessionId, channelArn);
        }
        if (!sessionMetrics.value) {
          sessionStore.getIngestMetrics(sessionId);
        }
        if (!limits.value) {
          sessionStore.getQuotaProvisioned("ivs");
        }
      }
    });
    return {
      sessionStore,
      sessionState,
      sessionCcv,
      sessionDetails,
      sessionMetrics,
      limits,
    };
  },

  components: {
    ChartBitrate,
    ListItems,
  },
});
</script>
