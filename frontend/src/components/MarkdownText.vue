<!-- src/components/MarkdownText.vue -->
<template>
  <div :class="$attrs.class" v-html="rendered"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

defineOptions({ inheritAttrs: false })

const props = defineProps<{ content: string }>()

const md = new MarkdownIt({ breaks: true })

const rendered = computed(() => md.render(props.content || ''))
</script>
