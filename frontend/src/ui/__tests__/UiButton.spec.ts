import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import UiButton from '../UiButton.vue'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div />' } },
    { path: '/app/deals/nouveau', component: { template: '<div />' } },
  ],
})

describe('UiButton', () => {
  it('renders slot content in a native button by default', () => {
    const wrapper = mount(UiButton, { slots: { default: 'Commencer' } })
    expect(wrapper.element.tagName).toBe('BUTTON')
    expect(wrapper.text()).toContain('Commencer')
    expect(wrapper.attributes('type')).toBe('button')
  })

  it('applies variant and size classes', () => {
    const wrapper = mount(UiButton, { props: { variant: 'ghost', size: 'lg' } })
    expect(wrapper.classes()).toContain('ui-btn--ghost')
    expect(wrapper.classes()).toContain('ui-btn--lg')
  })

  it('is disabled and shows a spinner while loading', () => {
    const wrapper = mount(UiButton, { props: { loading: true } })
    expect(wrapper.attributes('disabled')).toBeDefined()
    expect(wrapper.attributes('aria-busy')).toBe('true')
    expect(wrapper.find('.ui-btn__spinner').exists()).toBe(true)
  })

  it('renders an anchor when href is provided', () => {
    const wrapper = mount(UiButton, { props: { href: '#how' } })
    expect(wrapper.element.tagName).toBe('A')
    expect(wrapper.attributes('href')).toBe('#how')
    expect(wrapper.attributes('type')).toBeUndefined()
  })

  // Regression: QA found the dashboard "Créer un deal" CTA rendered <a> with no
  // href, because UiButton passed both `to` and an undefined `href` to
  // RouterLink. The router link must keep a real, navigable href.
  it('renders a navigable router-link when `to` is set', async () => {
    const wrapper = mount(UiButton, {
      props: { to: '/app/deals/nouveau' },
      global: { plugins: [router] },
    })
    await router.isReady()
    expect(wrapper.element.tagName).toBe('A')
    expect(wrapper.attributes('href')).toBe('/app/deals/nouveau')
    expect(wrapper.attributes('type')).toBeUndefined()
  })
})
