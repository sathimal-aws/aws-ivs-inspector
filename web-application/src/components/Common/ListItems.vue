<template>
  <div class="col q-gutter-y-sm">
    <div class="col" v-if="type">
      <div class="row q-col-gutter-md text-h6">
        <q-item-label class="col self-center">
          {{ type }}
        </q-item-label>

        <q-item-label v-if="issue" class="col-auto self-center">
          Issue: {{ issue || "None" }}
        </q-item-label>

        <div class="col-auto" v-if="!Object.keys(list).length">
          <q-spinner color="primary" size="1.5em" />
        </div>
      </div>
      <q-separator />
    </div>
    <q-list separator class="ivs-bg-grey" v-if="Object.keys(list).length > 0">
      <q-item v-for="(value, key) in list" :key="key">
        <q-item-section>
          <q-item-label>{{ key }}:</q-item-label>
        </q-item-section>

        <q-item-section side class="text-right">
          <q-item-label lines="3">{{ value }}</q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
    <q-item v-else class="ivs-bg-grey">
      <q-item-section>
        <q-item-label>No data available</q-item-label>
      </q-item-section>
    </q-item>
  </div>
</template>

<script>
import { defineComponent } from "vue";

export default defineComponent({
  name: "ListItems",

  props: {
    type: { type: String, default: null },
    list: { type: Object, default: () => ({}) }, // Provide a default empty object
    issue: { type: String, default: null },
    checkList: { type: Object, default: null },
  },
});
</script>
