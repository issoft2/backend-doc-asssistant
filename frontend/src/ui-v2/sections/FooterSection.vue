<!-- FooterSection.vue -->
<template>
  <footer class="bg-slate-50 border-t border-slate-200 py-12 text-center relative overflow-hidden">
    <!-- Optional subtle abstract shape -->
    <div class="absolute inset-0 -z-10">
      <svg class="w-full h-full" viewBox="0 0 800 200" fill="none">
        <ellipse cx="400" cy="100" rx="400" ry="100" fill="url(#footerGrad)" fill-opacity="0.05"/>
        <defs>
          <linearGradient id="footerGrad" x1="0" y1="0" x2="800" y2="0" gradientUnits="userSpaceOnUse">
            <stop stop-color="#4f46e5"/>
            <stop offset="1" stop-color="#4f46e5" stop-opacity="0"/>
          </linearGradient>
        </defs>
      </svg>
    </div>

    <div class="max-w-4xl mx-auto space-y-4">
      <p class="text-slate-600 text-sm">
        © {{ new Date().getFullYear() }} Lexiscope knowledge Assistant. All rights reserved.
      </p>

      <!-- Optional Links -->
      <div class="flex justify-center gap-6 text-slate-500 text-sm">
        <a href="/privacy" class="hover:text-indigo-600 transition">Privacy Policy</a>
        <a href="/terms" class="hover:text-indigo-600 transition">Terms of Service</a>
        <a href="/contact" class="hover:text-indigo-600 transition">Contact</a>
      </div>

      <!-- Optional Social Icons -->
      <div class="flex justify-center gap-4 mt-2 text-slate-500">
        <a href="#" aria-label="Twitter" class="hover:text-indigo-600 transition">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 19c7 0 11-6 11-11v-1a8 8 0 0 0 2-2c-1 0-2 0-3 .5A4 4 0 0 0 19 5a8 8 0 0 1-2 1c-1-1-3-1-4 0-1 1-2 3-1 4-3 0-6-1-8-3a4 4 0 0 0 1 5 4 4 0 0 1-2-.5v.5c0 2 1 4 3 5s4 1 6 1"/></svg>
        </a>
        <a href="#" aria-label="LinkedIn" class="hover:text-indigo-600 transition">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M4 3a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm0 6h4v12H4zm6 0h4v2h.1a4 4 0 0 1 4-2c4 0 5 2 5 5v7h-4v-6c0-1-1-2-2-2s-2 1-2 2v6h-4V9z"/></svg>
        </a>
        <a href="#" aria-label="GitHub" class="hover:text-indigo-600 transition">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0a12 12 0 0 0-4 23.4c.6.1.8-.3.8-.6v-2.1c-3 .6-3.7-1.3-3.7-1.3-.5-1.2-1.2-1.5-1.2-1.5-1-.7.1-.7.1-.7 1.1.1 1.7 1.1 1.7 1.1 1 .1 1.6-.8 1.6-.8.9-1.5 2.3-1.1 2.9-.9.1-.7.4-1.1.7-1.3-2.4-.3-5-1.2-5-5.3 0-1.2.4-2.1 1-2.9-.1-.3-.5-1.3.1-2.6 0 0 .8-.3 2.8 1a9.8 9.8 0 0 1 5.2 0c2-1.3 2.8-1 2.8-1 .6 1.3.2 2.3.1 2.6.6.8 1 1.7 1 2.9 0 4.1-2.6 5-5 5.3.4.3.8 1 .8 2.1v3.1c0 .3.2.7.8.6A12 12 0 0 0 12 0z"/></svg>
        </a>
      </div>
    </div>
  </footer>
</template>
