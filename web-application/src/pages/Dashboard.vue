<template>
  <div class="col q-gutter-sm body-spacing">
    <div class="col">
      <div class="row q-gutter-sm col-12 col-md">
        <div
          v-for="(metric, index) in metrics"
          :key="index"
          class="column col box-decorator"
        >
          <div class="col-auto q-pa-md text-h6">
            <q-item-label class="text-body1">
              {{ metric.Label }}
            </q-item-label>
            <q-item-label caption class="text-primary">
              {{ metric.Datapoints[0]?.Unit }} - 24hrs
            </q-item-label>
          </div>

          <div class="col q-py-lg text-center">
            <q-item-label class="value-text">
              {{
                metric.Datapoints.reduce(
                  (accumulator, current) =>
                    accumulator + current.Sum || current.Maximum,
                  0
                )
              }}
            </q-item-label>
          </div>
        </div>
      </div>
    </div>

    <div class="col" v-if="metrics">
      <div class="row q-gutter-sm col-12 col-md">
        <q-list class="col box-decorator">
          <q-item dense class="q-pa-md text-h6">
            <q-item-section>
              <q-item-label class="text-body1">
                Concurrent Streams
              </q-item-label>
            </q-item-section>

            <q-item-section side>
              <q-item-label class="text-body1 text-primary">
                24hrs
              </q-item-label>
            </q-item-section>
          </q-item>
        </q-list>

        <q-list class="col box-decorator">
          <q-item dense class="q-pa-md text-h6">
            <q-item-section>
              <q-item-label class="text-body1"> Concurrent Views </q-item-label>
            </q-item-section>

            <q-item-section side>
              <q-item-label class="text-body1 text-primary">
                24hrs
              </q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </div>
    </div>

    <div class="col">
      <div class="row q-gutter-sm col-12 col-md">
        <div
          v-if="quotasLowLatency?.length"
          class="col q-gutter-y-sm box-decorator"
        >
          <div class="col-auto q-pa-md text-h6">
            <q-item-label class="text-body1">
              Quotas: Low Latency
            </q-item-label>
          </div>

          <q-table
            class="bg-transparent"
            flat
            :rows="quotasLowLatency"
            :columns="columns"
            row-key="QuotaName"
            hide-header
            hide-bottom
          />
        </div>

        <div
          v-if="quotasStages?.length"
          class="col q-gutter-y-sm box-decorator"
        >
          <div class="col-auto q-pa-md text-h6">
            <q-item-label class="text-body1"> Quotas: Stages </q-item-label>
          </div>

          <q-table
            class="bg-transparent"
            flat
            :rows="quotasStages"
            :columns="columns"
            row-key="QuotaName"
            hide-header
            hide-bottom
            :pagination="initialPagination"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, defineComponent, onMounted } from "vue";
import { useAccountStore } from "src/stores/store-account";
import { useCommonStore } from "src/stores/store-common";
import { useRoute } from "vue-router";

export default defineComponent({
  name: "DashBoard",

  setup() {
    const $route = useRoute();
    const commonStore = useCommonStore();
    const accountStore = useAccountStore();
    const ivsRegion = computed(() => $route.params.region);

    const metrics = computed(() => accountStore.metrics[ivsRegion.value]);

    const quotasProvisioned = computed(
      () => accountStore.accountQuotas[ivsRegion.value]
    );

    const quotasLowLatencyKeys = [
      "Channels",
      "Concurrent streams",
      "Concurrent views",
      "Playback restriction policies",
      "Recording configurations",
    ];

    const quotasStagesKeys = [
      "Stages",
      "Stream Key",
      "Total number of Destinations per Composition",
      "Compositions",
      "Stage participants (subscribers)",
      "Stage participants (publishers)",
      "Max Composition duration",
      "Storage configurations",
      "Encoder configurations",
    ];

    const quotasLowLatency = computed(() =>
      quotasProvisioned?.value?.filter((quota) =>
        quotasLowLatencyKeys.includes(quota.QuotaName)
      )
    );

    const quotasStages = computed(() =>
      quotasProvisioned?.value?.filter((quota) =>
        quotasStagesKeys.includes(quota.QuotaName)
      )
    );

    const columns = [
      {
        name: "QuotaName",
        required: true,
        label: "Quota Name",
        align: "left",
        field: (row) => row.QuotaName,
        format: (val) => `${val}`,
        sortable: true,
      },
      {
        name: "Value",
        required: true,
        label: "Provisioned",
        align: "right",
        field: (row) => row.Value,
        format: (val) => `${val}`,
        sortable: true,
      },
    ];

    onMounted(() => {
      if (!quotasProvisioned.value?.length) {
        accountStore.getQuotaProvisioned("ivs", ivsRegion.value);
      }
      if (!metrics.value?.length) {
        accountStore.getMetrics(ivsRegion.value);
      }
    });

    return {
      metrics,
      quotasProvisioned,
      quotasLowLatency,
      quotasStages,
      columns,
      initialPagination: commonStore.initialPagination,
    };
  },
});
</script>

<style lang="sass">
.box-decorator
  background-color: $grey-2
  border: 1px solid #ff9900

.value-text
  font-size: 4vw
  font-weight: 400
  color: $grey-8
</style>
