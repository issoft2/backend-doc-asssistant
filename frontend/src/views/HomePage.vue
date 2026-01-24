<template>
  <div class="min-h-screen bg-slate-950 text-slate-50 flex flex-col">
    <!-- Toast for contact feedback -->
    <Toast />

    <!-- Nav -->
    <header class="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur">
      <div class="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div
            class="h-8 w-8 rounded-lg bg-indigo-500/20 border border-indigo-400/40 flex items-center justify-center text-xs font-semibold text-indigo-200"
          >
            CG
          </div>
          <div class="flex flex-col">
            <span class="text-sm font-semibold tracking-tight">
              Company Guideline Assistant
            </span>
            <span class="text-[11px] text-slate-400">
              A private AI layer over your policies, knowledge, and financial data
            </span>
          </div>
        </div>

        <div class="flex items-center gap-3 text-xs">
          <RouterLink to="/login">
            <Button
              label="Sign in"
              size="small"
              outlined
              class="!border-slate-700 !text-slate-100 hover:!border-slate-500 hover:!bg-slate-900/70"
            />
          </RouterLink>
        </div>
      </div>
    </header>

    <!-- Main -->
    <main class="flex-1">
      <!-- Hero -->
      <section
        class="max-w-6xl mx-auto px-4 py-10 md:py-16 grid md:grid-cols-2 gap-10 items-center"
      >
        <!-- Left: copy -->
        <div class="space-y-5">
          <div class="inline-flex items-center gap-2">
            <Tag
              severity="info"
              class="!bg-indigo-500/10 !border !border-indigo-400/40 !text-indigo-100 !text-[11px]"
              value="Multi‑tenant AI copilot for modern organizations"
            />
            <span class="h-1 w-1 rounded-full bg-emerald-400 animate-pulse" />
            <span class="text-[10px] text-emerald-200/80">
              Your content. Your rules. Your data.
            </span>
          </div>

          <h1 class="text-3xl md:text-4xl font-semibold tracking-tight text-slate-50">
            Stop digging folders. Ask for answers.
          </h1>

          <p class="text-sm md:text-[15px] text-slate-300 leading-relaxed max-w-xl">
            Upload policies, playbooks, reports, and spreadsheets. Your Assistant
            becomes a private AI help‑desk that answers questions, explains procedures, and turns
            financial tables into clear comparisons and charts — without leaking data or inventing
            new rules.
          </p>

          <!-- Primary actions -->
          <div class="flex flex-wrap gap-3 pt-1">
            <RouterLink to="/login">
              <Button
                label="Try it with your documents"
                size="small"
                class="!bg-indigo-500 !border-none !text-white hover:!bg-indigo-400 shadow-sm"
              />
            </RouterLink>

            <Button
              label="See how it works"
              size="small"
              outlined
              class="!border-slate-700 !text-slate-200 hover:!border-slate-500 hover:!bg-slate-900/70"
              @click="scrollToHow"
            />
          </div>

          <!-- Key benefits / capabilities -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4 text-[11px] text-slate-300">
            <Card
              v-for="benefit in benefits"
              :key="benefit.title"
              class="!bg-slate-950/60 !border-slate-800/80"
            >
              <template #title>
                <span class="flex items-center gap-2 text-slate-100 text-xs">
                  <span class="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  {{ benefit.title }}
                </span>
              </template>
              <template #content>
                <p class="text-[11px] text-slate-400">{{ benefit.body }}</p>
              </template>
            </Card>
          </div>

          <!-- Example questions strip -->
          <div class="pt-3 space-y-1">
            <p class="text-[11px] font-semibold text-slate-400">
              Ask in plain language:
            </p>
            <div class="flex flex-wrap gap-2 text-[11px]">
              <Chip
                v-for="q in exampleQuestions"
                :key="q"
                :label="q"
                class="!bg-slate-900/80 !border !border-slate-700/60 !text-slate-300"
              />
            </div>
          </div>
        </div>

        <!-- Right: stacked previews – finance + policy -->
        <div class="relative space-y-4">
          <div class="absolute -inset-6 bg-indigo-500/10 blur-3xl rounded-3xl pointer-events-none"></div>

          <!-- Finance / charts card -->
          <Card
            class="relative rounded-2xl !border-slate-800 !bg-slate-950/80 shadow-xl shadow-slate-950/60 overflow-hidden"
          >
            <template #header>
              <div class="border-b border-slate-800 px-4 py-2.5 flex items-center justify-between">
                <span class="text-xs font-medium text-slate-200">
                  Financial performance analysis
                </span>
                <span class="text-[11px] text-slate-500">
                  Tables and charts from your reports
                </span>
              </div>
            </template>

            <template #content>
              <div class="p-4 space-y-3 text-[11px] text-slate-200">
                <div class="space-y-1.5">
                  <p class="font-medium text-slate-100">
                    “Generate financial performance tables and charts for Q1 2023 and 2024.”
                  </p>
                  <p class="text-slate-400 leading-relaxed">
                    The assistant reads your quarterly statements, builds revenue, total‑expense, and
                    net‑profit tables, then renders comparison charts so leaders see trends in seconds
                    instead of digging through spreadsheets.
                  </p>
                </div>

                <div class="space-y-2">
                  <p class="text-[10px] uppercase tracking-wide text-slate-500 font-semibold">
                    What your managers see
                  </p>

                  <div class="grid grid-cols-1 gap-3">
                    <div
                      class="relative rounded-lg border border-indigo-500/40 bg-slate-900 overflow-hidden shadow-lg"
                    >
                      <img
                        src="/assets/bar.png"
                        alt="Revenue and expenses comparison charts Q1 2023 vs Q1 2024"
                        class="w-full h-32 md:h-36 object-cover"
                      />
                      <div
                        class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-slate-950/90 to-transparent px-3 pb-2 pt-6 text-[10px]"
                      >
                        <p class="text-slate-100 font-semibold">
                          Revenue & expenses comparison · Q1 2023 vs Q1 2024
                        </p>
                        <p class="text-slate-400">
                          Grouped bars call out shifts in spend and growth at a glance.
                        </p>
                      </div>
                    </div>

                    <div
                      class="relative rounded-lg border border-indigo-500/40 bg-slate-900 overflow-hidden shadow-lg"
                    >
                      <img
                        src="/assets/line.png"
                        alt="Financial performance line chart Q1 2023 vs Q1 2024"
                        class="w-full h-32 md:h-36 object-cover"
                      />
                      <div
                        class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-slate-950/90 to-transparent px-3 pb-2 pt-6 text-[10px]"
                      >
                        <p class="text-slate-100 font-semibold">
                          Financial performance line chart
                        </p>
                        <p class="text-slate-400">
                          Follow revenue, expenses, and net profit month by month.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <Message
                  severity="secondary"
                  class="!bg-slate-900/60 !border-slate-800 !text-slate-400 !text-[11px]"
                >
                  The same engine powers HR answers and financial insights — one assistant, grounded
                  entirely in your internal content.
                </Message>
              </div>
            </template>
          </Card>

          <!-- Policy / knowledge card -->
          <Card
            class="relative rounded-2xl !border-slate-800 !bg-slate-950/90 shadow-lg shadow-slate-950/50 overflow-hidden"
          >
            <template #header>
              <div class="border-b border-slate-800 px-4 py-2.5 flex items-center justify-between">
                <span class="text-xs font-medium text-slate-200">Employee policy chat</span>
                <span class="text-[11px] text-slate-500">Answers from your company only</span>
              </div>
            </template>
            <template #content>
              <div class="p-4 space-y-3 text-[11px] text-slate-200">
                <div class="space-y-1.5">
                  <p class="font-medium text-slate-100">
                    “What’s our remote work allowance?”
                  </p>
                  <p class="text-slate-400 leading-relaxed">
                    “According to your latest <span class='font-medium'>Remote Work Policy</span>,
                    full‑time employees can work remotely up to 3 days per week, subject to manager
                    approval and role eligibility. Security and equipment requirements are listed in
                    section 4.2…”
                  </p>
                </div>
                <Message
                  severity="secondary"
                  class="!bg-slate-900/60 !border-slate-800 !text-slate-400 !text-[11px]"
                >
                  Update a PDF once in the admin panel and every answer reflects the new version — no
                  retraining or redeploys.
                </Message>
              </div>
            </template>
          </Card>
        </div>
      </section>

      <!-- How it works -->
      <section id="how-it-works" class="border-t border-slate-900 bg-slate-950">
        <div class="max-w-6xl mx-auto px-4 py-10 md:py-12 space-y-6">
          <div class="flex items-center justify-between gap-2">
            <h2 class="text-sm font-semibold text-slate-100">How it works</h2>
            <p class="text-[11px] text-slate-400 max-w-md">
              Built for consultancies, multi‑brand groups, and internal enablement teams who need AI
              that respects tenant boundaries.
            </p>
          </div>

          <div class="grid md:grid-cols-3 gap-4 text-sm text-slate-300">
            <Card
              v-for="step in steps"
              :key="step.title"
              class="!bg-slate-950/60 !border-slate-800/80"
            >
              <template #title>
                <p class="text-xs font-semibold text-indigo-300 uppercase tracking-wide">
                  {{ step.title }}
                </p>
              </template>
              <template #content>
                <p class="text-[11px] text-slate-300">
                  {{ step.body }}
                </p>
              </template>
            </Card>
          </div>
        </div>
      </section>

      <!-- Contact us -->
      <section id="contact" class="border-t border-slate-900 bg-slate-950">
        <div class="max-w-6xl mx-auto px-4 py-10 md:py-12 grid md:grid-cols-2 gap-8">
          <div class="space-y-3">
            <h2 class="text-sm font-semibold text-slate-100">Contact us</h2>
            <p class="text-[11px] text-slate-400 max-w-sm">
              Share a bit about your use case and we’ll get back to you by email.
              No sales blast, just a focused response.
            </p>
            <ul class="text-[11px] text-slate-400 space-y-1">
              <li>• Product questions or roadmap input</li>
              <li>• Pricing and multi‑tenant deployments</li>
              <li>• Support or technical issues</li>
            </ul>
          </div>

          <Card class="!bg-slate-950/80 !border-slate-800/80">
            <template #content>
              <form class="space-y-3 text-[11px]" @submit.prevent="submitContact">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label class="block mb-1 text-slate-300">Name</label>
                    <InputText
                      v-model="contactForm.name"
                      type="text"
                      required
                      class="w-full text-[11px]"
                    />
                  </div>
                  <div>
                    <label class="block mb-1 text-slate-300">Email</label>
                    <InputText
                      v-model="contactForm.email"
                      type="email"
                      required
                      class="w-full text-[11px]"
                    />
                  </div>
                </div>

                <div>
                  <label class="block mb-1 text-slate-300">Topic</label>
                  <Dropdown
                    v-model="contactForm.category"
                    :options="categories"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Select a topic"
                    class="w-full text-[11px]"
                  />
                </div>

                <div>
                  <label class="block mb-1 text-slate-300">Message</label>
                  <Textarea
                    v-model="contactForm.message"
                    rows="4"
                    autoResize
                    required
                    class="w-full text-[11px]"
                    placeholder="Tell us briefly what you’re trying to do…"
                  />
                </div>

                <div class="flex items-center justify-between">
                  <p class="text-[10px] text-slate-500">
                    We’ll reply directly to your email. No marketing list.
                  </p>
                  <Button
                    type="submit"
                    :label="contactSubmitting ? 'Sending…' : 'Send message'"
                    size="small"
                    :loading="contactSubmitting"
                  />
                </div>

                <Message
                  v-if="contactSuccess"
                  severity="success"
                  class="!text-[11px]"
                >
                  Thank you — your message has been sent.
                </Message>
                <Message
                  v-if="contactError"
                  severity="error"
                  class="!text-[11px]"
                >
                  {{ contactError }}
                </Message>
              </form>
            </template>
          </Card>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-900 bg-slate-950">
      <div
        class="max-w-6xl mx-auto px-4 py-6 flex flex-col md:flex-row items-center justify-between gap-3 text-[11px] text-slate-400"
      >
        <p class="max-w-xl">
          Stop forwarding PDFs and answering the same questions twice. Give every tenant a secure AI
          assistant that knows their policies and numbers — and can explain both.
        </p>
        <RouterLink to="/login">
          <Button
            label="Open the app"
            size="small"
            class="!bg-indigo-500 !border-none !text-white hover:!bg-indigo-400"
          />
        </RouterLink>
      </div>

      <div class="border-t border-slate-900/80">
        <div
          class="max-w-6xl mx-auto px-4 py-3 flex flex-col md:flex-row items-center justify-between gap-2 text-[10px] text-slate-500"
        >
          <span>
            © {{ year }} Company Guideline Assistant. All rights reserved.
          </span>
          <span>
            Built for organisations that care about privacy and clear answers.
          </span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import { sendContact } from '../api'

