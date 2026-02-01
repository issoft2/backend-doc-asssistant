<template>
  <section id="how-it-works" class="relative py-32 bg-white dark:bg-[#020406] transition-colors duration-700 overflow-hidden">
    
    <div class="absolute top-[60%] left-0 w-full h-[1px] bg-slate-200 dark:bg-white/5 z-0 hidden md:block">
      <div class="h-full bg-indigo-600 dark:bg-emerald-500 w-1/3 animate-flow-line"></div>
    </div>

    <div class="max-w-7xl mx-auto px-8 relative z-10">
      
      <div class="mb-24 space-y-4 text-center md:text-left">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-sm bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-[9px] font-mono font-bold tracking-[0.4em] uppercase text-slate-500">
          Standard Operating Procedure // SOP_v2
        </div>
        <h2 class="text-5xl lg:text-7xl font-black tracking-tighter text-slate-900 dark:text-white leading-none italic">
          KNOWLEDGE <br/>
          <span class="text-indigo-600 dark:text-emerald-400">LIFECYCLE.</span>
        </h2>
      </div>

      <div class="grid gap-8 md:grid-cols-3">
        <div
          v-for="(step, index) in steps"
          :key="index"
          class="group relative p-8 bg-white dark:bg-white/[0.02] border border-slate-200 dark:border-white/10 rounded-[32px] transition-all hover:shadow-2xl hover:-translate-y-2"
        >
          <div class="flex items-center gap-4 mb-8">
            <div class="w-12 h-12 rounded-xl bg-slate-900 dark:bg-white flex items-center justify-center text-white dark:text-black font-mono font-bold text-lg shadow-lg">
              0{{ index + 1 }}
            </div>
            <div class="h-[1px] flex-1 bg-slate-100 dark:bg-white/5"></div>
          </div>

          <div class="space-y-4">
            <h3 class="text-xl font-bold tracking-tight text-slate-900 dark:text-white uppercase">
              {{ step.title }}
            </h3>
            
            <div class="h-12 overflow-hidden">
              <p class="text-sm text-slate-500 dark:text-slate-400 leading-relaxed group-hover:-translate-y-full transition-transform duration-500">
                {{ step.description }}
              </p>
              <div class="pt-2 flex gap-2 transition-transform duration-500 group-hover:-translate-y-full">
                <span v-for="tag in step.tags" :key="tag" class="text-[9px] font-mono px-2 py-0.5 rounded-full border border-indigo-500/20 text-indigo-600 dark:text-emerald-500 dark:border-emerald-500/20">
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>

          <div class="absolute top-4 right-4 opacity-10 font-mono text-[40px] font-black italic">
            //{{ step.code }}
          </div>
        </div>
      </div>

      <div class="mt-20 flex flex-col items-center justify-center gap-4">
        <p class="font-mono text-[10px] text-slate-400 uppercase tracking-widest">End-to-End Latency: &lt; 200ms</p>
        <div class="w-px h-12 bg-gradient-to-b from-slate-200 dark:from-white/10 to-transparent"></div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const steps = [
  {
    title: "Sovereign Ingestion",
    description: "Centralize institutional data via secure cloud sync or direct encrypted upload with full org-level partitioning.",
    code: "INGEST",
    tags: ["AES-256", "S3_SYNC", "M-TENANT"]
  },
  {
    title: "ACL-Aware Indexing",
    description: "Documents are transformed into high-dimensional vectors and locked behind organization-specific security boundaries.",
    code: "VECTOR",
    tags: ["NAMESPACE", "HARD_ISO", "K_GRAPH"]
  },
  {
    title: "Grounded Synthesis",
    description: "Queries are processed within an isolated context, generating responses verified by document-level citations.",
    code: "OUTPUT",
    tags: ["RAG_CITES", "ZERO_HAL", "AUDIT"]
  },
];
</script>

<style scoped>
h2 {
  font-family: 'Instrument Sans', sans-serif;
}

h3, p, span, div {
  font-family: 'JetBrains Mono', monospace;
}

@keyframes flow-line {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(300%); }
}

.animate-flow-line {
  animation: flow-line 8s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}
</style>