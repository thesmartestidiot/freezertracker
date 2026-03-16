import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')

if (import.meta.env.PROD) {
  console.log(
    '%c~ Freezer Tracker ~',
    'font-family: Georgia, serif; font-size: 16px; font-style: italic; color: #C4654A; padding: 8px 0;',
  )
  console.log(
    '%cKeeping kitchens organized, one frozen chicken breast at a time.',
    'font-family: system-ui; font-size: 11px; color: #7A7062; padding-bottom: 4px;',
  )
}
