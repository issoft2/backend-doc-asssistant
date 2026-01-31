<template>
  <section class="relative isolate overflow-hidden bg-slate-50 py-24 sm:py-32">
    <div class="absolute inset-0 -z-10 h-full w-full bg-[linear-gradient(to_right,#e2e8f0_1px,transparent_1px),linear-gradient(to_bottom,#e2e8f0_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>

    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <div class="mx-auto max-w-2xl lg:mx-0 lg:flex lg:max-w-none lg:items-center lg:gap-x-16">
        
        <div class="w-full lg:max-w-xl lg:flex-auto">
          <div class="mb-8 flex">
            <div class="relative rounded-full px-3 py-1 text-sm leading-6 text-slate-600 ring-1 ring-slate-200 hover:ring-slate-300 bg-white">
              <span class="font-semibold text-indigo-600">Secure Update:</span> Logical Isolation Verified 
            </div>
          </div>
          
          <h1 class="text-4xl font-bold tracking-tight text-slate-900 sm:text-6xl leading-[1.1]">
            Enterprise-Grade <span class="text-indigo-600">Knowledge Intelligence.</span>
          </h1>
          
          <p class="mt-6 text-lg leading-8 text-slate-600">
            A multi-tenant AI layer built for regulated environments. 
            <strong>Stop Digging. Start Asking.</strong> [cite: 4, 6] 
            Get grounded, role-aware answers exclusively from your internal documents[cite: 7, 10].
          </p>

          <div class="mt-10 flex items-center gap-x-6">
            <button class="bg-slate-900 text-white px-6 py-3 rounded-sm font-semibold shadow-lg hover:bg-slate-800 transition-all">
              Deploy Knowledge Layer
            </button>
            <a href="#how-it-works" class="text-sm font-bold leading-6 text-slate-900">
              Review Security Specs <span aria-hidden="true">→</span>
            </a>
          </div>
        </div>

        <div class="mt-16 sm:mt-24 lg:mt-0 lg:flex-shrink-0 lg:flex-grow">
          <div class="relative rounded-xl bg-slate-900 p-2 shadow-2xl ring-1 ring-slate-700">
            <div class="rounded-lg bg-slate-950 p-6 font-mono text-xs text-slate-300 space-y-4">
              <div class="flex items-center justify-between border-b border-slate-800 pb-2">
                <span class="text-emerald-400">● SYSTEM_ACTIVE</span>
                <span class="text-slate-500">TENANT_ID: {{ active_tenant }}</span>
              </div>
              <div class="space-y-2">
                <p class="text-indigo-400">> QUERY: "Analyze subsidiary Q3 overhead"</p>
                <p class="text-slate-500">> ENFORCING ACL: User[FINANCE_LEAD] → Org[SUBSIDIARY_A]</p>
                <p class="text-emerald-500">> ACCESS GRANTED: 12 Documents Found [cite: 103]</p>
                <div class="pl-4 border-l border-slate-800 italic text-slate-400">
                  "Based on document 'A-2026-Report.pdf', overhead has decreased by 12%..." 
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>