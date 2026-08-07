export interface AppUser {
  id: number | null
  firstName: string
  lastName: string
  username: string | null
  fullName: string
  roleLabel: string
}

export interface AppThemeState {
  colorScheme: 'light' | 'dark'
}
