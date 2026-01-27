<template>
    < <div class="min-h-screen bg-slate-50 text-slate-900 flex flex-col">

    <!-- HEADER / NAV -->
    <header class="sticky top-0 z-50 bg-white/80 backdrop-blur border-b border-slate-200">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">

        <!-- Brand -->
        <div class="flex items-center gap-3">
          <div class="h-9 w-9 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-semibold text-sm">
            CG
          </div>
          <span class="font-semibold text-sm">
            Knowledge Assistant
          </span>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-4">
          <RouterLink
            to="/login"
            class="text-sm font-medium text-slate-600 hover:text-slate-900 transition"
          >
            Login
          </RouterLink>

          <a 
            href="#hero-contact-form"
            class="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 transition"
          >
            Get Started
          </a>
        </div>

      </div>
    </header>

         <slot /> <!-- This is where the page content (section) will appear -->
         <!-- You can add footer here if all pages share it  -->

    </div>
</template>

<script setup>
// No additional script logic needed for layout
</script>