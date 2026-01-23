<template>
  <div :class="['prose prose-slate max-w-none', $attrs.class]" v-html="rendered"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

defineOptions({ inheritAttrs: false })

const props = defineProps<{ content: string }>()

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: false,
})

const rendered = computed(() => md.render(props.content || ''))
</script>
