<template>
  <div class="col">
    <q-scroll-area style="height: calc(100vh - 75px)" :thumb-style="thumbStyle">
      <div class="col q-pa-md">
        <q-item dense class="text-h6">
          <q-item-section>
            <q-item-label> Session: {{ sessionState }} </q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-item-label> Session CCV: {{ sessionCcv }} </q-item-label>
          </q-item-section>

          <q-item-section side>
            <q-btn
              color="primary"
              round
              dense
              unelevated
              icon="refresh"
              @click="handleMetricLoad"
            />
          </q-item-section>
        </q-item>

        <q-separator />
      </div>

      <div class="col">
        <q-card class="full-width" style="height: 420px" square flat>
          <div v-if="sessionMetrics">
            <q-tabs
              v-model="metricTab"
              no-caps
              class="text-grey"
              active-color="primary"
              indicator-color="primary"
              align="justify"
            >
              <q-tab
                v-for="(metric, index) in metricTypes"
                :key="index"
                :name="metric.type"
                :label="metric.label"
              />
            </q-tabs>

            <q-separator />

            <q-tab-panels v-model="metricTab" animated>
              <q-tab-panel
                class="q-pa-none"
                :name="metric.type"
                v-for="(metric, index) in metricTypes"
                :key="index"
              >
                <chart-ingest-metrics
                  :metrics="sessionMetrics[metric.type]"
                  :label="metric.label"
                />
              </q-tab-panel>
            </q-tab-panels>
          </div>
          <div
            v-else
            class="column col items-center justify-center full-height"
          >
            <div class="col-auto">
              <q-spinner color="primary" size="3em" />
            </div>

            <q-item-label header> Loading metrics... </q-item-label>

            <div class="col-auto">
              <q-btn
                color="primary"
                round
                dense
                unelevated
                icon="refresh"
                @click="handleMetricLoad"
              />
            </div>
          </div>
        </q-card>
      </div>

      <div class="col q-px-md">
        <div class="row q-col-gutter-md col-12 col-md-4 col-sm-6">
          <div class="col-lg-4 col-md-6 col-sm-12">
            <list-items type="Channel" :list="sessionDetails?.channel" />
            <list-items
              v-if="sessionDetails?.recordingConfiguration"
              type="Recording"
              :list="sessionDetails?.recordingConfiguration"
            />
          </div>
          <div class="col-lg-4 col-md-6 col-sm-12">
            <list-items
              type="Video"
              :list="sessionDetails?.ingestConfiguration?.video"
            />
            <list-items
              type="Audio"
              :list="sessionDetails?.ingestConfiguration?.audio"
            />
          </div>

          <div class="col-lg-4 col-md-6 col-sm-12">
            <list-items-event
              type="Events"
              :list="sessionEvents"
              @showEventReason="showEventReason"
            />
          </div>
        </div>
      </div>
    </q-scroll-area>

    <q-dialog v-model="showInformation" maximized position="right">
      <div class="bg-grey-2 col-3" style="min-width: 500px">
        <q-item class="text-h6" style="height: 56px">
          <q-item-section>
            <q-item-label> What {{ infoType }} means </q-item-label>
          </q-item-section>
          <q-item-section avatar>
            <q-btn
              icon="close"
              round
              outline
              dense
              @click="showInformation = false"
            />
          </q-item-section>
        </q-item>

        <q-separator />

        <q-scroll-area style="height: 100vh" :thumb-style="thumbStyle">
          <div class="col q-pa-md">
            <p v-if="infoType === 'Stream starvation'">
              "Stream starvation" is a delay or halt in content packet delivery
              when you are sending content to IVS; that is, when content is
              being ingested by IVS. If IVS does not get the expected amount of
              bits on ingest that the encoding device advertised it would send
              over a certain timeframe, this is considered a starvation event.
              Often, starvation events are caused by the broadcaster’s encoder,
              local network conditions, and/or in transit over the public
              internet, between the encoding device and IVS.
            </p>
            <p v-if="infoType === 'Stream starvation'">
              From a viewer's perspective, starvation events may appear as video
              that lags, buffers, or freezes. Stream-starvations events can be
              brief (less than 5 seconds) or long (several minutes), depending
              on the nature of the starvation event.
            </p>
            <p v-if="infoType === 'Stream starvation'">
              To allow monitoring for starvation events, IVS sends starvation
              events as Amazon EventBridge events; see Examples: Stream Health
              Change in Using Amazon EventBridge with Amazon IVS. These are sent
              when a stream enters or exits a state of starvation. Depending on
              the use case, you can take an appropriate action, like notifying
              the broadcaster and viewers of intermittent stream conditions.
            </p>
            <br />
            <br />

            <a
              href="https://docs.aws.amazon.com/ivs/latest/LowLatencyUserGuide/troubleshooting-faqs.html#troubleshooting-broadcast-encode"
              target="_blank"
            >
              Refer AWS IVS public document for further details
            </a>
          </div>
        </q-scroll-area>
      </div>
    </q-dialog>
  </div>
