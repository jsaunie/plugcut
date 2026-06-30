import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import { useAuthStore } from './features/auth/store'
import { i18n } from './i18n'
import { router } from './router'
import { setAuthTokenGetter, setTokenRefresher } from './shared/http'
import './styles/base.css'

const pinia = createPinia()

// Let the HTTP client read/refresh tokens without importing the store (avoids a cycle).
setAuthTokenGetter(() => useAuthStore(pinia).accessToken)
setTokenRefresher(() => useAuthStore(pinia).tryRefresh())

createApp(App).use(pinia).use(router).use(i18n).mount('#app')
