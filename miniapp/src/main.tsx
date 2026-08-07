import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import { AppErrorBoundary } from '@/components/AppErrorBoundary'
import { AppStoreProvider } from '@/store/app-store'
import '@/styles/index.css'

const rootElement = document.getElementById('root')

if (rootElement) {
  createRoot(rootElement).render(
    <StrictMode>
      <AppErrorBoundary>
        <AppStoreProvider>
          <App />
        </AppStoreProvider>
      </AppErrorBoundary>
    </StrictMode>,
  )
}
