<template>
  <div class="col q-gutter-y-sm">
    <div class="col" v-if="type">
      <div class="row q-col-gutter-md text-h6">
        <q-item-label class="col self-center">
          {{ type }}
        </q-item-label>

        <q-item-label v-if="issue" class="col-auto self-center">
          Issue: None
        </q-item-label>
      </div>
      <q-separator />
    </div>

    <q-list separator class="ivs-bg-grey">
      <q-item
        v-for="(value, key) in list"
        :key="key"
        :clickable="value.name.includes('Starvation')"
        @click="$emit('showEventReason', value.name)"
      >
        <q-item-section side v-if="value.name.includes('Starvation')">
          <q-btn
            icon="o_info"
            round
            padding="none"
            unelevated
            :color="value.name.includes('Start') ? 'red' : 'green'"
          />
        </q-item-section>

        <q-item-section side>
          <q-item-label> {{ value.name }}: </q-item-label>
        </q-item-section>

        <q-item-section class="text-right">
          <q-item-label lines="3">
            {{ date.formatDate(value.time, "YYYY-MMM-DD hh:mm:ss a") }}
          </q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
  </div>
</template>

<script>
import { date } from "quasar";
import { defineComponent, toRefs } from "vue";

export default defineComponent({
  name: "ListItems",

  props: {
    type: { type: String, default: null },
    list: { type: Object, default: null },
    checkList: { type: Object, default: null },
    issue: { type: String, default: null },
  },

  setup(props) {
    return { date };
  },
});
</script>
