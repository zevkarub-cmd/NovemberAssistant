import { AppHeader } from '@/components/AppHeader'
import { MenuCard } from '@/components/MenuCard'
import {
  OutsideTelegramState,
  TelegramStatus,
} from '@/components/TelegramStatus'
import { useTelegram } from '@/hooks/useTelegram'
import { menuItems } from '@/lib/menu'

export function HomePage() {
  const telegram = useTelegram()

  if (!telegram.isReady) {
    return <div className="flex flex-1" />
  }

  if (!telegram.isTelegram) {
    return <OutsideTelegramState />
  }

  return (
    <div className="flex flex-1 flex-col">
      <AppHeader />

      <div className="mt-5">
        <TelegramStatus connection={telegram} />
      </div>

      <section className="mt-8 flex flex-col gap-3">
        {menuItems.map((item, index) => (
          <div
            key={item.id}
            className="animate-in fade-in slide-in-from-bottom-2 fill-mode-both duration-500"
            style={{ animationDelay: `${80 + index * 50}ms` }}
          >
            <MenuCard item={item} />
          </div>
        ))}
      </section>
    </div>
  )
}
