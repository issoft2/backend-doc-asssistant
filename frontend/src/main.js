import { createApp } from 'vue'
import PrimeVue from 'primevue/config'

import Aura from '@primeuix/themes/aura'      // styled theme preset

import ToastService from 'primevue/toastservice'
import Toast from 'primevue/toast'

import App from './App.vue'
import router from './router'

import 'primeicons/primeicons.css'           // icons

const app = createApp(App)

app.use(router)

app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      cssLayer: false                         // keep false while using Tailwind
    }
  }
})

app.use(ToastService)
app.component('Toast', Toast)

app.mount('#app')
