import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import * as api from '../api'
import { useContactsStore } from '../store'
import type { Contact, ContactInput } from '../types'

vi.mock('../api', () => ({
  listContacts: vi.fn(),
  getContact: vi.fn(),
  createContact: vi.fn(),
  updateContact: vi.fn(),
  deleteContact: vi.fn(),
}))

const mockedApi = vi.mocked(api)

function makeContact(id: string, name = 'Marie'): Contact {
  return {
    id,
    full_name: name,
    kind: 'person',
    headline: '',
    email: null,
    phone: null,
    linkedin_url: null,
    company: null,
    location: null,
    tags: [],
    notes: '',
    source: 'manual',
    created_at: '',
    updated_at: '',
  }
}

const input: ContactInput = {
  full_name: 'Anna',
  kind: 'person',
  headline: '',
  email: null,
  phone: null,
  linkedin_url: null,
  company: null,
  location: null,
  tags: [],
  notes: '',
}

describe('contacts store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('loads contacts', async () => {
    mockedApi.listContacts.mockResolvedValue([makeContact('1')])
    const store = useContactsStore()
    await store.fetchAll()
    expect(store.contacts).toHaveLength(1)
    expect(store.loaded).toBe(true)
  })

  it('creates and keeps the list sorted by name', async () => {
    mockedApi.createContact.mockResolvedValue(makeContact('2', 'Anna'))
    const store = useContactsStore()
    store.contacts = [makeContact('1', 'Zoe')]
    await store.create(input)
    expect(store.contacts[0].full_name).toBe('Anna')
  })

  it('removes a contact', async () => {
    mockedApi.deleteContact.mockResolvedValue(undefined)
    const store = useContactsStore()
    store.contacts = [makeContact('1'), makeContact('2')]
    await store.remove('1')
    expect(store.contacts.map((c) => c.id)).toEqual(['2'])
  })
})
