<!-- FeatureSection.vue -->
<template>
  <section id="features" class="relative py-24 bg-white">
    <div class="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
      <!-- Section Header -->
      <div class="text-center max-w-2xl mx-auto">
        <h2 class="text-3xl sm:text-4xl font-extrabold text-gray-900">
          Why teams love our Assistant
        </h2>
        <p class="mt-4 text-gray-600 text-lg sm:text-xl">
          Powerful AI features that help your team find answers, analyze documents, and get insights instantly.
        </p>
      </div>

      <!-- Features Grid -->
      <div class="mt-16 grid gap-10 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="feature in features"
          :key="feature.title"
          class="relative p-6 bg-gray-50 rounded-2xl shadow hover:shadow-lg transition cursor-pointer"
        >
          <!-- Icon -->
          <div class="flex items-center justify-center w-16 h-16 rounded-full bg-indigo-100 text-indigo-600 mb-4">
            <component :is="feature.icon" class="w-8 h-8" />
          </div>

          <!-- Title -->
          <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ feature.title }}</h3>

          <!-- Description -->
          <p class="text-gray-600 leading-relaxed">{{ feature.description }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
// import '@iconify/vue'
import { 
  DocumentTextIcon, 
  UserGroupIcon, 
  ShieldCheckIcon 
} from '@heroicons/vue/24/outline'


const features = [
  {
    title: "Document Intelligence",
    description:
      "Upload PDFs, Docs, and spreadsheets. Our AI reads, understands, and answers questions instantly.",
    icon: DocumentTextIcon ,
  },
  {
    title: "Team Collaboration",
    description:
      "Share knowledge safely across your team with multi-tenant access and permissions.",
    icon: DocumentTextIcon,
  },
  {
    title: "Privacy & Security",
    description:
      "All data stays private. End-to-end encryption and enterprise-grade access control keep your documents safe.",
    icon: DocumentTextIcon,
  },
  // add more features here if needed
];
</script>

<style scoped>
/* Optional: subtle hover scale effect */
div[role="feature"] {
  transition: transform 0.3s ease;
}
div[role="feature"]:hover {
  transform: translateY(-4px);
}
</style>

