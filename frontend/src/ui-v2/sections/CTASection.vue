<template>
  <section 
    class="relative py-32 bg-slate-50 dark:bg-[#020406] transition-colors duration-700 overflow-hidden"
  >
    <div class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-slate-200 dark:via-white/10 to-transparent"></div>
    
    <div class="max-w-5xl mx-auto px-8 relative z-10">
      <div 
        class="relative overflow-hidden bg-slate-900 dark:bg-white/[0.02] border border-slate-800 dark:border-white/10 rounded-[48px] p-12 md:p-20 text-center shadow-2xl"
      >
        <div class="absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-96 bg-indigo-500/20 dark:bg-emerald-500/10 blur-[120px] rounded-full pointer-events-none"></div>

        <div class="relative z-10 space-y-8">
          <div class="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-white/5 border border-white/10">
            <div class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </div>
            <span class="text-[10px] font-mono font-bold tracking-[0.2em] text-white uppercase">Instance_Ready // Port_8080</span>
          </div>

          <h2 class="text-4xl md:text-6xl font-black tracking-tighter text-white leading-[0.9] italic">
            SECURE YOUR <br/>
            <span class="text-transparent bg-clip-text bg-gradient-to-b from-white to-white/40">INSTITUTIONAL MEMORY.</span>
          </h2>

          <p class="max-w-xl mx-auto text-lg text-slate-400 font-medium leading-relaxed">
            Move beyond generic chat. Deploy a sovereign intelligence layer where your data is isolated, your ACLs are respected, and your answers are grounded.
          </p>

          <div class="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6">
            <RouterLink
              to="/login"
              class="group relative px-10 py-5 bg-white text-black font-black uppercase text-xs tracking-widest rounded-2xl transition-all hover:shadow-[0_0_40px_rgba(255,255,255,0.2)] hover:-translate-y-1 active:scale-95 overflow-hidden"
            >
              <span class="relative z-10">Initialize Environment</span>
              <div class="absolute inset-0 bg-indigo-600 dark:bg-emerald-500 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
              <span class="absolute inset-0 flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 font-black uppercase text-xs tracking-widest">
                Deploy Now
              </span>
            </RouterLink>

            <a
              href="#how-it-works"
              class="px-8 py-5 border border-white/10 text-white font-mono text-[10px] tracking-widest uppercase rounded-2xl hover:bg-white/5 transition-all"
            >
              System Architecture
            </a>
          </div>

          <div class="pt-12 flex items-center justify-center gap-8 opacity-40">
            <div v-for="audit in ['SOC2', 'AES-256', 'HIPAA', 'GDPR']" :key="audit" class="text-[9px] font-mono font-bold text-white tracking-widest">
              [{{ audit }}]
            </div>
          </div>
        </div>

        <div class="absolute bottom-0 left-0 w-full h-1/2 opacity-[0.03] pointer-events-none overflow-hidden">
          <pre class="text-[8px] text-white text-left p-4 leading-none">
            {{ `
              TENANT_INIT: SUBSCRIBER_ALPHA
              BLOCK_SIZE: 1024_VEC
              ACL_ENFORCEMENT: STRICT
              ENCRYPTION: AES_GCM_256
              STATUS: LISTENING_FOR_HANDSHAKE...
            ` }}
          </pre>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
// Logic for interaction can be added here
</script>

<style scoped>
h2 {
  font-family: 'Instrument Sans', sans-serif;
}

p, span, a, div, pre {
  font-family: 'JetBrains Mono', monospace;
}

/* Subtly moving noise texture to make it feel "active" */
.bg-white\/\[0\.02\]::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
  opacity: 0.05;
  pointer-events: none;
}
</style>