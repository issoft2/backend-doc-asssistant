import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import Toast from 'primevue/toast'

import App from './App.vue'
import router from './router'

// import 'primevue/resources/themes/lara-dark-indigo/theme.css'
// or:
// import 'primevue/resources/themes/lara-light-indigo/theme.css'

import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'

const app = createApp(App)

app.use(router)
app.use(PrimeVue)
app.use(ToastService)              // 1) register the toast service

app.component('Toast', Toast)      // 2) register the Toast component globally

app.mount('#app')
