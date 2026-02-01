<template>
  <section class="relative min-h-[90vh] flex items-center justify-center pt-12">
    
    <div class="absolute inset-0 z-0 pointer-events-none">
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full 
                  bg-[radial-gradient(circle_at_center,rgba(99,102,241,0.05)_0%,transparent_70%)]
                  dark:bg-[radial-gradient(circle_at_center,rgba(16,185,129,0.03)_0%,transparent_70%)]">
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-8 w-full grid lg:grid-cols-2 gap-16 items-center">
      
      <div class="space-y-10 relative z-10">
        <div class="space-y-6">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-sm border border-indigo-500/20 dark:border-emerald-500/20 bg-indigo-500/5 dark:bg-emerald-500/5 text-indigo-600 dark:text-emerald-400 font-mono text-[9px] tracking-[0.3em] uppercase">
            Institutional Privacy Layer
          </div>

          <h1 class="font-black leading-[0.95] tracking-tighter text-slate-900 dark:text-white italic"
              style="font-size: clamp(3rem, 7vw, 7.5rem);">
            OWN YOUR <br/>
            <span class="text-indigo-600 dark:text-emerald-400">MEMORY.</span>
          </h1>

          <p class="max-w-md text-lg md:text-xl text-slate-600 dark:text-slate-400 font-medium leading-relaxed">
            The private knowledge engine for multi-subsidiary groups. 
            Ground your AI in <span class="text-slate-900 dark:text-white border-b-2 border-indigo-500/20">authorized internal data</span> with zero cross-tenant leakage.
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-6">
          <button class="px-10 py-5 bg-slate-900 dark:bg-emerald-500 text-white dark:text-black font-black uppercase text-xs tracking-widest hover:shadow-2xl hover:-translate-y-1 transition-all active:scale-95">
            Initialize Nexus
          </button>
          <a href="#how-it-works" class="group flex items-center gap-3 font-mono text-[10px] tracking-widest uppercase text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors">
            Process Logic 
            <span class="material-symbols-rounded text-sm group-hover:translate-x-1 transition-transform">arrow_forward</span>
          </a>
        </div>
      </div>

      <div 
        class="relative perspective-1000 group hidden lg:block"
        @mousemove="handleVaultTilt"
        @mouseleave="resetVaultTilt"
      >
        <div 
          ref="vaultCard"
          class="relative z-20 transition-transform duration-300 ease-out 
                 bg-white/80 dark:bg-white/[0.02] backdrop-blur-3xl 
                 border border-slate-200 dark:border-white/10 rounded-[40px] p-1 shadow-2xl"
        >
          <div class="bg-slate-50 dark:bg-[#05070a] rounded-[38px] p-8 overflow-hidden">
            <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none bg-[repeating-linear-gradient(45deg,transparent,transparent_20px,rgba(16,185,129,0.03)_20px,rgba(16,185,129,0.03)_40px)]"></div>

            <header class="flex justify-between items-start mb-10">
              <div class="space-y-1">
                <h3 class="text-[10px] font-mono font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Isolation Engine</h3>
                <p class="text-sm font-bold text-slate-900 dark:text-white">Boundary: Org_01_Secure</p>
              </div>
              <span class="px-2 py-1 rounded bg-emerald-500/10 text-emerald-500 text-[9px] font-black uppercase tracking-tighter border border-emerald-500/20">
                Verified
              </span>
            </header>

            <div class="space-y-6">
              <div class="p-4 rounded-2xl bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10">
                <div class="flex items-center gap-3 mb-3">
                  <div class="w-1.5 h-1.5 rounded-full bg-indigo-600 dark:bg-emerald-500 animate-pulse"></div>
                  <span class="text-[10px] font-mono text-slate-500 uppercase tracking-widest">Active Search Context</span>
                </div>
                <div class="h-2 w-3/4 bg-slate-200 dark:bg-white/10 rounded-full mb-2"></div>
                <div class="h-2 w-1/2 bg-slate-200 dark:bg-white/10 rounded-full"></div>
              </div>

              <div class="pt-4 border-t border-slate-200 dark:border-white/5">
                <p class="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed italic">
                  "Only document vectors within the **Tenant Namespace** are pulled into the inference window. Cross-org visibility is restricted by the **ACL Controller**."
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="absolute -top-6 -right-6 w-32 h-32 bg-indigo-500/10 dark:bg-emerald-500/10 blur-3xl rounded-full"></div>
        <div class="absolute -bottom-10 -left-10 w-48 h-48 bg-slate-200 dark:bg-indigo-500/5 blur-3xl rounded-full"></div>
      </div>

    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';

const vaultCard = ref<HTMLElement | null>(null);
const tilt = reactive({ x: 0, y: 0 });

const handleVaultTilt = (e: MouseEvent) => {
  if (!vaultCard.value) return;
  const rect = vaultCard.value.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  const centerX = rect.width / 2;
  const centerY = rect.height / 2;
  const rotateX = (centerY - y) / 20; // Subtle movement
  const rotateY = (x - centerX) / 20;
  vaultCard.value.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
};

const resetVaultTilt = () => {
  if (!vaultCard.value) return;
  vaultCard.value.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg)`;
};
</script>

<style scoped>
/* High-Density Typography */
h1 {
  font-family: 'Instrument Sans', sans-serif;
  font-style: italic;
  font-weight: 900;
}

div, p, button, span {
  font-family: 'JetBrains Mono', monospace;
}
</style>