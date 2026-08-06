import type { MenuItem } from '@/types'

export const menuItems: MenuItem[] = [
  {
    id: 'opening',
    title: '☀️ Открытие смены',
    description: 'Чек-лист и касса на старте дня',
    icon: 'sun',
    path: '/opening',
  },
  {
    id: 'closing',
    title: '🌙 Закрытие смены',
    description: 'Итоги дня и закрытие кассы',
    icon: 'moon',
    path: '/closing',
  },
  {
    id: 'inventory',
    title: '📦 Остатки',
    description: 'Учёт продуктов и расходников',
    icon: 'box',
    path: '/inventory',
  },
  {
    id: 'employees',
    title: '👥 Сотрудники',
    description: 'Команда и роли на смене',
    icon: 'users',
    path: '/employees',
  },
  {
    id: 'stats',
    title: '📊 Статистика',
    description: 'Показатели и аналитика',
    icon: 'stats',
    path: '/stats',
  },
  {
    id: 'settings',
    title: '⚙️ Настройки',
    description: 'Параметры приложения',
    icon: 'settings',
    path: '/settings',
  },
]
