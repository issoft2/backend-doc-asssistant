<template>
  <section id="features" class="relative py-32 overflow-hidden bg-slate-50 dark:bg-[#020406] transition-colors duration-700">
    
    <div class="absolute inset-0 z-0 opacity-[0.03] dark:opacity-[0.05] pointer-events-none" 
         style="background-image: linear-gradient(#94a3b8 1px, transparent 1px), linear-gradient(90deg, #94a3b8 1px, transparent 1px); background-size: 50px 50px;">
    </div>

    <div class="max-w-7xl mx-auto px-8 relative z-10">
      
      <div class="flex flex-col lg:flex-row justify-between items-end mb-20 gap-8">
        <div class="max-w-2xl space-y-4">
          <div class="font-mono text-[10px] tracking-[0.4em] text-indigo-600 dark:text-emerald-500 uppercase">
            System Capabilities // v4.0
          </div>
          <h2 class="text-5xl lg:text-7xl font-black tracking-tighter text-slate-900 dark:text-white leading-[0.85] italic">
            ENGINEERED FOR <br/>
            <span class="opacity-30 dark:opacity-20">SOVEREIGNTY.</span>
          </h2>
        </div>
        <p class="max-w-xs text-sm font-mono text-slate-500 dark:text-slate-400 leading-relaxed border-l border-slate-200 dark:border-white/10 pl-6">
          Hardened infrastructure designed for the specific rigors of government and regulated enterprise data flows.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
        
        <div class="md:col-span-8 group relative overflow-hidden bg-white dark:bg-white/[0.02] border border-slate-200 dark:border-white/10 p-8 rounded-3xl transition-all hover:border-indigo-500/50 dark:hover:border-emerald-500/50">
          <div class="relative z-10 h-full flex flex-col justify-between">
            <div class="space-y-4">
              <span class="material-symbols-rounded text-3xl text-indigo-600 dark:text-emerald-500">shield_lock</span>
              <h3 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-white uppercase">Hard Tenant Isolation</h3>
              <p class="max-w-md text-slate-600 dark:text-slate-400 font-medium">
                Physical logic separation at the vector level. We enforce strict namespace boundaries, ensuring one organization’s intelligence never bleeds into another.
              </p>
            </div>
            
            <div class="mt-12 p-4 bg-slate-50 dark:bg-black/40 rounded-xl border border-slate-100 dark:border-white/5 font-mono text-[10px] opacity-60 group-hover:opacity-100 transition-opacity">
              <div class="flex justify-between text-emerald-500 mb-2">
                <span>[TENANT_ENFORCER]</span>
                <span>STATUS: VERIFIED</span>
              </div>
              <div class="text-slate-500">>> Request from ORG_ID_292 blocked from accessing Namespace_882</div>
            </div>
          </div>
          <div class="absolute -bottom-20 -right-20 w-64 h-64 bg-indigo-500/5 dark:bg-emerald-500/5 blur-[80px] rounded-full group-hover:bg-indigo-500/10 dark:group-hover:bg-emerald-500/10 transition-colors"></div>
        </div>

        <div class="md:col-span-4 group bg-slate-900 dark:bg-white/[0.03] p-8 rounded-3xl border border-slate-800 dark:border-white/10 transition-all hover:-translate-y-1">
          <div class="h-full flex flex-col">
            <span class="material-symbols-rounded text-3xl text-emerald-400 mb-6">database</span>
            <h3 class="text-xl font-bold text-white uppercase mb-4">Grounded Provenance</h3>
            <p class="text-slate-400 text-sm leading-relaxed mb-8">
              Zero-hallucination policy. Every response is anchored to a specific page, paragraph, and document ID with full audit trails.
            </p>
            <div class="mt-auto space-y-2">
              <div v-for="i in 3" :key="i" class="h-1 bg-white/5 rounded-full overflow-hidden">
                <div class="h-full bg-emerald-500/40" :style="{ width: 100 - (i * 20) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="md:col-span-4 group bg-white dark:bg-white/[0.02] border border-slate-200 dark:border-white/10 p-8 rounded-3xl hover:shadow-xl transition-all">
          <span class="material-symbols-rounded text-3xl text-indigo-500 mb-6">fingerprint</span>
          <h3 class="text-xl font-bold uppercase mb-3">Granular ACL</h3>
          <p class="text-slate-500 dark:text-slate-400 text-sm">Role-based access down to individual collections. Perfect for hierarchical umbrella organizations.</p>
        </div>

        <div class="md:col-span-8 group relative overflow-hidden bg-white dark:bg-white/[0.02] border border-slate-200 dark:border-white/10 p-8 rounded-3xl">
          <div class="flex flex-col md:flex-row gap-8 items-center">
            <div class="flex-1 space-y-4">
              <h3 class="text-xl font-bold uppercase">Infinite Ingestion</h3>
              <p class="text-slate-500 dark:text-slate-400 text-sm">Ingest policies, playbooks, and structured spreadsheets at scale. Our pipeline handles OCR, table-parsing, and complex document structures automatically.</p>
            </div>
            <div class="flex gap-2">
              <div v-for="i in 4" :key="i" class="w-12 h-16 rounded-lg border border-slate-200 dark:border-white/10 flex items-center justify-center bg-slate-50 dark:bg-white/5 group-hover:border-indigo-500 transition-colors">
                <span class="material-symbols-rounded text-slate-300 dark:text-slate-700">description</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
// Standardizing on Google Material Symbols Rounded
</script>

<style scoped>
h2 {
  font-family: 'Instrument Sans', sans-serif;
}

h3, p, span, div {
  font-family: 'JetBrains Mono', monospace;
}

/* Custom "Magnetic" card feel */
.group {
  transition: all 0.4s cubic-bezier(0.2, 0, 0, 1);
}
</style>