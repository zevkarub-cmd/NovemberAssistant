import type { TelegramUser } from '@/types/telegram'
import type { AppUser } from '@/types/user'

const DEFAULT_ROLE = 'Загрузка...'

export function createGuestUser(): AppUser {
  return {
    id: null,
    firstName: 'Гость',
    lastName: '',
    username: null,
    fullName: 'Гость',
    roleLabel: DEFAULT_ROLE,
  }
}

export function mapTelegramUser(user: TelegramUser | null): AppUser {
  if (!user) {
    return createGuestUser()
  }

  const firstName = user.firstName?.trim() || 'Сотрудник'
  const lastName = user.lastName?.trim() || ''
  const fullName = [firstName, lastName].filter(Boolean).join(' ')

  return {
    id: user.id,
    firstName,
    lastName,
    username: user.username ?? null,
    fullName,
    roleLabel: DEFAULT_ROLE,
  }
}
