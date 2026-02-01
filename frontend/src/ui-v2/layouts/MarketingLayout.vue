<template>
  <div 
    class="min-h-screen transition-colors duration-700
           bg-slate-50 dark:bg-[#020406] text-slate-900 dark:text-slate-100 font-sans"
  >
    <header class="fixed top-0 inset-x-0 z-[100] px-6 py-4 pointer-events-none">
      <div class="max-w-7xl mx-auto flex items-center justify-between 
                  bg-white/70 dark:bg-white/[0.03] backdrop-blur-2xl 
                  border border-slate-200/50 dark:border-white/10 
                  rounded-2xl px-6 py-3 shadow-sm pointer-events-auto">

        <div class="flex items-center gap-4 group cursor-pointer">
          <div class="relative">
            <div class="h-10 w-10 rounded-xl bg-indigo-600 dark:bg-emerald-500 
                        flex items-center justify-center transition-transform group-hover:rotate-12">
              <span class="text-white dark:text-black font-black text-xs">AS</span>
            </div>
            <div class="absolute -bottom-1 -right-1 h-3 w-3 rounded-full bg-emerald-500 border-2 border-white dark:border-[#020406]">
              <div class="absolute inset-0 rounded-full bg-emerald-500 animate-ping opacity-40"></div>
            </div>
          </div>
          <div class="flex flex-col">
            <span class="font-black text-sm tracking-tighter uppercase leading-none">ASKMI</span>
            <span class="text-[9px] font-mono text-slate-500 dark:text-emerald-500/60 uppercase tracking-widest mt-1">
              Intelligence Responses
            </span>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <button 
            @click="toggleTheme" 
            class="p-2 rounded-xl hover:bg-slate-200/50 dark:hover:bg-white/5 transition-all text-slate-500 dark:text-slate-400"
          >
            <span class="material-symbols-rounded text-[20px]">
              {{ theme === 'dark' ? 'light_mode' : 'dark_mode' }}
            </span>
          </button>

          <div class="h-6 w-[1px] bg-slate-200 dark:bg-white/10 mx-2"></div>

          <RouterLink
            to="/login"
            class="px-4 py-2 text-xs font-bold uppercase tracking-widest text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-emerald-400 transition-colors"
          >
            Access
          </RouterLink>

          <a 
            href="#contact"
            class="relative overflow-hidden bg-slate-900 dark:bg-white text-white dark:text-black px-5 py-2.5 rounded-xl text-xs font-bold uppercase tracking-tighter transition-all hover:shadow-lg active:scale-95"
          >
            <span class="relative z-10">Deploy Now</span>
          </a>
        </div>
      </div>
    </header>

    <main class="relative z-10 pt-24">
      <slot />
    </main>

    <footer class="mt-auto border-t border-slate-200 dark:border-white/5 bg-white/30 dark:bg-black/20 py-12 px-8">
      <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
        <div class="flex flex-col gap-2">
          <p class="text-[10px] font-mono text-slate-400 dark:text-slate-500 uppercase tracking-[0.3em]">
            © 2026 Intelligence Systems
          </p>
          <div class="flex gap-4 text-[9px] font-mono text-slate-400">
            <span class="flex items-center gap-1">
              <span class="w-1 h-1 rounded-full bg-emerald-500"></span> 
              Encrypted
            </span>
            <span class="flex items-center gap-1">
              <span class="w-1 h-1 rounded-full bg-emerald-500"></span> 
              Compliant
            </span>
          </div>
        </div>
        
        <div class="flex gap-8">
          <a href="#" class="text-[10px] font-mono uppercase tracking-widest text-slate-500 hover:text-indigo-600 dark:hover:text-emerald-400 transition-colors">Security</a>
          <a href="#" class="text-[10px] font-mono uppercase tracking-widest text-slate-500 hover:text-indigo-600 dark:hover:text-emerald-400 transition-colors">Privacy</a>
          <a href="#" class="text-[10px] font-mono uppercase tracking-widest text-slate-500 hover:text-indigo-600 dark:hover:text-emerald-400 transition-colors">Legal</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useTheme } from '../composables/useTheme';
const { theme } = useTheme();

const toggleTheme = () => {
  theme.value = theme.value === 'dark' ? 'light' : 'dark';
};
</script>

<style>
/* 2026 Material 3 Body Font */
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');

body {
  font-family: 'Instrument Sans', sans-serif;
  -webkit-font-smoothing: antialiased;
}

.font-mono {
  font-family: 'JetBrains Mono', monospace;
}

/* Custom Scrollbar for 2026 Sleekness */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #cbd5e120;
  border-radius: 10px;
}
</style>