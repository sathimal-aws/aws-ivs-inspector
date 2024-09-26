<template>
  <div class="col">
    <div class="col">
      <q-scroll-area
        style="height: calc(100vh - 75px)"
        :thumb-style="thumbStyle"
      >
        <div class="col">
          <q-item dense class="q-pa-md text-h6">
            <q-item-section class="col-12 col-sm">
              <q-item-label> Session: {{ sessionState }} </q-item-label>
            </q-item-section>

            <q-item-section class="col-12 col-sm-auto">
              <q-item-label> Session CCV: {{ sessionCcv }} </q-item-label>
            </q-item-section>
          </q-item>
          <q-separator />
        </div>

        <div class="col">
          <q-card
            class="relative-position full-width"
            style="height: 420px"
            flat
          >
            <q-card-section v-if="metricsLoaded" class="q-pa-none">
              <transition
                appear
                enter-active-class="animated jumpUp"
                leave-active-class="animated fadeOut"
              >
                <div v-show="metricsLoaded">
                  <div class="col" v-if="sessionMetrics">
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
                </div>
              </transition>
            </q-card-section>

            <q-inner-loading
              v-else
              label="Loading Metrics..."
              label-class="text-teal"
              label-style="font-size: 1.1em"
            />
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

            <!-- <div class="col-lg-3 col-md-4 col-sm-6 col-xs-12">
                <list-items-quotas
                  type="Limits (provision/usage)"
                  :list="limits"
                />
              </div> -->
          </div>
        </div>
      </q-scroll-area>
    </div>

    <div class="col">
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
              "Stream starvation" is a delay or halt in content packet delivery
              when you are sending content to IVS; that is, when content is
              being ingested by IVS. If IVS does not get the expected amount of
              bits on ingest that the encoding device advertised it would send
              over a certain timeframe, this is considered a starvation event.
              Often, starvation events are caused by the broadcaster’s encoder,
              local network conditions, and/or in transit over the public
              internet, between the encoding device and IVS.

              <br />
              <br />

              From a viewer's perspective, starvation events may appear as video
              that lags, buffers, or freezes. Stream-starvations events can be
              brief (less than 5 seconds) or long (several minutes), depending
              on the nature of the starvation event.

              <br />
              <br />

              To allow monitoring for starvation events, IVS sends starvation
              events as Amazon EventBridge events; see Examples: Stream Health
              Change in Using Amazon EventBridge with Amazon IVS. These are sent
              when a stream enters or exits a state of starvation. Depending on
              the use case, you can take an appropriate action, like notifying
              the broadcaster and viewers of intermittent stream conditions.

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

export default defineComponent({
  name: "SessionDetails",

  setup() {
    const sessionStore = useSessionStore();
    const commonStore = useCommonStore();
    const $route = useRoute();
    const awsRegion = $route.params.region;
    const awsAccountId = $route.params.account_id;
    const channelId = $route.params.channel_id;
    const sessionId = $route.params.session_id;
    const channelArn = `arn:aws:ivs:${awsRegion}:${awsAccountId}:channel/${channelId}`;

    const sessionDetails = computed(
      () => sessionStore.sessions[awsRegion]?.[sessionId]
    );

    const sessionMetrics = computed(
      () => sessionStore.sessionMetrics[awsRegion]?.[sessionId]
    );

    const metricTypes = [
      { label: "Ingest Video Bitrate (kbps)", type: "IngestVideoBitrate" },
      { label: "Ingest Audio Bitrate (kbps)", type: "IngestAudioBitrate" },
      { label: "Ingest Framerate (fps)", type: "IngestFramerate" },
      { label: "Keyframe Interval (idr)", type: "KeyframeInterval" },
      { label: "Concurrent Views (count)", type: "ConcurrentViews" },
    ];

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

    const sessionEvents = computed(() =>
      sessionDetails.value?.events
        ? Object.values(sessionDetails.value?.events).sort(
            (x, y) => new Date(x.time).getTime() - new Date(y.time).getTime()
          )
        : null
    );

    const showEventReason = (reason) => {
      // console.log("reason:", reason);
      infoType.value = reason;
      showInformation.value = true;
    };

    const infoType = ref(false);

    const showInformation = ref(false);

    const metricsLoaded = ref(false);

    watch(sessionDetails, (currentValue, oldValue) => {
      console.log("currentValue:", currentValue);
      // console.log("oldValue:", oldValue);
      console.log("endTime:", currentValue.endTime);

      if (currentValue.startTime && !currentValue.endTime) {
        console.log("session is live");
        sessionStore.getStream(sessionId, channelArn, awsRegion);
      }
    });

    onMounted(() => {
      if (!sessionDetails.value) {
        // console.log("sessionId:", sessionId);
        sessionStore
          .getSessionEvents(sessionId, channelArn, awsRegion)
          .then((res) => {
            // console.log(res);
          });
        if (!sessionDetails.value) {
          sessionStore
            .getSession(sessionId, channelArn, awsRegion)
            .then((res) => {
              // console.log("getSessionRes:", res);
            });
        }
        if (!sessionMetrics.value) {
          sessionStore
            .getIngestMetrics(sessionId, channelId, awsRegion)
            .then((res) => {
              // console.log("getIngestMetricsResponse", res);
              if (res) metricsLoaded.value = true;
            });
        }
        // if (!limits.value) {
        //   sessionStore.getQuotaProvisioned("ivs", awsRegion);
        // }
      } else metricsLoaded.value = true;
    });

    return {
      metricTab: ref("IngestVideoBitrate"),
      metricTypes,
      sessionStore,
      sessionState,
      sessionCcv,
      sessionDetails,
      sessionMetrics,
      sessionEvents,
      limits,
      thumbStyle: commonStore.thumbStyle,
      showInformation,
      infoType,
      metricsLoaded,
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
