import type { ReactNode } from 'react'
import { Sidebar } from '@/components/layout/Sidebar'
import { Header } from '@/components/layout/Header'
import { BackgroundDecor } from '@/components/layout/BackgroundDecor'
import { FilterBar } from '@/components/filters/FilterBar'

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="relative flex h-screen w-full overflow-hidden">
      <BackgroundDecor />
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <FilterBar />
        <main className="flex-1 overflow-y-auto px-6 py-6">{children}</main>
      </div>
    </div>
  )
}
