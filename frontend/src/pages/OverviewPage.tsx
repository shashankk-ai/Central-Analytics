import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { PILLARS } from '@/types/common'

const PHASE_STATUS: Record<string, { label: string; variant: 'outline' | 'secondary' }> = {
  'capital-flow': { label: 'Phase 1 · DPO live (DSO/DIO pending)', variant: 'secondary' },
  'sales-vs-aop': { label: 'Phase 2 · not started', variant: 'outline' },
  'margin-vs-aop': { label: 'Phase 3 · not started', variant: 'outline' },
  'expense-vs-aop': { label: 'Phase 4 · not started', variant: 'outline' },
  'support-kpis': { label: 'Phase 5 · not started', variant: 'outline' },
}

export function OverviewPage() {
  return (
    <div>
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
        <h2 className="font-heading text-2xl font-semibold">Central Analytics</h2>
        <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
          Foundation is live. Each pillar activates once its data sources, columns, and calculation logic are
          confirmed with leadership.
        </p>
      </motion.div>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {PILLARS.map((pillar, i) => (
          <motion.div
            key={pillar.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, delay: i * 0.05 }}
          >
            <Link to={pillar.route}>
              <Card className="glass-panel h-full border-0 transition-transform hover:-translate-y-0.5 hover:shadow-lg">
                <CardHeader className="flex flex-row items-start justify-between gap-2 space-y-0">
                  <div>
                    <span className="font-mono text-[10px] tracking-widest text-muted-foreground">{pillar.index}</span>
                    <h3 className="font-heading text-base font-semibold">{pillar.name}</h3>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{pillar.description}</p>
                  <Badge variant={PHASE_STATUS[pillar.id].variant} className="mt-4 font-mono text-[10px]">
                    {PHASE_STATUS[pillar.id].label}
                  </Badge>
                </CardContent>
              </Card>
            </Link>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
