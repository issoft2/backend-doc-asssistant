<template>
  <section class="relative py-40 bg-[#050505] overflow-hidden border-y border-white/5">
    <div class="absolute inset-0 opacity-[0.03] pointer-events-none mix-blend-overlay" 
         style="background-image: url('https://grainy-gradients.vercel.app/noise.svg');"></div>

    <div class="max-w-7xl mx-auto px-8 relative z-10">
      <div class="grid lg:grid-cols-2 gap-20 items-center">
        
        <div class="space-y-10">
          <div class="flex items-center gap-4 group">
            <div class="h-[1px] w-12 bg-emerald-500 group-hover:w-24 transition-all duration-700"></div>
            <span class="font-mono text-[10px] tracking-[0.4em] uppercase text-emerald-500">System_Ready // v4.02</span>
          </div>

          <h2 class="text-6xl md:text-8xl font-black tracking-tighter text-white leading-[0.85] italic uppercase">
            Initialize <br/>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-white via-white/40 to-white/10">Sovereignty.</span>
          </h2>

          <p class="max-w-md text-lg text-slate-400 font-medium leading-relaxed border-l-2 border-white/10 pl-6">
            Stop feeding public models. Deploy your private knowledge base in an isolated tenant environment today.
          </p>

          <div class="flex flex-wrap gap-6 pt-4">
            <RouterLink to="/login" 
              class="group relative px-12 py-6 bg-white text-black font-black uppercase text-[11px] tracking-[0.2em] hover:scale-105 active:scale-95 transition-all">
              Initialize Environment
              <div class="absolute -bottom-2 -right-2 w-full h-full border border-emerald-500/50 -z-10 group-hover:translate-x-1 group-hover:translate-y-1 transition-transform"></div>
            </RouterLink>
            
            <button class="px-8 py-6 border border-white/10 text-white font-mono text-[10px] uppercase tracking-widest hover:bg-white/5 transition-colors">
              Read_Docs.pdf
            </button>
          </div>
        </div>

        <div class="hidden lg:block relative h-[500px] border border-white/5 bg-white/[0.02] rounded-tr-[100px]">
          <div class="absolute inset-0 p-8 flex flex-col justify-between font-mono text-[9px] text-white/20 uppercase tracking-[0.3em]">
            <div class="flex justify-between">
              <span>Auth_Protocol: RSA_4096</span>
              <span>Uptime: 99.998%</span>
            </div>
            <div class="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent"></div>
            <div class="flex justify-between items-end">
              <span>Encryption_Active</span>
              <div class="flex gap-2">
                <div v-for="i in 4" :key="i" class="w-4 h-4 border border-white/10"></div>
              </div>
            </div>
          </div>
          <div class="absolute inset-0 flex items-center justify-center">
            <div class="w-40 h-40 border-2 border-emerald-500/20 rotate-45 animate-pulse"></div>
            <div class="absolute w-40 h-40 border border-white/5 -rotate-12"></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* DISTINCTIVE TYPE PAIRING */
h2 { font-family: 'Instrument Sans', sans-serif; letter-spacing: -0.05em; }
p, span, button, a { font-family: 'JetBrains Mono', monospace; }
</style>