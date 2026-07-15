<template>
  <section class="log-panel">
    <h3>日志</h3>
    <ul>
      <li v-for="(line, index) in lines" :key="index">{{ line }}</li>
    </ul>
  </section>
</template>

<script setup>
defineProps({
  lines: { type: Array, default: () => [] },
})
</script>

<style scoped>
.log-panel ul {
  margin: 0;
  padding-left: 18px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
}
</style>
