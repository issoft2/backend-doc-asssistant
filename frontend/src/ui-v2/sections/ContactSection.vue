<template>
  <section 
    id="contact" 
    class="relative py-32 bg-white dark:bg-[#080808] transition-colors duration-700 overflow-hidden"
  >
    <div class="absolute inset-0 opacity-[0.02] dark:opacity-[0.04] pointer-events-none mix-blend-overlay" 
         style="background-image: url('https://grainy-gradients.vercel.app/noise.svg');"></div>

    <div class="max-w-7xl mx-auto px-8 relative z-10">
      <div class="grid lg:grid-cols-[1fr_1.1fr] gap-24 items-center">
        
        <div class="space-y-12">
          <div class="space-y-8">
            <div class="h-px w-16 bg-indigo-600 dark:bg-emerald-500"></div>
            
            <h2 class="text-6xl lg:text-8xl font-black tracking-tighter text-slate-900 dark:text-white leading-[0.85] uppercase italic">
              Let's talk <br/>
              <span class="text-indigo-600 dark:text-emerald-500">Strategy.</span>
            </h2>
            
            <p class="max-w-md text-xl text-slate-600 dark:text-slate-400 leading-relaxed font-medium">
              Enterprise-grade AI requires more than a login. We help you map your data architecture and ensure total privacy for your team.
            </p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-8 pt-8 border-t border-slate-200 dark:border-white/10">
            <div v-for="item in trustItems" :key="item.label" class="space-y-3">
              <h4 class="text-[11px] font-mono font-bold uppercase tracking-[0.2em] text-indigo-600 dark:text-emerald-500">{{ item.label }}</h4>
              <p class="text-xs text-slate-500 dark:text-slate-500 leading-relaxed">{{ item.desc }}</p>
            </div>
          </div>
        </div>

        <div class="relative group">
          <div class="relative z-10 bg-white dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-sm p-12 shadow-[40px_40px_80px_-20px_rgba(0,0,0,0.1)] dark:shadow-none">
            
            <form @submit.prevent="submitContact" class="space-y-10">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-10">
                <div class="relative group">
                  <input v-model="contactForm.name" type="text" required
                         class="peer w-full bg-transparent border-b-2 border-slate-200 dark:border-white/10 py-3 text-slate-900 dark:text-white focus:border-indigo-600 dark:focus:border-emerald-500 outline-none transition-all placeholder-transparent">
                  <label class="absolute left-0 top-3 text-slate-400 text-sm transition-all peer-focus:-top-6 peer-focus:text-[10px] peer-focus:uppercase peer-focus:tracking-widest peer-focus:font-bold peer-focus:text-indigo-600 dark:peer-focus:text-emerald-500 peer-valid:-top-6 peer-valid:text-[10px]">Full Name</label>
                </div>

                <div class="relative group">
                  <input v-model="contactForm.email" type="email" required
                         class="peer w-full bg-transparent border-b-2 border-slate-200 dark:border-white/10 py-3 text-slate-900 dark:text-white focus:border-indigo-600 dark:focus:border-emerald-500 outline-none transition-all placeholder-transparent">
                  <label class="absolute left-0 top-3 text-slate-400 text-sm transition-all peer-focus:-top-6 peer-focus:text-[10px] peer-focus:uppercase peer-focus:tracking-widest peer-focus:font-bold peer-focus:text-indigo-600 dark:peer-focus:text-emerald-500 peer-valid:-top-6 peer-valid:text-[10px]">Work Email</label>
                </div>
              </div>

              <div class="relative group">
                <input v-model="contactForm.subject" type="text" required
                       class="peer w-full bg-transparent border-b-2 border-slate-200 dark:border-white/10 py-3 text-slate-900 dark:text-white focus:border-indigo-600 dark:focus:border-emerald-500 outline-none transition-all placeholder-transparent">
                <label class="absolute left-0 top-3 text-slate-400 text-sm transition-all peer-focus:-top-6 peer-focus:text-[10px] peer-focus:uppercase peer-focus:tracking-widest peer-focus:font-bold peer-focus:text-indigo-600 dark:peer-focus:text-emerald-500 peer-valid:-top-6 peer-valid:text-[10px]">Organization</label>
              </div>

              <div class="relative group">
                <textarea v-model="contactForm.message" rows="3" required
                          class="peer w-full bg-transparent border-b-2 border-slate-200 dark:border-white/10 py-3 text-slate-900 dark:text-white focus:border-indigo-600 dark:focus:border-emerald-500 outline-none transition-all placeholder-transparent resize-none"></textarea>
                <label class="absolute left-0 top-3 text-slate-400 text-sm transition-all peer-focus:-top-6 peer-focus:text-[10px] peer-focus:uppercase peer-focus:tracking-widest peer-focus:font-bold peer-focus:text-indigo-600 dark:peer-focus:text-emerald-500 peer-valid:-top-6 peer-valid:text-[10px]">Tell us about your project</label>
              </div>

              <button 
                type="submit" 
                :disabled="contactSubmitting"
                class="w-full bg-slate-900 dark:bg-white text-white dark:text-black py-6 rounded-sm text-[11px] font-black uppercase tracking-[0.3em] hover:bg-indigo-600 dark:hover:bg-emerald-500 dark:hover:text-black transition-all active:scale-[0.98]"
              >
                {{ contactSubmitting ? 'Sending Request...' : 'Send Message' }}
              </button>

              <p v-if="contactSuccess" class="text-center text-[10px] font-mono font-bold text-emerald-500 uppercase tracking-widest">
                Thank you. We'll be in touch shortly.
              </p>
            </form>
          </div>

          <div class="absolute -bottom-4 -right-4 w-full h-full border-2 border-slate-200 dark:border-white/10 -z-10 transition-transform group-hover:translate-x-2 group-hover:translate-y-2"></div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const contactForm = ref({ name: '', email: '', subject: '', message: '' })
const contactSubmitting = ref(false)
const contactSuccess = ref(false)

const trustItems = [
  { label: 'Data Sovereignty', desc: 'Your data is never used to train public models. Period.' },
  { label: 'Cloud or On-Prem', desc: 'Deploy on our secure cloud or within your own VPC.' }
]

async function submitContact() {
  contactSubmitting.value = true
  await new Promise(r => setTimeout(r, 1500))
  contactSuccess.value = true
  contactSubmitting.value = false
}
</script>

<style scoped>
h2 { font-family: 'Instrument Sans', sans-serif; letter-spacing: -0.04em; }
p, h4, label, button { font-family: 'JetBrains Mono', monospace; }

/* Remove default autofill background in dark mode */
input:-webkit-autofill,
input:-webkit-autofill:hover, 
input:-webkit-autofill:focus {
  -webkit-text-fill-color: inherit;
  -webkit-box-shadow: 0 0 0px 1000px transparent inset;
  transition: background-color 5000s ease-in-out 0s;
}
</style>