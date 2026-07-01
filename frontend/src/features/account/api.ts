import { apiFetch } from '@/shared/http'

export function changePassword(currentPassword: string, newPassword: string): Promise<void> {
  return apiFetch<void>('/auth/me/password', {
    method: 'PUT',
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  })
}

export function changeEmail(newEmail: string, currentPassword: string): Promise<{ email: string }> {
  return apiFetch<{ email: string }>('/auth/me/email', {
    method: 'PUT',
    body: JSON.stringify({ new_email: newEmail, current_password: currentPassword }),
  })
}

export function deleteAccount(currentPassword: string): Promise<void> {
  return apiFetch<void>('/auth/me', {
    method: 'DELETE',
    body: JSON.stringify({ current_password: currentPassword }),
  })
}
