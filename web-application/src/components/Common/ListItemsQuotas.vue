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
      <q-item v-for="(quota, key) in list" :key="key">
        <q-item-section>
          <q-item-label> {{ quota.key }}: </q-item-label>
        </q-item-section>

        <q-item-section side class="text-right">
          <q-item-label lines="3">
            {{ quota.provisioned }}
          </q-item-label>
        </q-item-section>

        <q-item-section side class="text-right"> / </q-item-section>

        <q-item-section side class="text-right">
          <q-item-label lines="3">
            {{ quota.usage }}
          </q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
  </div>
</template>

<script>
import { defineComponent } from "vue";

export default defineComponent({
  name: "ListItems",

  props: {
    type: { type: String, default: null },
    list: { type: Object, default: null },
    checkList: { type: Object, default: null },
    issue: { type: String, default: null },
  },
});
</script>