const toast = useToast()
const year = new Date().getFullYear()

const benefits = [
  {
    title: 'Multi‑tenant by design',
    body:
      'Serve multiple clients or business units from one stack while keeping workspaces, ' +
      'indexes, and chat history fully isolated.'
  },
  {
    title: 'Role‑aware answers',
    body:
      'Shape responses for HR, managers, execs, vendors, or employees based on their ' +
      'access and responsibilities.'
  },
  {
    title: 'Data & financial analysis',
    body:
      'Ask for quarterly revenue, expenses, and net‑profit tables and get side‑by‑side ' +
      'comparisons with charts straight from your reports.'
  }
]

const exampleQuestions = [
  '“What is our travel reimbursement policy and who signs off?”',
  '“Compare Q1 2023 vs Q1 2024 financial performance with charts.”',
  '“Summarise the onboarding handbook for new employees.”'
]

const steps = [
  {
    title: '1. Onboard tenants in minutes',
    body:
      'Vendor and tenant admins create workspaces, configure collections, and invite HR, ' +
      'finance, Legal, and content owners from a simple web UI.'
  },
  {
    title: '2. Connect and upload knowledge',
    body:
      'Ingest handbooks, SOPs, contracts, wikis, and financial reports into secure, ' +
      'tenant‑scoped storage. Embeddings and chat history never cross tenants.'
  },
  {
    title: '3. Ask questions, get grounded answers',
    body:
      'Employees get clear, cited answers to policy questions. Managers get live‑from‑your‑' +
      'data tables and charts — not generic internet AI.'
  }
]

