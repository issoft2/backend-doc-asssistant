<template>
    <div v-html="rendered"></div>
</template>

<script setup>
    import { computed } from 'vue';
    import markdownIt from 'markdown-it';

    const props = defineProps<{ content: string }>();
    const md = new markdownIt({ breaks: true })

    const rendered = computed(() => md.render(props.content || ''))
</script>