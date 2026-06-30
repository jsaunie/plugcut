<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import AppShell from '@/features/app/AppShell.vue'
import { getContact } from '@/features/contacts/api'
import { useContactsStore } from '@/features/contacts/store'
import type { Contact, ContactInput, ContactKind } from '@/features/contacts/types'
import { nameError, parseTags } from '@/features/contacts/validation'
import { ApiError } from '@/shared/http'
import { UiButton, UiField, UiTextarea, UiTextInput } from '@/ui'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const store = useContactsStore()

const id = computed(() => (route.params.id as string | undefined) ?? null)
const isEdit = computed(() => Boolean(id.value))

const form = reactive({
  full_name: '',
  kind: 'person' as ContactKind,
  headline: '',
  company: '',
  email: '',
  phone: '',
  linkedin_url: '',
  location: '',
  tagsRaw: '',
  notes: '',
})
const nameErr = ref('')
const formError = ref('')
const saving = ref(false)

function fill(contact: Contact): void {
  form.full_name = contact.full_name
  form.kind = contact.kind
  form.headline = contact.headline
  form.company = contact.company ?? ''
  form.email = contact.email ?? ''
  form.phone = contact.phone ?? ''
  form.linkedin_url = contact.linkedin_url ?? ''
  form.location = contact.location ?? ''
  form.tagsRaw = contact.tags.join(', ')
  form.notes = contact.notes
}

onMounted(async () => {
  if (!isEdit.value) return
  const existing = store.contacts.find((c) => c.id === id.value)
  if (existing) {
    fill(existing)
    return
  }
  try {
    fill(await getContact(id.value as string))
  } catch (err) {
    formError.value = err instanceof ApiError ? err.message : t('contacts.errors.generic')
  }
})

function trimOrNull(value: string): string | null {
  return value.trim() ? value.trim() : null
}

function buildInput(): ContactInput {
  return {
    full_name: form.full_name.trim(),
    kind: form.kind,
    headline: form.headline.trim(),
    company: trimOrNull(form.company),
    email: trimOrNull(form.email),
    phone: trimOrNull(form.phone),
    linkedin_url: trimOrNull(form.linkedin_url),
    location: trimOrNull(form.location),
    tags: parseTags(form.tagsRaw),
    notes: form.notes,
  }
}

async function submit(): Promise<void> {
  formError.value = ''
  const key = nameError(form.full_name)
  nameErr.value = key ? t(key) : ''
  if (key) return
  saving.value = true
  try {
    if (isEdit.value) await store.update(id.value as string, buildInput())
    else await store.create(buildInput())
    await router.push('/app/contacts')
  } catch (err) {
    formError.value = err instanceof ApiError ? err.message : t('contacts.errors.generic')
  } finally {
    saving.value = false
  }
}

async function remove(): Promise<void> {
  if (!id.value) return
  saving.value = true
  try {
    await store.remove(id.value)
    await router.push('/app/contacts')
  } catch (err) {
    formError.value = err instanceof ApiError ? err.message : t('contacts.errors.generic')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <AppShell>
    <RouterLink to="/app/contacts" class="back">← {{ t('contacts.title') }}</RouterLink>
    <h1 class="title">{{ isEdit ? t('contacts.form.editTitle') : t('contacts.form.newTitle') }}</h1>

    <form class="form" novalidate @submit.prevent="submit">
      <div class="kind">
        <button
          v-for="option in (['person', 'company'] as const)"
          :key="option"
          type="button"
          class="kind__btn"
          :class="{ 'kind__btn--active': form.kind === option }"
          @click="form.kind = option"
        >
          {{ t(`contacts.kind.${option}`) }}
        </button>
      </div>

      <UiField :label="t('contacts.form.fullName')" for-id="name" :error="nameErr || undefined">
        <UiTextInput id="name" v-model="form.full_name" :invalid="Boolean(nameErr)" />
      </UiField>

      <UiField :label="t('contacts.form.headline')" for-id="headline">
        <UiTextInput
          id="headline"
          v-model="form.headline"
          :placeholder="t('contacts.form.headlinePlaceholder')"
        />
      </UiField>

      <div class="grid">
        <UiField :label="t('contacts.form.company')" for-id="company">
          <UiTextInput id="company" v-model="form.company" />
        </UiField>
        <UiField :label="t('contacts.form.location')" for-id="location">
          <UiTextInput id="location" v-model="form.location" />
        </UiField>
        <UiField :label="t('contacts.form.email')" for-id="email">
          <UiTextInput id="email" v-model="form.email" type="email" />
        </UiField>
        <UiField :label="t('contacts.form.phone')" for-id="phone">
          <UiTextInput id="phone" v-model="form.phone" />
        </UiField>
      </div>

      <UiField :label="t('contacts.form.linkedin')" for-id="linkedin">
        <UiTextInput
          id="linkedin"
          v-model="form.linkedin_url"
          placeholder="https://linkedin.com/in/..."
        />
      </UiField>

      <UiField :label="t('contacts.form.tags')" for-id="tags">
        <UiTextInput
          id="tags"
          v-model="form.tagsRaw"
          :placeholder="t('contacts.form.tagsPlaceholder')"
        />
      </UiField>

      <UiField :label="t('contacts.form.notes')" for-id="notes">
        <UiTextarea id="notes" v-model="form.notes" :rows="5" />
      </UiField>

      <p v-if="formError" class="form__error" role="alert">{{ formError }}</p>

      <div class="actions">
        <UiButton type="submit" size="lg" :loading="saving">{{ t('contacts.form.save') }}</UiButton>
        <UiButton to="/app/contacts" variant="ghost" size="lg">{{ t('common.cancel') }}</UiButton>
        <button v-if="isEdit" type="button" class="delete" :disabled="saving" @click="remove">
          {{ t('contacts.form.delete') }}
        </button>
      </div>
    </form>
  </AppShell>
</template>

<style scoped>
.back {
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
.back:hover {
  color: var(--accent);
}
.title {
  margin: 1rem 0 2rem;
  font-size: var(--fs-display-md);
}
.form {
  display: grid;
  gap: 1.2rem;
  max-width: 640px;
}
.kind {
  display: inline-flex;
  gap: 0.3rem;
  padding: 0.25rem;
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius-pill);
  width: fit-content;
}
.kind__btn {
  padding: 0.45rem 1rem;
  border-radius: var(--radius-pill);
  font-size: 0.9rem;
  color: var(--muted-on-ink);
}
.kind__btn--active {
  background: var(--accent);
  color: var(--accent-ink);
  font-weight: 600;
}
.grid {
  display: grid;
  gap: 1.2rem;
  grid-template-columns: repeat(2, 1fr);
}
.form__error {
  color: var(--danger);
  font-size: var(--fs-small);
}
.actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.8rem;
}
.delete {
  margin-left: auto;
  font-size: var(--fs-small);
  color: var(--danger);
  text-decoration: underline;
}
.delete:disabled {
  opacity: 0.5;
}
@media (max-width: 560px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
