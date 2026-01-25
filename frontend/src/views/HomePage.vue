<template>
  <main class="bg-[var(--bg-primary)] text-[var(--text-primary)] overflow-hidden">

    <!-- HERO -->
    <section class="relative isolate">
      <div class="max-w-7xl mx-auto px-6 py-32 text-center">
        <h1
          v-motion="heroMotion"
          class="text-4xl md:text-6xl font-semibold tracking-tight leading-tight"
        >
          Build. Sign. Share.  
          <span class="block text-[var(--accent)]">Documents without friction</span>
        </h1>

        <p
          v-motion="fadeUp(0.1)"
          class="mt-6 max-w-2xl mx-auto text-lg text-[var(--text-muted)]"
        >
          A modern platform for editing, signing, and managing PDFs — fast, secure,
          and built for teams that value simplicity.
        </p>

        <div
          v-motion="fadeUp(0.2)"
          class="mt-10 flex justify-center gap-4"
        >
          <button class="btn-primary">
            Get started free
          </button>
          <button class="btn-secondary">
            See how it works
          </button>
        </div>
      </div>
    </section>

    <!-- FEATURES -->
    <section class="border-t border-[var(--border-subtle)]">
      <div class="max-w-7xl mx-auto px-6 py-24">
        <div class="grid md:grid-cols-3 gap-12">

          <Feature
            icon="⚡"
            title="Instant editing"
            text="Edit PDFs directly in your browser. No installs. No learning curve."
          />

          <Feature
            icon="✍🏽"
            title="Legally binding signatures"
            text="Sign and request signatures with full audit trails and compliance."
          />

          <Feature
            icon="🔒"
            title="Enterprise-grade security"
            text="Hard tenant isolation, encryption, and role-based access by default."
          />

        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="border-t border-[var(--border-subtle)]">
      <div
        v-motion="fadeUp(0.1)"
        class="max-w-4xl mx-auto px-6 py-28 text-center"
      >
        <h2 class="text-3xl md:text-4xl font-semibold tracking-tight">
          Ready to modernize your document workflow?
        </h2>

        <p class="mt-4 text-[var(--text-muted)]">
          Start free. Upgrade when your team grows.
        </p>

        <div class="mt-8">
          <button class="btn-primary">
            Create your first document
          </button>
        </div>
      </div>
    </section>

  </main>
</template>

<script setup>
import { useReducedMotion } from '@vueuse/motion'

const reducedMotion = useReducedMotion()

const baseFade = {
  initial: { opacity: 0, y: 16 },
  enter: { opacity: 1, y: 0 },
}

const heroMotion = reducedMotion.value
  ? {}
  : {
      ...baseFade,
      transition: { duration: 0.5, ease: 'easeOut' },
    }

const fadeUp = (delay = 0) =>
  reducedMotion.value
    ? {}
    : {
        ...baseFade,
        transition: { duration: 0.4, delay, ease: 'easeOut' },
      }
</script>

<script>
export default {
  components: {
    Feature: {
      props: ['icon', 'title', 'text'],
      template: `
        <div class="text-center space-y-4">
          <div class="text-3xl">{{ icon }}</div>
          <h3 class="text-lg font-semibold">{{ title }}</h3>
          <p class="text-[var(--text-muted)] text-sm">
            {{ text }}
          </p>
        </div>
      `,
    },
  },
}
</script>
