import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import { LayoutGrid } from 'lucide-react'
import { PILLARS } from '@/types/common'
import { cn } from '@/lib/utils'

export function Sidebar() {
  return (
    <aside className="flex h-full w-64 flex-col gap-1 border-r border-border/60 bg-sidebar/80 px-3 py-4 backdrop-blur-xl">
      <div className="mb-6 flex items-center gap-2 px-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <span className="font-heading text-sm font-semibold">S</span>
        </div>
        <div>
          <p className="font-heading text-sm font-semibold leading-tight">Scimplify</p>
          <p className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">Central Analytics</p>
        </div>
      </div>

      <NavItem to="/" label="Overview" icon={<LayoutGrid className="h-4 w-4" />} exact index="00" />

      <div className="mt-2 mb-1 px-3 text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
        Pillars
      </div>
      {PILLARS.map((pillar) => (
        <NavItem key={pillar.id} to={pillar.route} label={pillar.name} index={pillar.index} />
      ))}
    </aside>
  )
}

function NavItem({
  to,
  label,
  index,
  icon,
  exact,
}: {
  to: string
  label: string
  index: string
  icon?: React.ReactNode
  exact?: boolean
}) {
  return (
    <NavLink to={to} end={exact} className="relative">
      {({ isActive }) => (
        <motion.div
          className={cn(
            'relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-colors',
            isActive ? 'text-primary-foreground' : 'text-foreground/80 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
          )}
        >
          {isActive && (
            <motion.div
              layoutId="sidebar-active"
              className="absolute inset-0 rounded-xl bg-primary shadow-sm"
              transition={{ type: 'spring', stiffness: 400, damping: 32 }}
            />
          )}
          <span className="relative z-10 font-mono text-[10px] tabular-nums opacity-60">{index}</span>
          {icon && <span className="relative z-10">{icon}</span>}
          <span className="relative z-10 font-medium">{label}</span>
        </motion.div>
      )}
    </NavLink>
  )
}
