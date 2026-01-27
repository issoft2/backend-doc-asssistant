<!-- CTASection.vue -->
<template>
  <section class="relative bg-indigo-600 py-24">
    <div class="max-w-4xl mx-auto px-6 text-center">
      <!-- CTA Heading -->
      <h2 class="text-3xl sm:text-4xl font-extrabold text-white">
        Ready to get answers from your documents instantly?
      </h2>

      <!-- CTA Description -->
      <p class="mt-4 text-indigo-100 text-lg sm:text-xl">
        Upload your files, ask questions naturally, and get insights — all private and secure.
      </p>

      <!-- CTA Buttons -->
      <div class="mt-8 flex flex-wrap justify-center gap-4">
        <RouterLink
          to="/login"
          class="px-6 py-3 rounded-lg bg-white text-indigo-600 font-semibold shadow hover:bg-gray-100 transition"
        >
          Try it now
        </RouterLink>
        <a
          href="#how-it-works"
          class="px-6 py-3 rounded-lg border border-white text-white font-semibold hover:bg-white hover:text-indigo-600 transition"
        >
          Learn how it works
        </a>
      </div>
    </div>

    <!-- Abstract Background Shapes -->
    <div class="absolute inset-0 -z-10 overflow-hidden">
      <svg class="absolute top-1/2 left-1/2 w-[600px] h-[600px] transform -translate-x-1/2 -translate-y-1/2 animate-slow-spin" fill="none">
        <circle cx="300" cy="300" r="300" fill="url(#grad2)" fill-opacity="0.1"/>
        <defs>
          <radialGradient id="grad2" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(300 300) rotate(90) scale(300)">
            <stop stop-color="#ffffff"/>
            <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
          </radialGradient>
        </defs>
      </svg>
    </div>
  </section>
</template>

<script setup>
// No JS logic needed here
</script>

<style scoped>
.animate-slow-spin {
  animation: slow-spin 120s linear infinite;
}

@keyframes slow-spin {
  0% { transform: rotate(0deg);}
  100% { transform: rotate(360deg);}
}
</style>
