<!-- HowItWorks.vue -->
<template>
  <section id="how-it-works" class="relative py-24 bg-gray-50">
    <div class="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
      <!-- Section Header -->
      <div class="text-center max-w-2xl mx-auto">
        <h2 class="text-3xl sm:text-4xl font-extrabold text-gray-900">
          How it works
        </h2>
        <p class="mt-4 text-gray-600 text-lg sm:text-xl">
          Follow these simple steps to start getting answers from your documents instantly.
        </p>
      </div>

      <!-- Steps Grid -->
      <div class="mt-16 grid gap-12 sm:grid-cols-1 md:grid-cols-3">
        <div
          v-for="(step, index) in steps"
          :key="index"
          class="relative p-6 bg-white rounded-2xl shadow hover:shadow-lg transition cursor-pointer"
        >
          <!-- Step number badge -->
          <div class="w-12 h-12 flex items-center justify-center rounded-full bg-indigo-100 text-indigo-600 font-bold text-lg mb-4">
            {{ index + 1 }}
          </div>

          <!-- Step Title -->
          <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ step.title }}</h3>

          <!-- Step Description -->
          <p class="text-gray-600 leading-relaxed">{{ step.description }}</p>
        </div>
      </div>
    </div>

    <!-- Optional abstract background shapes -->
    <div class="absolute inset-0 -z-10 overflow-hidden">
      <svg class="absolute top-0 left-1/2 transform -translate-x-1/2 mt-12" width="600" height="600" fill="none">
        <circle cx="300" cy="300" r="300" fill="url(#grad1)" fill-opacity="0.1" class="animate-slow-spin"/>
        <defs>
          <radialGradient id="grad1" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(300 300) rotate(90) scale(300)">
            <stop stop-color="#6366f1"/>
            <stop offset="1" stop-color="#6366f1" stop-opacity="0"/>
          </radialGradient>
        </defs>
      </svg>
    </div>
  </section>
</template>

<script setup>
const steps = [
  {
    title: "Unified Knowledge Import",
    description: "Unified Knowledge Import Securely centralize your data by uploading files directly or syncing effortlessly with Google Drive, Dropbox, and cloud storage. Whether it's a PDF, Doc, or Sheet, your data remains private, encrypted, and entirely under your control.",
  },

  {
    title: "Conversational Intelligence",
    description: "Ask complex questions in plain English and get precise answers. Interact with your documents like a teammate without the manual search.",
  },
  {
    title: "Instant Visual Analytics",
    description: "Transform raw data into professional charts, summaries, and actionable insights with a simple question.",
  },
];
</script>

<style scoped>
.animate-slow-spin {
  animation: slow-spin 60s linear infinite;
}

@keyframes slow-spin {
  0% { transform: rotate(0deg);}
  100% { transform: rotate(360deg);}
}
</style>
