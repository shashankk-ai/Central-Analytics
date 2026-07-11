import { Moon, RefreshCw, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useThemeStore } from '@/store/themeStore'

export function Header() {
  const { theme, toggle } = useThemeStore()

  return (
    <header className="glass-panel-soft sticky top-0 z-30 flex h-16 items-center justify-between rounded-none border-x-0 border-t-0 px-6">
      <div>
        <h1 className="font-heading text-lg font-semibold leading-tight">Central Analytics Overview</h1>
        <p className="font-mono text-[11px] tracking-wide text-muted-foreground">
          Scimplify · Cocreate Global Technologies Pvt. Ltd.
        </p>
      </div>
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground">
          <RefreshCw className="h-3.5 w-3.5" />
          <span className="font-mono text-xs">Live</span>
        </Button>
        <Button variant="ghost" size="icon" onClick={toggle} aria-label="Toggle theme">
          {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>
      </div>
    </header>
  )
}
