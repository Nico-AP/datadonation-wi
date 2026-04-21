import { createApp } from 'vue'
import UApp from './CustomUploaderApp.vue'
import { createI18n } from 'vue-i18n'

const i18n = new createI18n({
    fallbackLocale: 'en',
})

const selectors = ["#customuapp", "#uapp"];
const mountEl = selectors.map(selector => document.querySelector(selector)).find(Boolean);

if (!mountEl) {
    // This bundle can be loaded on pages without uploader mount element.
    // Exit quietly instead of breaking unrelated pages (e.g., briefing).
    console.debug('Uploader mount element not found; skipping initialization.');
} else {
    const app = createApp(UApp, {...mountEl.dataset})

    app.use(i18n)
    app.mount(mountEl)
}
