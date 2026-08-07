import { Component, type ReactNode } from 'react'
import { OutsideTelegramState } from '@/components/TelegramStatus'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
}

/**
 * Prevents a full white screen if something unexpected throws at runtime.
 */
export class AppErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return <OutsideTelegramState />
    }

    return this.props.children
  }
}
