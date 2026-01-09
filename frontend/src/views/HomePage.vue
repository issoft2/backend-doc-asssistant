<template>
  <div class="min-h-screen bg-slate-950 text-slate-50 flex flex-col">
    <!-- Nav -->
    <header class="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur">
      <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div
            class="h-8 w-8 rounded-lg bg-indigo-500/20 border border-indigo-400/40 flex items-center justify-center text-xs font-semibold text-indigo-200"
          >
            CG
          </div>
          <div class="flex flex-col">
            <span class="text-sm font-semibold tracking-tight">Company Guideline Assistant</span>
            <span class="text-[11px] text-slate-400">
              Your private AI for HR, policies, and internal documents
            </span>
          </div>
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
            Multi‑tenant AI assistant for modern organisations
            <span class="h-1 w-1 rounded-full bg-emerald-400 animate-pulse" />
            <span class="text-[10px] text-emerald-200/80">Data stays in your company</span>
          </p>

          <h1 class="text-3xl md:text-4xl font-semibold tracking-tight text-slate-50">
            Turn your company documents into a private, searchable AI helpdesk.
          </h1>

          <p class="text-sm md:text-[15px] text-slate-300 leading-relaxed max-w-xl">
            Company Guideline Assistant gives every tenant its own secure AI that answers employee
            questions using HR policies, handbooks, procedures, and reports — without mixing data
            between clients or inventing new rules.
          </p>

          <!-- Primary actions -->
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

          <!-- Key benefits / capabilities -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4 text-[11px] text-slate-300">
            <div class="flex items-start gap-2">
              <span class="mt-1 h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
              <div>
                <p class="font-semibold text-slate-100">Multi‑tenant by design</p>
                <p class="text-slate-400">
                  Each company has its own isolated workspace, indexes, and conversations.
                </p>
              </div>
            </div>
            <div class="flex items-start gap-2">
              <span class="mt-1 h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
              <div>
                <p class="font-semibold text-slate-100">Role‑aware answers</p>
                <p class="text-slate-400">
                  Tailor access for vendors, HR, executives, managers, and employees.
                </p>
              </div>
            </div>
            <div class="flex items-start gap-2">
              <span class="mt-1 h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
              <div>
                <p class="font-semibold text-slate-100">Grounded in your docs</p>
                <p class="text-slate-400">
                  Answers come from your uploaded policies and reports, with sources.
                </p>
              </div>
            </div>
          </div>

          <!-- Example questions strip -->
          <div class="pt-3">
            <p class="text-[11px] font-semibold text-slate-400 mb-1">
              Ask questions like:
            </p>
            <div class="flex flex-wrap gap-2 text-[11px]">
              <span class="px-2.5 py-1 rounded-full bg-slate-900/80 border border-slate-700/60 text-slate-300">
                “What is our travel reimbursement policy?”
              </span>
              <span class="px-2.5 py-1 rounded-full bg-slate-900/80 border border-slate-700/60 text-slate-300">
                “Summarise the 2022 financial report by quarter.”
              </span>
              <span class="px-2.5 py-1 rounded-full bg-slate-900/80 border border-slate-700/60 text-slate-300">
                “Who approves remote work and how many days are allowed?”
              </span>
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
            <div class="p-4 space-y-4 text-[11px] text-slate-200">
              <div class="space-y-1.5">
                <p class="font-medium text-slate-100">
                  “What’s our remote work allowance?”
                </p>
                <p class="text-slate-400 leading-relaxed">
                  “According to
                  <span class="font-medium">Remote Work Policy – Trio‑Corp</span>, full‑time
                  employees can work remotely up to 3 days per week, subject to manager approval
                  and role eligibility. Equipment and security requirements are listed in section
                  4.2…”
                </p>
              </div>

              <div class="space-y-2">
                <p class="text-[10px] uppercase tracking-wide text-slate-500 font-semibold">
                  Why teams use Company Guideline Assistant
                </p>
                <ul class="space-y-1.5 text-slate-400">
                  <li class="flex items-start gap-1.5">
                    <span class="mt-1 h-1 w-1 rounded-full bg-indigo-400"></span>
                    <span>Deflect repetitive “Where is the policy?” questions from HR inboxes.</span>
                  </li>
                  <li class="flex items-start gap-1.5">
                    <span class="mt-1 h-1 w-1 rounded-full bg-indigo-400"></span>
                    <span>Ensure employees always see the latest version of your documents.</span>
                  </li>
                  <li class="flex items-start gap-1.5">
                    <span class="mt-1 h-1 w-1 rounded-full bg-indigo-400"></span>
                    <span>Keep every tenant’s data separate for consultants and multi‑client vendors.</span>
                  </li>
                </ul>
              </div>

              <div
                class="rounded-lg border border-dashed border-slate-800 bg-slate-900/60 px-3 py-2 text-[11px] text-slate-400"
              >
                HR and policy owners update documents from the admin panel — answers stay in sync
                without retraining or redeploying models.
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- How it works -->
      <section id="how-it-works" class="border-t border-slate-900 bg-slate-950">
        <div class="max-w-6xl mx-auto px-4 py-10 md:py-12 space-y-6">
          <div class="flex items-center justify-between gap-2">
            <h2 class="text-sm font-semibold text-slate-100">How it works</h2>
            <p class="text-[11px] text-slate-400">
              Designed for consultancies, multi‑brand groups, and internal HR teams.
            </p>
          </div>

          <div class="grid md:grid-cols-3 gap-6 text-sm text-slate-300">
            <div class="space-y-2">
              <p class="text-xs font-semibold text-indigo-300 uppercase tracking-wide">
                1. Onboard your company or clients
              </p>
              <p>
                Vendor and tenant admins provision companies, configure collections, and invite HR,
                Legal, and policy owners — all from a simple web UI.
              </p>
            </div>
            <div class="space-y-2">
              <p class="text-xs font-semibold text-indigo-300 uppercase tracking-wide">
                2. Connect and upload documents
              </p>
              <p>
                Ingest handbooks, HR policies, compliance docs, procedures, and reports into secure,
                tenant‑scoped storage. Each tenant’s embeddings and chat history are isolated.
              </p>
            </div>
            <div class="space-y-2">
              <p class="text-xs font-semibold text-indigo-300 uppercase tracking-wide">
                3. Employees ask questions in chat
              </p>
              <p>
                Employees log in with their role, ask natural‑language questions, and get grounded
                answers with citations to the underlying documents — not generic AI responses.
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
        <p class="max-w-xl">
          Built for HR, People Ops, Legal, and policy owners who need a secure, multi‑tenant AI
          assistant — instead of another inbox full of “Where is the policy?” questions.
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
