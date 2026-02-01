<template>
  <footer class="bg-[#050505] text-white py-24 border-t border-white/5 font-bold">
    <div class="max-w-7xl mx-auto px-8">
      
      <div class="grid grid-cols-1 md:grid-cols-4 gap-16 pb-20">
        <div class="col-span-1 space-y-8">
          <div class="text-xl font-black italic tracking-tighter uppercase">ASKMI®</div>
          <div class="space-y-2">
            <div class="flex items-center gap-2 text-[10px] text-emerald-700">
              <span class="w-1.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
              ALL SYSTEMS OPERATIONAL
            </div>
            <p class="text-[10px] text-slate-500 leading-loose uppercase tracking-widest">
              Data Intelligence <br/> 
              Privacy First <br/>
              Enterprise Ready <br />
              Generate Financial Focast <br/>
            </p>
          </div>
        </div>

        <div v-for="group in linkGroups" :key="group.title" class="space-y-6">
          <h4 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]">{{ group.title }}</h4>
          <ul class="space-y-3">
            <li v-for="link in group.links" :key="link">
              <a href="#" class="text-[11px] text-slate-400 hover:text-white transition-colors flex items-center group">
                <span class="opacity-0 group-hover:opacity-100 transition-opacity mr-2 text-emerald-500">→</span>
                {{ link }}
              </a>
            </li>
          </ul>
        </div>
      </div>

      
    </div>
  </footer>
</template>

<script setup>
const linkGroups = [
  { title: 'Core_Logic', links: ['Neural_Engine', 'Vector_Vault', 'ACL_Guard', 'Live_Status'] },
  { title: 'Governance', links: ['Sovereignty_Report', 'Data_Residency', 'Trust_Center', 'SOC2_Compliance'] }
]
</script>