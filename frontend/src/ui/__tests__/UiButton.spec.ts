import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import UiButton from '../UiButton.vue'

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
})
