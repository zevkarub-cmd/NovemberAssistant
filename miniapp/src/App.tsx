import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { LoadingScreen } from '@/components/LoadingScreen'
import { AppLayout } from '@/layouts/AppLayout'
import { ClosingPage } from '@/pages/ClosingPage'
import { EmployeesPage } from '@/pages/EmployeesPage'
import { HomePage } from '@/pages/HomePage'
import { InventoryPage } from '@/pages/InventoryPage'
import { OpeningPage } from '@/pages/OpeningPage'
import { SettingsPage } from '@/pages/SettingsPage'
import { StatsPage } from '@/pages/StatsPage'
import { TasksPage } from '@/pages/TasksPage'
import { useAppStore } from '@/hooks/useAppStore'

export default function App() {
  const { isBootstrapping } = useAppStore()

  if (isBootstrapping) {
    return <LoadingScreen />
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<HomePage />} />
          <Route path="opening" element={<OpeningPage />} />
          <Route path="closing" element={<ClosingPage />} />
          <Route path="inventory" element={<InventoryPage />} />
          <Route path="employees" element={<EmployeesPage />} />
          <Route path="tasks" element={<TasksPage />} />
          <Route path="stats" element={<StatsPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
