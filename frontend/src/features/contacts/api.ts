import { apiFetch } from '@/shared/http'

import type { Contact, ContactInput } from './types'

export function listContacts(): Promise<Contact[]> {
  return apiFetch<Contact[]>('/contacts')
}

export function getContact(id: string): Promise<Contact> {
  return apiFetch<Contact>(`/contacts/${id}`)
}

export function createContact(input: ContactInput): Promise<Contact> {
  return apiFetch<Contact>('/contacts', { method: 'POST', body: JSON.stringify(input) })
}

export function updateContact(id: string, input: ContactInput): Promise<Contact> {
  return apiFetch<Contact>(`/contacts/${id}`, { method: 'PUT', body: JSON.stringify(input) })
}

export function deleteContact(id: string): Promise<void> {
  return apiFetch<void>(`/contacts/${id}`, { method: 'DELETE' })
}
