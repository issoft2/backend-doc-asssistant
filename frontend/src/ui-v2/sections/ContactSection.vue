<!-- ContactSection.vue -->
<template>
  <section id="contact" class="py-24 bg-white border-t border-slate-200 relative overflow-hidden">
    <!-- Background Abstract Shape -->
    <div class="absolute inset-0 -z-10">
      <svg class="w-full h-full" viewBox="0 0 800 600" fill="none">
        <circle class="animate-slow-spin" cx="400" cy="300" r="300" fill="url(#gradContact)" fill-opacity="0.05"/>
        <defs>
          <radialGradient id="gradContact" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(400 300) rotate(90) scale(300)">
            <stop stop-color="#4f46e5"/>
            <stop offset="1" stop-color="#4f46e5" stop-opacity="0"/>
          </radialGradient>
        </defs>
      </svg>
    </div>

    <div class="max-w-3xl mx-auto px-6 space-y-8" id="hero-contact-form"> 
      <!-- Heading -->
      <h2 v-motion="fadeUp(0.1)" class="text-3xl sm:text-4xl font-extrabold text-center text-slate-900">
        Reach out for access, support, or partnerships
      </h2>
      <p v-motion="fadeUp(0.3)" class="text-center text-slate-500 text-base sm:text-lg">
        Share your use case, feedback, or questions — we’ll get back to you directly by email.
      </p>

      <!-- Contact Form -->
      <form
        @submit.prevent="submitContact"
        class="space-y-6 bg-slate-50 p-8 rounded-xl shadow-lg border border-slate-200"

      >
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            v-model="contactForm.name"
            type="text"
            placeholder="Your Name"
            required
            class="input-field rounded-lg border border-slate-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition"
          />
          <input
            v-model="contactForm.email"
            type="email"
            placeholder="Your Email"
            required
            class="input-field rounded-lg border border-slate-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition"
          />
        </div>

        <input
          v-model="contactForm.subject"
          type="text"
          placeholder="Subject"
          required
          class="input-field w-full rounded-lg border border-slate-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition"
        />

        <textarea
          v-model="contactForm.message"
          rows="5"
          placeholder="Your Message"
          required
          class="input-field w-full rounded-lg border border-slate-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-y transition"
        ></textarea>

        <div class="flex flex-col md:flex-row justify-between items-center gap-4">
          <button
            type="submit"
            class="btn-primary px-6 py-3 rounded-lg text-white font-semibold shadow hover:bg-indigo-700 transition"
            :disabled="contactSubmitting"
          >
            {{ contactSubmitting ? 'Sending…' : 'Send Message' }}
          </button>
          <div class="flex flex-col text-sm text-center md:text-left">
            <p v-if="contactSuccess" class="text-emerald-500 font-medium">Message sent successfully!</p>
            <p v-if="contactError" class="text-red-500 font-medium">{{ contactError }}</p>
          </div>
        </div>
      </form>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { sendContact } from '../../api'
import { useReducedMotion } from '@vueuse/motion'


// Motion helpers
const reducedMotion = useReducedMotion()
const baseFade = { initial: { opacity: 0, y: 16 }, enter: { opacity: 1, y: 0 } }
const heroMotion = reducedMotion.value ? {} : { ...baseFade, transition: { duration: 0.5, ease: 'easeOut' } }
const fadeUp = (delay = 0) => reducedMotion.value ? {} : { ...baseFade, transition: { duration: 0.4, delay, ease: 'easeOut' } }



const contactForm = ref({ name: '', email: '', subject: '', message: '' })
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

<style scoped>
.animate-slow-spin {
  animation: slow-spin 180s linear infinite;
}

@keyframes slow-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
