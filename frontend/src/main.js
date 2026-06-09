import { createApp } from 'vue'
import App from './App.vue'
import router from './app/router.js'
import './styles/tokens.css'
import './styles/layout.css'
import './styles/components.css'

createApp(App).use(router).mount('#app')
