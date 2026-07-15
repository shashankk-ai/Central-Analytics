import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { AlertTriangle, CircleDashed, FileSpreadsheet, Info } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { InstrumentBifurcationChart } from '@/components/charts/InstrumentBifurcationChart'
import { useDpo } from '@/hooks/useDpo'
import { formatDays, formatIndianCurrency } from '@/lib/format'

export function CapitalFlowPage() {
  const { data, isLoading, isError, error } = useDpo()

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <CircleDashed className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="flex h-full items-center justify-center">
        <Card className="glass-panel max-w-md border-0">
          <CardHeader className="items-center">
            <AlertTriangle className="mb-2 h-8 w-8 text-destructive" />
            <CardTitle className="font-heading text-lg">Couldn't load DPO</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-center text-sm text-muted-foreground">{String(error)}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-5">
      <motion.div
        className="flex items-start justify-between gap-4"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
      >
        <div>
          <h2 className="font-heading text-2xl font-semibold">Days Payable Outstanding</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Reflects the active filters above · job-work vendors and AR/AP netting excluded
          </p>
        </div>
        <Button variant="outline" size="sm" className="gap-2" nativeButton={false} render={<Link to="/capital-flow/payment-terms" />}>
          <FileSpreadsheet className="h-3.5 w-3.5" />
          Payment Terms Master
        </Button>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25, delay: 0.05 }}>
        <Card className="glass-panel border-0">
          <CardContent className="flex flex-col items-center gap-2 py-10">
            <span className="font-mono text-6xl font-medium tabular-nums text-primary">
              {data.dpo !== null ? formatDays(data.dpo) : '—'}
            </span>
            <span className="font-mono text-xs uppercase tracking-widest text-muted-foreground">DPO</span>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25, delay: 0.08 }}>
        <Card className="glass-panel border-0">
          <CardHeader>
            <CardTitle className="font-heading text-base">Instrument-wise bifurcation</CardTitle>
          </CardHeader>
          <CardContent>
            <InstrumentBifurcationChart data={data.by_instrument} />
          </CardContent>
        </Card>
      </motion.div>

      <motion.div
        className="grid grid-cols-1 gap-4 sm:grid-cols-3"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25, delay: 0.1 }}
      >
        <Card className="glass-panel border-0">
          <CardHeader>
            <CardTitle className="font-mono text-xs uppercase tracking-widest text-muted-foreground">
              Total PO value included
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="font-mono text-2xl font-medium tabular-nums">
              {formatIndianCurrency(data.total_po_value)}
            </span>
          </CardContent>
        </Card>

        <Card className="glass-panel border-0">
          <CardHeader className="flex flex-row items-center gap-2 space-y-0">
            <Info className="h-4 w-4 text-amber-500" />
            <CardTitle className="font-mono text-xs uppercase tracking-widest text-muted-foreground">
              Blank payment term
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="font-mono text-2xl font-medium tabular-nums text-amber-600 dark:text-amber-400">
              {formatIndianCurrency(data.blank_term_po_value)}
            </span>
            <span className="ml-2 text-sm text-muted-foreground">({data.blank_term_po_count})</span>
          </CardContent>
        </Card>

        <Card className="glass-panel border-0">
          <CardHeader className="flex flex-row items-center gap-2 space-y-0">
            <Info className="h-4 w-4 text-amber-500" />
            <CardTitle className="font-mono text-xs uppercase tracking-widest text-muted-foreground">
              AR/AP netting excluded
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="font-mono text-2xl font-medium tabular-nums text-amber-600 dark:text-amber-400">
              {formatIndianCurrency(data.ar_ap_excluded_po_value)}
            </span>
            <span className="ml-2 text-sm text-muted-foreground">({data.ar_ap_excluded_po_count})</span>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25, delay: 0.15 }}>
        <Card className="glass-panel border-0">
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle className="font-heading text-base">Payment terms needing review</CardTitle>
            <Badge variant={data.terms_needing_review.length > 0 ? 'destructive' : 'secondary'} className="font-mono">
              {data.terms_needing_review.length}
            </Badge>
          </CardHeader>
          <CardContent>
            {data.terms_needing_review.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Every payment term in the current PO data is already in the master.
              </p>
            ) : (
              <ul className="flex flex-col gap-3">
                {data.terms_needing_review.map((term) => (
                  <li
                    key={term.terms_description}
                    className="flex items-center justify-between gap-4 border-b border-border/50 pb-3 last:border-0 last:pb-0"
                  >
                    <div>
                      <p className="text-sm font-medium">{term.terms_description}</p>
                      <p className="text-xs text-muted-foreground">
                        Auto-calculated: {formatDays(term.weighted_payable_days)} ·{' '}
                        {term.affected_po_count} PO{term.affected_po_count === 1 ? '' : 's'}
                      </p>
                    </div>
                    <span className="font-mono text-sm tabular-nums text-amber-600 dark:text-amber-400">
                      {formatIndianCurrency(term.affected_po_value)}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
