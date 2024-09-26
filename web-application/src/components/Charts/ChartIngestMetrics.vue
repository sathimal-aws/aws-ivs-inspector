<template>
  <v-chart
    v-if="chartOptions.series.data.length"
    class="ivs-bg-grey q-pa-md"
    :option="chartOptions"
    autoresize
  />
</template>

<script>
import { defineComponent, onMounted, ref, provide, watch, toRefs } from "vue";
import { date } from "quasar";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { LineChart } from "echarts/charts";

import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  ToolboxComponent,
  DataZoomComponent,
} from "echarts/components";

import VChart, { THEME_KEY } from "vue-echarts";

use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  ToolboxComponent,
  DataZoomComponent,
]);

const metricConfigs = {
  "Ingest Video Bitrate (kbps)": {
    unit: "kbps",
    calculate: (value) => Math.trunc(value / 1024),
  },
  "Ingest Audio Bitrate (kbps)": {
    unit: "kbps",
    calculate: (value) => Math.trunc(value / 1024),
  },
  "Ingest Framerate (fps)": {
    unit: "fps",
    calculate: (value) => Math.trunc(value),
  },
  "Keyframe Interval (idr)": {
    unit: "seconds",
    calculate: (value) => Math.trunc(value),
  },
  "Concurrent Views (count)": {
    unit: "count",
    calculate: (value) => Math.trunc(value),
  },
};

export default defineComponent({
  name: "IngestMetricsChart",

  props: {
    label: { type: String, default: null },
    metrics: { type: Object, default: null },
  },

  components: { VChart },

  setup(props) {
    provide(THEME_KEY);

    const { metrics } = toRefs(props);

    const chartOptions = ref({
      tooltip: {
        trigger: "axis",
      },
      grid: {
        left: "2%",
        right: "2%",
        top: "10%",
        bottom: "15%",
        containLabel: true,
      },
      dataZoom: [
        {
          show: true,
          realtime: true,
          start: 0,
          end: 100,
          xAxisIndex: [0],
        },
        {
          type: "inside",
          realtime: true,
          start: 30,
          end: 70,
          xAxisIndex: [0],
        },
      ],
      xAxis: {
        type: "category",
        boundaryGap: true,
        data: [],
      },
      yAxis: {
        type: "value",
        min: null,
        max: null,
        boundaryGap: [0, "100%"],
        name: metricConfigs[props.label]?.unit || "",
      },
      series: {
        name: props.label,
        type: "line",
        stack: "Total",
        data: [],
      },
    });

    const updateChartOptions = () => {
      const metricConfig = metricConfigs[props.label];
      chartOptions.value.xAxis.data = Object.keys(props.metrics).map((key) =>
        date.formatDate(parseInt(key) * 1000, "hh:mm:ss")
      );
      chartOptions.value.series.data = Object.values(props.metrics).map(
        metricConfig?.calculate || ((value) => value)
      );
      chartOptions.value.yAxis.min = Math.min(
        ...chartOptions.value.series.data
      );
      chartOptions.value.yAxis.max = Math.max(
        ...chartOptions.value.series.data
      );
    };

    watch(metrics, updateChartOptions);
    onMounted(updateChartOptions);

    return { chartOptions };
  },
});
</script>

<style scoped>
.echarts {
  width: 100%;
  height: 360px;
  margin: auto auto;
}
.echart {
  width: 100%;
  height: 360px;
  /* border: 1px solid #cfcfcf; */
}
h1,
h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 10px;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
