<template>
  <div class="empty-state">
    <div>{{ title }}</div>
    <div v-if="description" style="margin-top: 6px;">{{ description }}</div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '暂无数据' },
  description: { type: String, default: '' },
})
</script>
