import { Outlet } from 'react-router-dom'
import { AppFooter } from '@/components/AppFooter'

export function AppLayout() {
  return (
    <div className="relative mx-auto flex min-h-full w-full max-w-md flex-1 flex-col">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-56 bg-[radial-gradient(ellipse_at_top,_rgba(212,165,116,0.18),_transparent_65%)]"
      />
      <main className="relative z-10 flex flex-1 flex-col px-4 pb-2 pt-[max(1.25rem,env(safe-area-inset-top))]">
        <Outlet />
      </main>
      <AppFooter />
    </div>
  )
}
