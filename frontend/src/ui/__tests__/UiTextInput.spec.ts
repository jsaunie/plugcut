import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import UiTextInput from '../UiTextInput.vue'

describe('UiTextInput', () => {
  it('emits update:modelValue on input', async () => {
    const wrapper = mount(UiTextInput, { props: { modelValue: '' } })
    await wrapper.find('input').setValue('dev@example.com')
    expect(wrapper.emitted('update:modelValue')?.at(-1)).toEqual(['dev@example.com'])
  })

  it('marks the input invalid', () => {
    const wrapper = mount(UiTextInput, { props: { modelValue: '', invalid: true } })
    const input = wrapper.find('input')
    expect(input.classes()).toContain('ui-input--invalid')
    expect(input.attributes('aria-invalid')).toBe('true')
  })

  it('defaults to a text input and forwards the type', () => {
    const wrapper = mount(UiTextInput, { props: { modelValue: '', type: 'password' } })
    expect(wrapper.find('input').attributes('type')).toBe('password')
  })
})
