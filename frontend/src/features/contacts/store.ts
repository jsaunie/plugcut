import { defineStore } from 'pinia'

import * as api from './api'
import type { Contact, ContactInput } from './types'

interface ContactsState {
  contacts: Contact[]
  loading: boolean
  loaded: boolean
}

export const useContactsStore = defineStore('contacts', {
  state: (): ContactsState => ({
    contacts: [],
    loading: false,
    loaded: false,
  }),
  actions: {
    async fetchAll(): Promise<void> {
      this.loading = true
      try {
        this.contacts = await api.listContacts()
        this.loaded = true
      } finally {
        this.loading = false
      }
    },

    async create(input: ContactInput): Promise<Contact> {
      const contact = await api.createContact(input)
      this.contacts = [...this.contacts, contact].sort((a, b) =>
        a.full_name.localeCompare(b.full_name),
      )
      return contact
    },

    async update(id: string, input: ContactInput): Promise<Contact> {
      const contact = await api.updateContact(id, input)
      this.contacts = this.contacts.map((c) => (c.id === id ? contact : c))
      return contact
    },

    async remove(id: string): Promise<void> {
      await api.deleteContact(id)
      this.contacts = this.contacts.filter((c) => c.id !== id)
    },
  },
})
