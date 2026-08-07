export function LoadingScreen() {
  return (
    <div className="flex min-h-full flex-1 flex-col items-center justify-center px-6">
      <div className="relative mb-6 flex size-20 items-center justify-center">
        <div className="absolute inset-0 animate-pulse rounded-[1.75rem] bg-accent/25" />
        <div className="relative flex size-16 items-center justify-center rounded-[1.4rem] bg-gradient-to-br from-[#2a1f18] to-[#5c4030] shadow-[0_16px_40px_rgba(42,31,24,0.28)]">
          <span className="text-3xl leading-none">☕</span>
        </div>
      </div>

      <p className="text-lg font-semibold tracking-tight text-foreground">November</p>
      <p className="mt-2 text-sm text-muted-foreground">Загрузка приложения...</p>

      <div className="mt-8 h-1 w-28 overflow-hidden rounded-full bg-border">
        <div className="h-full w-1/2 animate-[loading_1.2s_ease-in-out_infinite] rounded-full bg-accent" />
      </div>
    </div>
  )
}
