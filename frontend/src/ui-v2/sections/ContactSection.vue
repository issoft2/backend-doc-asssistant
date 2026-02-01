<template>
  <section 
    id="contact" 
    class="relative py-32 bg-slate-50 dark:bg-[#010204] transition-colors duration-700 overflow-hidden"
  >
    <div class="absolute inset-0 z-0 opacity-[0.03] dark:opacity-[0.05] pointer-events-none"
         style="background-image: radial-gradient(circle at 2px 2px, #94a3b8 1px, transparent 0); background-size: 32px 32px;">
    </div>

    <div class="max-w-7xl mx-auto px-8 relative z-10">
      <div class="grid lg:grid-cols-[0.9fr_1.1fr] gap-20 items-start">
        
        <div class="space-y-12">
          <div class="space-y-6">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 dark:bg-emerald-500/5 border border-indigo-100 dark:border-emerald-500/20 text-[10px] font-bold tracking-[0.3em] uppercase text-indigo-600 dark:text-emerald-400">
              <span class="w-1.5 h-1.5 rounded-full bg-indigo-600 dark:bg-emerald-500 animate-pulse"></span>
              Secure Channel Open
            </div>
            
            <h2 class="text-5xl lg:text-7xl font-black tracking-tighter text-slate-900 dark:text-white leading-[0.85] italic">
              INITIATE <br/>
              <span class="text-indigo-600 dark:text-emerald-400">ENGAGEMENT.</span>
            </h2>
            
            <p class="max-w-md text-lg text-slate-600 dark:text-slate-400 leading-relaxed font-medium">
              Ready to deploy institutional intelligence? Request a dedicated tenant environment or discuss custom ACL integration for your organization.
            </p>
          </div>

          <div class="space-y-8 pt-8 border-t border-slate-200 dark:border-white/5">
            <div v-for="item in trustItems" :key="item.label" class="flex gap-4 group">
              <div class="h-10 w-10 shrink-0 rounded-lg bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 flex items-center justify-center text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-emerald-400 transition-colors">
                <span class="material-symbols-rounded text-[20px]">{{ item.icon }}</span>
              </div>
              <div>
                <h4 class="text-[11px] font-mono font-bold uppercase tracking-widest text-slate-900 dark:text-white">{{ item.label }}</h4>
                <p class="text-xs text-slate-500 dark:text-slate-500 font-mono mt-1">{{ item.desc }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="relative">
          <form 
            @submit.prevent="submitContact"
            class="relative z-10 bg-white/80 dark:bg-white/[0.02] backdrop-blur-3xl border border-slate-200 dark:border-white/10 rounded-[40px] p-10 shadow-2xl space-y-8"
          >
            <div class="flex justify-between items-center mb-4 text-[9px] font-mono text-slate-400 uppercase tracking-widest">
              <span>Form_ID: XF-2026</span>
              <span class="text-emerald-500 flex items-center gap-1">
                <span class="w-1 h-1 bg-emerald-500 rounded-full"></span> SSL_ENCRYPTED
              </span>
            </div>

            <div class="grid grid-cols-2 gap-6">
              <div class="space-y-2">
                <label class="text-[10px] font-mono font-bold text-slate-500 uppercase px-1">Identity</label>
                <input v-model="contactForm.name" type="text" placeholder="Your Name" required
                       class="w-full bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-2xl px-5 py-4 text-sm focus:ring-2 focus:ring-indigo-500/20 dark:focus:ring-emerald-500/20 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600">
              </div>
              <div class="space-y-2">
                <label class="text-[10px] font-mono font-bold text-slate-500 uppercase px-1">Contact_Route</label>
                <input v-model="contactForm.email" type="email" placeholder="Email Address" required
                       class="w-full bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-2xl px-5 py-4 text-sm focus:ring-2 focus:ring-indigo-500/20 dark:focus:ring-emerald-500/20 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600">
              </div>
            </div>

            <div class="space-y-2">
              <label class="text-[10px] font-mono font-bold text-slate-500 uppercase px-1">Context_Subject</label>
              <input v-model="contactForm.subject" type="text" placeholder="Inquiry Type" required
                     class="w-full bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-2xl px-5 py-4 text-sm focus:ring-2 focus:ring-indigo-500/20 dark:focus:ring-emerald-500/20 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600">
            </div>

            <div class="space-y-2">
              <label class="text-[10px] font-mono font-bold text-slate-500 uppercase px-1">Transmission_Body</label>
              <textarea v-model="contactForm.message" rows="4" placeholder="How can we help your organization?" required
                        class="w-full bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-2xl px-5 py-4 text-sm focus:ring-2 focus:ring-indigo-500/20 dark:focus:ring-emerald-500/20 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600 resize-none"></textarea>
            </div>

            <button 
              type="submit" 
              :disabled="contactSubmitting"
              class="group relative w-full overflow-hidden bg-slate-900 dark:bg-white py-5 rounded-2xl flex items-center justify-center transition-all hover:shadow-2xl active:scale-[0.98]"
            >
              <div class="absolute inset-0 bg-indigo-600 dark:bg-emerald-500 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
              <span class="relative z-10 text-xs font-black uppercase tracking-[0.2em] text-white dark:text-black">
                {{ contactSubmitting ? 'Transmitting...' : 'Initiate Connection' }}
              </span>
            </button>

            <div class="flex justify-center h-4">
              <p v-if="contactSuccess" class="text-[10px] font-mono font-bold text-emerald-500 uppercase">Transmission Confirmed // 200 OK</p>
              <p v-if="contactError" class="text-[10px] font-mono font-bold text-red-500 uppercase">{{ contactError }}</p>
            </div>
          </form>

          <div class="absolute -z-10 -bottom-10 -right-10 w-64 h-64 bg-indigo-500/10 dark:bg-emerald-500/5 blur-[100px] rounded-full"></div>
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
const contactError = ref('')

const trustItems = [
  { icon: 'lock', label: 'Privacy First', desc: 'No data is used for model training.' },
  { icon: 'shield', label: 'Encrypted', desc: 'End-to-end encryption on all queries.' },
  { icon: 'dns', label: 'Residency', desc: 'Hosted in your region of choice.' }
]

async function submitContact() {
  contactSubmitting.value = true
  contactSuccess.value = false
  contactError.value = ''
  try {
    // Simulated API call logic
    await new Promise(r => setTimeout(r, 1500))
    contactSuccess.value = true
    contactForm.value = { name: '', email: '', subject: '', message: '' }
  } catch (e: any) {
    contactError.value = 'CONNECTION_REFUSED_RETRY'
  } finally {
    contactSubmitting.value = false
  }
}
</script>

<style scoped>
h2 { font-family: 'Instrument Sans', sans-serif; }
div, p, label, input, textarea, button, span { font-family: 'JetBrains Mono', monospace; }

/* Custom field interaction */
.input-field:focus::placeholder {
  opacity: 0.3;
  transform: translateX(10px);
  transition: all 0.3s ease;
}
</style>