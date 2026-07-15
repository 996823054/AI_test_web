<template>
  <section class="evidence-viewer">
    <h3>证据</h3>
    <pre>{{ pretty }}</pre>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  evidence: { type: [Object, Array, String], required: true },
})

const pretty = computed(() =>
  typeof props.evidence === 'string' ? props.evidence : JSON.stringify(props.evidence, null, 2),
)
</script>

<style scoped>
.evidence-viewer {
  border-top: 1px solid rgba(20, 28, 36, 0.08);
  padding-top: 12px;
}
pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
}
</style>
