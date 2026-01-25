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
    <section
      v-motion="heroMotion"
      class="relative isolate max-w-7xl mx-auto px-6 py-28 text-center"
    >
      <h1 class="text-4xl md:text-5xl font-bold tracking-tight">
        Ask your Assistant. <br/>
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
        <Feature
          v-motion="fadeUp(0.1)"
          icon="🧩"
          title="Multi-tenant by design"
          text="Serve multiple clients with isolated workspaces, indexes, and chat history."
        />
        <Feature
          v-motion="fadeUp(0.3)"
          icon="🔑"
          title="Role-aware answers"
          text="Responses adapt based on HR, managers, execs, or employees access."
        />
        <Feature
          v-motion="fadeUp(0.5)"
          icon="📊"
          title="Data & financial analysis"
          text="Ask for revenue, expenses, and net-profit tables with charts straight from your reports."
        />
      </div>
    </section>

    <!-- HOW IT WORKS -->
    <section id="how-it-works" class="py-20 bg-slate-50">
      <div class="max-w-4xl mx-auto px-6 text-center space-y-6">
        <h2 v-motion="fadeUp(0.1)" class="text-2xl font-semibold">How it works</h2>
        <p v-motion="fadeUp(0.3)" class="text-slate-500 text-sm">
          Built for consultancies, multi-brand groups, and internal teams who need AI respecting tenant boundaries.
        </p>
        <div class="mt-10 grid md:grid-cols-3 gap-8 text-left">
          <div v-motion="fadeUp(0.5)" class="space-y-2">
            <h3 class="font-semibold text-indigo-600">1. Onboard tenants</h3>
            <p class="text-slate-600 text-sm">Admins create workspaces, configure collections, and invite team members in minutes.</p>
          </div>
          <div v-motion="fadeUp(0.7)" class="space-y-2">
            <h3 class="font-semibold text-indigo-600">2. Connect & upload</h3>
            <p class="text-slate-600 text-sm">Upload handbooks, SOPs, contracts, and reports securely. Chat history stays private.</p>
          </div>
          <div v-motion="fadeUp(0.9)" class="space-y-2">
            <h3 class="font-semibold text-indigo-600">3. Ask questions</h3>
            <p class="text-slate-600 text-sm">Get clear, grounded answers and charts based on your internal data — not generic AI.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CONTACT -->
    <section id="contact" class="py-20 bg-white border-t border-slate-200">
      <div class="max-w-2xl mx-auto px-6 space-y-6">
        <h2 v-motion="fadeUp(0.1)" class="text-2xl font-semibold text-center">Contact Us</h2>
        <p v-motion="fadeUp(0.3)" class="text-slate-500 text-sm text-center">
          Share your use case — we’ll get back to you directly by email.
        </p>

        <form @submit.prevent="submitContact" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              v-model="contactForm.name"
              type="text"
              placeholder="Name"
              required
              class="input-field"
            />
            <input
              v-model="contactForm.email"
              type="email"
              placeholder="Email"
              required
              class="input-field"
            />
          </div>
          <input
            v-model="contactForm.subject"
            type="text"
            placeholder="Subject"
            required
            class="input-field w-full"
          />
          <textarea
            v-model="contactForm.message"
            rows="4"
            placeholder="Message"
            required
            class="input-field w-full resize-y"
          ></textarea>
          <div class="flex justify-between items-center">
            <button
              type="submit"
              class="btn-primary"
              :disabled="contactSubmitting"
            >
              {{ contactSubmitting ? 'Sending…' : 'Send Message' }}
            </button>
            <p v-if="contactSuccess" class="text-emerald-500 text-sm">Message sent!</p>
            <p v-if="contactError" class="text-red-500 text-sm">{{ contactError }}</p>
          </div>
        </form>
      </div>
    </section>

    <!-- FOOTER -->
    <footer class="bg-slate-50 border-t border-slate-200 py-6 text-center text-xs text-slate-500">
      © {{ new Date().getFullYear() }} Company Guideline Assistant. All rights reserved.
    </footer>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useReducedMotion } from '@vueuse/motion'
import { sendContact } from '../api'

const reducedMotion = useReducedMotion()

const baseFade = {
  initial: { opacity: 0, y: 16 },
  enter: { opacity: 1, y: 0 },
}

const heroMotion = reducedMotion.value
  ? {}
  : { ...baseFade, transition: { duration: 0.5, ease: 'easeOut' } }

const fadeUp = (delay = 0) =>
  reducedMotion.value
    ? {}
    : { ...baseFade, transition: { duration: 0.4, delay, ease: 'easeOut' } }

// Contact form state
const contactForm = ref({
  name: '',
  email: '',
  subject: '',
  message: '',
})
const contactSubmitting = ref(false)
const contactSuccess = ref(false)
const contactError = ref('')

async function submitContact() {
  contactSubmitting.value = true
  contactSuccess.value = false
  contactError.value = ''
  try {
    await sendContact(contactForm.value)
    contactSuccess.value = true
    contactForm.value = { name: '', email: '', subject: '', message: '' }
  } catch (e) {
    contactError.value = e.response?.data?.detail || 'Failed to send message.'
  } finally {
    contactSubmitting.value = false
  }
}
</script>


