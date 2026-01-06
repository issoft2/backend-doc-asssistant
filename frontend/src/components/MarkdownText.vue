<template>
  <div
    :class="wrapperClass"
    v-html="compiled"
  ></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps<{
  content: string
  class?: string
}>()

const compiled = computed(() => marked.parse(props.content || ''))
const wrapperClass = computed(() => props.class)
</script>