const categories = [
  { label: 'Product question', value: 'product' },
  { label: 'Pricing / billing', value: 'pricing' },
  { label: 'Deployment / multi‑tenant setup', value: 'deployment' },
  { label: 'Support / bug report', value: 'support' },
  { label: 'Other', value: 'other' }
]

const contactForm = ref({
  name: '',
  email: '',
  category: '',
  message: ''
})

const contactSubmitting = ref(false)
const contactSuccess = ref(false)
const contactError = ref('')

function resetContactForm() {
  contactForm.value = { name: '', email: '', category: '', message: '' }
}

async function submitContact() {
  contactSubmitting.value = true
  contactSuccess.value = false
  contactError.value = ''

  try {
    await sendContact(contactForm.value)
    contactSuccess.value = true
    toast.add({
      severity: 'success',
      summary: 'Message sent',
      detail: 'We’ll get back to you by email.',
      life: 4000
    })
    resetContactForm()
  } catch (e) {
    const msg =
      e?.response?.data?.detail ||
      'Failed to send message, please try again.'
    contactError.value = msg
    toast.add({
      severity: 'error',
      summary: 'Failed to send',
      detail: msg,
      life: 5000
    })
  } finally {
    contactSubmitting.value = false
  }
}

function scrollToHow() {
  const el = document.getElementById('how-it-works')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}
</script>
