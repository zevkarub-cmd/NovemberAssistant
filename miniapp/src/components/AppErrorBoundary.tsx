import { Component, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
}

export class AppErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-full flex-1 items-center justify-center px-6">
          <div className="w-full max-w-sm rounded-2xl border border-border bg-card p-8 text-center shadow-[0_16px_48px_rgba(26,20,16,0.1)]">
            <p className="text-base font-semibold text-foreground">
              Что-то пошло не так
            </p>
            <p className="mt-2 text-sm text-muted-foreground">
              Перезапустите приложение
            </p>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
