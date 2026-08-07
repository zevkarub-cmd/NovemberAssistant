import { CheckCircle2 } from 'lucide-react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import type { TelegramConnection } from '@/types/telegram'

interface TelegramStatusProps {
  connection: TelegramConnection
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-border/50 py-2.5 last:border-b-0 last:pb-0">
      <span className="shrink-0 text-sm text-muted-foreground">{label}</span>
      <span className="text-right text-sm font-medium break-all text-foreground">
        {value}
      </span>
    </div>
  )
}

function displayValue(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  return String(value)
}

/**
 * Telegram connection card + raw initDataUnsafe dump.
 */
export function TelegramStatus({ connection }: TelegramStatusProps) {
  if (!connection.isReady || !connection.isTelegram) {
    return null
  }

  const { user } = connection
  const viewportSize =
    connection.viewportWidth != null && connection.viewportHeight != null
      ? `${Math.round(connection.viewportWidth)} × ${Math.round(connection.viewportHeight)}`
      : '—'

  const rawJson = JSON.stringify(connection.initDataUnsafe ?? {}, null, 2)

  return (
    <div className="flex flex-col gap-4">
      <Card className="overflow-hidden p-0 shadow-[0_12px_40px_rgba(26,20,16,0.08)]">
        <CardHeader className="border-b border-border/50 bg-secondary/40 px-5 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex size-9 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
              <CheckCircle2 className="size-5" strokeWidth={2.25} />
            </div>
            <div>
              <CardTitle className="text-[15px]">✅ Mini App подключен</CardTitle>
              <CardDescription className="mt-0.5">
                Telegram WebApp активен
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="px-5 py-2">
          <InfoRow label="Имя" value={displayValue(user?.firstName)} />
          <InfoRow label="Фамилия" value={displayValue(user?.lastName)} />
          <InfoRow
            label="Username"
            value={user?.username ? `@${user.username}` : '—'}
          />
          <InfoRow label="Telegram ID" value={displayValue(user?.id)} />
          <InfoRow label="Язык" value={displayValue(user?.languageCode)} />
          <InfoRow label="Платформа" value={displayValue(connection.platform)} />
          <InfoRow
            label="Версия Telegram"
            value={displayValue(connection.version)}
          />
          <InfoRow
            label="Тема Telegram"
            value={displayValue(connection.colorScheme)}
          />
          <InfoRow label="Размер окна" value={viewportSize} />
        </CardContent>
      </Card>

      <Card className="overflow-hidden p-0 shadow-[0_12px_40px_rgba(26,20,16,0.08)]">
        <CardHeader className="border-b border-border/50 px-5 py-4">
          <CardTitle className="text-[15px]">Raw Telegram Data</CardTitle>
          <CardDescription>initDataUnsafe</CardDescription>
        </CardHeader>
        <CardContent className="px-4 py-4">
          <div className="overflow-x-auto rounded-xl bg-[#1a1410] p-4">
            <pre className="m-0 font-mono text-[11px] leading-relaxed whitespace-pre-wrap text-[#e8dcc8]">
              {rawJson}
            </pre>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

/**
 * Full-page state when the Mini App is opened outside Telegram.
 */
export function OutsideTelegramState() {
  return (
    <div className="flex flex-1 items-center justify-center px-6 py-16">
      <Card className="w-full max-w-sm p-8 text-center shadow-[0_16px_48px_rgba(26,20,16,0.1)]">
        <p className="text-base font-semibold tracking-tight text-foreground">
          Запущено вне Telegram
        </p>
      </Card>
    </div>
  )
}
