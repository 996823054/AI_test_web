<template>
  <ol class="step-timeline">
    <li v-for="(step, index) in steps" :key="index" :data-status="step.status || 'pending'">
      <strong>{{ step.name || `步骤 ${index + 1}` }}</strong>
      <span>{{ step.status || 'pending' }}</span>
    </li>
  </ol>
</template>

<script setup>
defineProps({
  steps: { type: Array, default: () => [] },
})
</script>

<style scoped>
.step-timeline {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}
.step-timeline li {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(20, 28, 36, 0.06);
}
</style>
