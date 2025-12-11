<template>
  <div class="min-h-screen bg-slate-950 text-slate-50 flex flex-col">
    <!-- Nav -->
    <header class="border-b border-slate-800">
      <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div
            class="h-8 w-8 rounded-lg bg-indigo-500/20 border border-indigo-400/40 flex items-center justify-center text-xs font-semibold text-indigo-200"
          >
            CG
          </div>
          <span class="text-sm font-semibold tracking-tight">Company Guideline Assistant</span>
        </div>
        <div class="flex items-center gap-3 text-xs">
          <RouterLink
            to="/login"
            class="px-3 py-1.5 rounded-lg border border-slate-700 hover:border-slate-500 hover:bg-slate-900/70 transition"
          >
            Sign in
          </RouterLink>
        </div>
      </div>
    </header>

    <!-- Hero -->
    <main class="flex-1">
      <section
        class="max-w-6xl mx-auto px-4 py-10 md:py-16 grid md:grid-cols-2 gap-10 items-center"
      >
        <!-- Left: copy -->
        <div class="space-y-5">
          <p
            class="inline-flex items-center gap-2 rounded-full border border-indigo-400/40 bg-indigo-500/10 px-3 py-1 text-[11px] font-medium text-indigo-100"
          >
            Multi‑tenant AI document assistant for modern organisations
          </p>

          <h1 class="text-3xl md:text-4xl font-semibold tracking-tight text-slate-50">
            Turn company documents into a private AI assistant.
          </h1>

          <p
            class="text-sm md:text-[15px] text-slate-300 leading-relaxed max-w-xl"
          >
            Company Guideline Assistant gives each company its own secure, tenant‑isolated AI that
            answers employee questions using your HR, compliance, and handbook documents —
            without mixing data between clients or hallucinating new policies.
          </p>

          <div class="flex flex-wrap gap-3 pt-1">
            <RouterLink
              to="/login"
              class="inline-flex items-center justify-center px-4 py-2.5 rounded-lg bg-indigo-500 text-xs font-medium text-white shadow-sm hover:bg-indigo-400 transition"
            >
              Get started – Sign in
            </RouterLink>
            <a
              href="#how-it-works"
              class="inline-flex items-center justify-center px-4 py-2.5 rounded-lg border border-slate-700 text-xs font-medium text-slate-200 hover:border-slate-500 hover:bg-slate-900/70 transition"
            >
              See how it works
            </a>
          </div>

          <div class="flex flex-wrap gap-4 pt-3 text-[11px] text-slate-400">
            <div class="flex items-center gap-1.5">
              <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
              <span>Built as a multi‑tenant SaaS: each company has its own isolated space</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
              <span>Role‑based access for vendor, HR, executives, managers, and employees</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
              <span>Answers grounded strictly in your uploaded policy documents</span>
            </div>
          </div>
        </div>

        <!-- Right: preview card -->
        <div class="relative">
          <div
            class="absolute -inset-6 bg-indigo-500/10 blur-3xl rounded-3xl pointer-events-none"
          ></div>
          <div
            class="relative rounded-2xl border border-slate-800 bg-slate-950/80 shadow-xl shadow-slate-950/60 overflow-hidden"
          >
            <div
              class="border-b border-slate-800 px-4 py-2.5 flex items-center justify-between"
            >
              <span class="text-xs font-medium text-slate-200">Employee policy chat</span>
              <span class="text-[11px] text-slate-500">Answers from your company only</span>
            </div>
            <div class="p-4 space-y-3 text-[11px] text-slate-200">
              <div class="space-y-1.5">
                <p class="font-medium text-slate-100">
                  “What’s our remote work allowance?”
                </p>
                <p class="text-slate-400">
                  “According to <span class='font-medium'>Trio‑Corp Remote Work Policy</span>,
                  full‑time employees can work remotely up to 3 days per week, subject to manager
                  approval and role eligibility…”
                </p>
              </div>
              <div
                class="rounded-lg border border-dashed border-slate-800 bg-slate-900/60 px-3 py-2 flex items-center justify-between"
              >
                <span class="text-slate-400">
                  HR and policy owners update documents from the admin panel — answers stay in sync
                  without any retraining.
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- How it works -->
      <section id="how-it-works" class="border-t border-slate-900 bg-slate-950">
        <div class="max-w-6xl mx-auto px-4 py-10 md:py-12 space-y-6">
          <h2 class="text-sm font-semibold text-slate-100">How it works</h2>
          <div class="grid md:grid-cols-3 gap-6 text-sm text-slate-300">
            <div class="space-y-2">
              <p class="text-xs font-semibold text-indigo-300">
                1. Onboard your company (or clients)
              </p>
              <p>
                Vendor and tenant admins provision companies, configure collections, and invite HR
                and policy owners — all from a simple web UI.
              </p>
            </div>
            <div class="space-y-2">
              <p class="text-xs font-semibold text-indigo-300">
                2. Upload policies and handbooks
              </p>
              <p>
                HR and admins ingest handbooks, HR policies, compliance docs, and procedures into
                secure, tenant‑isolated storage. Each tenant’s data is kept separate.
              </p>
            </div>
            <div class="space-y-2">
              <p class="text-xs font-semibold text-indigo-300">
                3. Employees ask questions in chat
              </p>
              <p>
                Employees log in and ask natural‑language questions. The assistant retrieves from
                that company’s documents only and cites the underlying sources.
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Footer CTA -->
    <footer class="border-t border-slate-900 bg-slate-950">
      <div
        class="max-w-6xl mx-auto px-4 py-6 flex flex-col md:flex-row items-center justify-between gap-3 text-[11px] text-slate-400"
      >
        <p>
          Built for HR, People Ops, and policy owners who need a secure, multi‑tenant AI assistant —
          instead of another inbox full of “Where is the policy?” questions.
        </p>
        <RouterLink
          to="/login"
          class="inline-flex items-center justify-center px-3 py-2 rounded-lg bg-indigo-500 text-xs font-medium text-white hover:bg-indigo-400 transition"
        >
          Open the app
        </RouterLink>
      </div>
    </footer>
  </div>
</template>
