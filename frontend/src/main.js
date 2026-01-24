import { createApp } from 'vue'
import PrimeVue from 'primevue/config'

// ✅ import a preset as default from its path
import Aura from '@primeuix/themes/aura'

import ToastService from 'primevue/toastservice'
import Toast from 'primevue/toast'

import App from './App.vue'
import router from './router'

import 'primeicons/primeicons.css'

const app = createApp(App)

app.use(router)

app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: 'system', // or '.dark' or remove if you don't use it
      cssLayer: false
    }
  }
})

app.use(ToastService)
app.component('Toast', Toast)

app.mount('#app')