</template>

<script>
import { defineComponent, computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useSessionStore } from "src/stores/store-session";
import { useCommonStore } from "src/stores/store-common";
import ChartIngestMetrics from "src/components/Charts/ChartIngestMetrics.vue";
import ListItems from "src/components/Common/ListItems.vue";
import ListItemsEvent from "src/components/Common/ListItemsEvent.vue";
import { useQuasar } from "quasar";

export default defineComponent({
  name: "SessionDetails",

  setup() {
    const sessionStore = useSessionStore();
    const commonStore = useCommonStore();
    const $route = useRoute();
    const $q = useQuasar();

    // Extract route parameters
    const awsRegion = $route.params.region;
    const awsAccountId = $route.params.account_id;
    const channelId = $route.params.channel_id;
    const sessionId = $route.params.session_id;

    // Computed properties for session details, metrics, state, etc.
    const channelArn = computed(
      () => `arn:aws:ivs:${awsRegion}:${awsAccountId}:channel/${channelId}`
    );
    const sessionDetails = computed(
      () => sessionStore.sessions[awsRegion]?.[sessionId]
    );
    const sessionMetrics = computed(
      () => sessionStore.sessionMetrics[awsRegion]?.[sessionId]
    );
    const sessionState = computed(() => {
      const stream = sessionDetails.value?.stream;
      return stream ? `${stream.state}:${stream.health}` : "Inactive";
    });
    const sessionCcv = computed(
      () => sessionDetails.value?.stream?.viewerCount || "0"
    );
    const sessionEvents = computed(() => {
      const events = sessionDetails.value?.events;
      return events
        ? Object.values(events).sort(
            (a, b) => new Date(a.time) - new Date(b.time)
          )
        : null;
    });

    // Metric types for the chart
    const metricTypes = [
      { label: "Ingest Video Bitrate (kbps)", type: "IngestVideoBitrate" },
      { label: "Ingest Audio Bitrate (kbps)", type: "IngestAudioBitrate" },
      { label: "Ingest Framerate (fps)", type: "IngestFramerate" },
      { label: "Keyframe Interval (idr)", type: "KeyframeInterval" },
      { label: "Concurrent Views (count)", type: "ConcurrentViews" },
    ];

    // Refs for dialog and loading state
    const showInformation = ref(false);
    const infoType = ref(null);
    const metricsLoaded = ref(sessionMetrics.value ? true : false);
    const eventNames = computed(() =>
      Object.values(sessionDetails.value.events).map((event) => event.name)
    );

    // Watch for changes in sessionDetails events
    watch(sessionDetails, (current) => {
      if (current?.events && eventNames.value.includes("Stream End")) {
        $q.notify({
          position: "top",
          type: "negative",
          message: "Live stream ended",
          icon: "warning",
          timeout: 0,
          actions: [{ icon: "close", color: "white" }],
        });
      }
    });

    // Fetch data on component mount
    onMounted(async () => {
      if (!sessionDetails.value) {
        await Promise.all([
          sessionStore.getSessionEvents(sessionId, channelArn.value, awsRegion),
          sessionStore.getSession(sessionId, channelArn.value, awsRegion),
          sessionStore.getStream(sessionId, channelArn.value, awsRegion),
        ]);
        if (!sessionMetrics.value) {
          handleMetricLoad();
        }
      } else {
        metricsLoaded.value = true;
      }
    });

    const handleMetricLoad = () => {
      sessionStore
        .getIngestMetrics(sessionId, channelId, awsRegion)
        .then((res) => {
          if (res) metricsLoaded.value = true;
        });
      if (!eventNames.value.includes("Stream End")) {
        sessionStore.getStream(sessionId, channelArn.value, awsRegion);
      }
    };

    // Function to show event reason dialog
    const showEventReason = (reason) => {
      infoType.value = reason;
      showInformation.value = true;
    };

    return {
      metricTab: ref("IngestVideoBitrate"),
      metricTypes,
      sessionStore,
      sessionState,
      sessionCcv,
      sessionDetails,
      sessionMetrics,
      sessionEvents,
      thumbStyle: commonStore.thumbStyle,
      showInformation,
      infoType,
      metricsLoaded,
      handleMetricLoad,
      showEventReason,
    };
  },

  components: {
    ChartIngestMetrics,
    ListItems,
    ListItemsEvent,
  },
});
</script>
