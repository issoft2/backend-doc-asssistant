<template>
  <main class="bg-slate-50 text-slate-900 min-h-screen flex flex-col">

    <!-- NAV -->
    <header class="bg-white/80 backdrop-blur border-b border-slate-200">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="h-10 w-10 rounded-lg bg-indigo-500/20 flex items-center justify-center text-xs font-semibold text-indigo-600">
            CG
          </div>
          <div class="flex flex-col">
            <span class="font-semibold text-sm">Company knowledge Assistant</span>
            <span class="text-xs text-slate-500">For your Private data</span>
          </div>
        </div>
        <div>
          <RouterLink
            to="/login"
            class="px-4 py-2 rounded-lg border border-slate-300 hover:bg-slate-100 text-sm transition"
          >Sign In</RouterLink>
        </div>
      </div>
    </header>

    <!-- HERO -->
    <section class="relative isolate max-w-7xl mx-auto px-6 py-28 text-center">
      <h1 class="text-4xl md:text-5xl font-bold tracking-tight">
        Ask your An Assistant. <br/>
        <span class="text-indigo-600">Get answers instantly.</span>
      </h1>
      <p class="mt-4 max-w-xl mx-auto text-slate-600 text-base">
        Upload policies, playbooks, reports, and spreadsheets. Your assistant answers questions, explains procedures, and builds charts — all private and secure.
      </p>
      <div class="mt-8 flex justify-center gap-4">
        <RouterLink to="/login" class="btn-primary">Try with your documents</RouterLink>
        <a href="#how-it-works" class="btn-secondary">See how it works</a>
      </div>
    </section>

    <!-- KEY BENEFITS -->
    <section class="bg-white border-t border-slate-200 py-20">
      <div class="max-w-7xl mx-auto px-6 grid md:grid-cols-3 gap-12 text-center">
        <div class="space-y-2">
          <div class="text-3xl">🧩</div>
          <h3 class="font-semibold text-lg">Multi-tenant by design</h3>
          <p class="text-slate-500 text-sm">Serve multiple clients with isolated workspaces, indexes, and chat history.</p>
        </div>
        <div class="space-y-2">
          <div class="text-3xl">🔑</div>
          <h3 class="font-semibold text-lg">Role-aware answers</h3>
          <p class="text-slate-500 text-sm">Responses adapt based on HR, managers, execs, or employees access.</p>
        </div>
        <div class="space-y-2">
          <div class="text-3xl">📊</div>
          <h3 class="font-semibold text-lg">Data & financial analysis</h3>
          <p class="text-slate-500 text-sm">Ask for revenue, expenses, and net-profit tables with charts straight from your reports.</p>
        </div>
      </div>
    </section>

    <!-- HOW IT WORKS -->
    <section id="how-it-works" class="py-20 bg-slate-50">
      <div class="max-w-4xl mx-auto px-6 text-center space-y-6">
        <h2 class="text-2xl font-semibold">How it works</h2>
        <p class="text-slate-500 text-sm">Built for consultancies, multi-brand groups, and internal teams who need AI respecting tenant boundaries.</p>
        <div class="mt-10 grid md:grid-cols-3 gap-8 text-left">
          <div class="space-y-2">
            <h3 class="font-semibold text-indigo-600">1. Onboard tenants</h3>
            <p class="text-slate-600 text-sm">Admins create workspaces, configure collections, and invite team members in minutes.</p>
          </div>
          <div class="space-y-2">
            <h3 class="font-semibold text-indigo-600">2. Connect & upload</h3>
            <p class="text-slate-600 text-sm">Upload handbooks, SOPs, contracts, and reports securely. Chat history stays private.</p>
          </div>
          <div class="space-y-2">
            <h3 class="font-semibold text-indigo-600">3. Ask questions</h3>
            <p class="text-slate-600 text-sm">Get clear, grounded answers and charts based on your internal data — not generic AI.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CONTACT -->
    <section id="contact" class="py-20 bg-white border-t border-slate-200">
      <div class="max-w-4xl mx-auto px-6 text-center space-y-6">
        <h2 class="text-2xl font-semibold">Contact us</h2>
        <p class="text-slate-500 text-sm">Share your use case — we’ll get back to you directly by email.</p>
        <RouterLink to="/login" class="btn-primary">Open the app</RouterLink>
      </div>
    </section>

    <!-- FOOTER -->
    <footer class="bg-slate-50 border-t border-slate-200 py-6 text-center text-xs text-slate-500">
      © {{ new Date().getFullYear() }} Company Guideline Assistant. All rights reserved.
    </footer>

  </main>
</template>


<script >
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

