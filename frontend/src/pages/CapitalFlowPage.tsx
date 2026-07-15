import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { AlertTriangle, CircleDashed, FileSpreadsheet, Info, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { InstrumentBifurcationChart } from '@/components/charts/InstrumentBifurcationChart'
import { GroupedBarChart } from '@/components/charts/GroupedBarChart'
import { MonthTrendChart } from '@/components/charts/MonthTrendChart'
import { useDpo } from '@/hooks/useDpo'
import { formatDays, formatIndianCurrency } from '@/lib/format'
import type { DpoResult } from '@/types/capitalFlow'

function LensHeader({ label, question }: { label: string; question: string }) {
  return (
    <div className="mb-3 flex items-baseline gap-3">
      <span className="font-mono text-xs uppercase tracking-widest text-primary">{label}</span>
      <span className="text-xs text-muted-foreground">{question}</span>
    </div>
  )
}

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

  const topSupplier = data.by_supplier.find((s) => s.group !== 'Other')
  const advance = data.by_instrument.find((i) => i.group === 'Advance')

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-8">
      <motion.div
        className="flex items-start justify-between gap-4"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
      >
        <div>
          <span className="font-mono text-[10px] tracking-widest text-muted-foreground">01 · CAPITAL FLOW</span>
          <h2 className="font-heading text-2xl font-semibold">Is capital moving or stuck?</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Days Payable Outstanding · job-work vendors and AR/AP netting excluded
          </p>
        </div>
        <Button variant="outline" size="sm" className="gap-2" nativeButton={false} render={<Link to="/capital-flow/payment-terms" />}>
          <FileSpreadsheet className="h-3.5 w-3.5" />
          Payment Terms Master
        </Button>
      </motion.div>

      {/* PERFORMANCE — are we growing? */}
      <motion.section initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25, delay: 0.05 }}>
        <LensHeader label="Performance" question="Are we growing?" />
        <div className="flex flex-col gap-4">
          <Card className="glass-panel border-0">
            <CardContent className="flex flex-col items-center gap-2 py-10">
              <span className="font-mono text-6xl font-medium tabular-nums text-primary">
                {data.dpo !== null ? formatDays(data.dpo) : '—'}
              </span>
              <span className="font-mono text-xs uppercase tracking-widest text-muted-foreground">DPO</span>
            </CardContent>
          </Card>
          <Card className="glass-panel border-0">
            <CardHeader>
              <CardTitle className="font-heading text-base">Month-wise trend</CardTitle>
            </CardHeader>
            <CardContent>
              {data.by_month.length > 1 ? (
                <MonthTrendChart data={data.by_month} />
              ) : (
                <p className="text-sm text-muted-foreground">Not enough months in range to show a trend.</p>
              )}
            </CardContent>
          </Card>
        </div>
      </motion.section>

      {/* RISK — what could hurt us? */}
      <motion.section initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25, delay: 0.1 }}>
        <LensHeader label="Risk" question="What could hurt us?" />
        <div className="flex flex-col gap-4">
          <Card className="glass-panel border-0">
            <CardHeader>
              <CardTitle className="font-heading text-base">Supplier concentration</CardTitle>
              {topSupplier && (
                <p className="text-xs text-muted-foreground">
                  Largest supplier ({topSupplier.group}) is {topSupplier.share_of_total_value_pct.toFixed(1)}% of PO value
                </p>
              )}
            </CardHeader>
            <CardContent>
              <GroupedBarChart data={data.by_supplier} labelWidth={170} />
            </CardContent>
          </Card>
          <Card className="glass-panel border-0">
            <CardHeader>
              <CardTitle className="font-heading text-base">Instrument mix</CardTitle>
              {advance && advance.share_of_total_value_pct > 30 && (
                <p className="flex items-center gap-1.5 text-xs text-amber-600 dark:text-amber-400">
                  <TrendingUp className="h-3 w-3" />
                  Advance is {advance.share_of_total_value_pct.toFixed(1)}% of value — cash tied up ahead of delivery
                </p>
              )}
            </CardHeader>
            <CardContent>
              <InstrumentBifurcationChart data={data.by_instrument} />
            </CardContent>
          </Card>
        </div>
      </motion.section>

      {/* CONTROL — are we disciplined? */}
      <motion.section initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25, delay: 0.15 }}>
        <LensHeader label="Control" question="Are we disciplined?" />
        <div className="flex flex-col gap-4">
          <Card className="glass-panel border-0">
            <CardHeader>
              <CardTitle className="font-heading text-base">Business unit-wise</CardTitle>
            </CardHeader>
            <CardContent>
              <GroupedBarChart data={data.by_business_unit} labelWidth={150} />
            </CardContent>
          </Card>

          <Card className="glass-panel border-0">
            <CardHeader>
              <CardTitle className="font-heading text-base">Payable-days distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <GroupedBarChart data={data.by_term_bucket} labelWidth={80} />
            </CardContent>
          </Card>

          <DataQualityPanel data={data} />
        </div>
      </motion.section>

      {/* AOP TRACKING — vs annual plan */}
      <motion.section initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25, delay: 0.2 }}>
        <LensHeader label="AOP tracking" question="vs annual plan" />
        <Card className="glass-panel border-0">
          <CardContent className="py-6">
            <p className="text-sm text-muted-foreground">
              No annual DPO target has been provided yet — this section activates once an AOP target for Capital Flow
              is available.
            </p>
          </CardContent>
        </Card>
      </motion.section>
    </div>
  )
}

function DataQualityPanel({ data }: { data: DpoResult }) {
  return (
    <Card className="glass-panel border-0">
      <CardHeader>
        <CardTitle className="font-heading text-base">Data quality</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <div className="mb-1 flex items-center gap-2">
              <Info className="h-3.5 w-3.5 text-amber-500" />
              <span className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Blank payment term</span>
            </div>
            <span className="font-mono text-xl font-medium tabular-nums text-amber-600 dark:text-amber-400">
              {formatIndianCurrency(data.blank_term_po_value)}
            </span>
            <span className="ml-2 text-sm text-muted-foreground">({data.blank_term_po_count})</span>
          </div>
          <div>
            <div className="mb-1 flex items-center gap-2">
              <Info className="h-3.5 w-3.5 text-amber-500" />
              <span className="font-mono text-xs uppercase tracking-widest text-muted-foreground">AR/AP netting excluded</span>
            </div>
            <span className="font-mono text-xl font-medium tabular-nums text-amber-600 dark:text-amber-400">
              {formatIndianCurrency(data.ar_ap_excluded_po_value)}
            </span>
            <span className="ml-2 text-sm text-muted-foreground">({data.ar_ap_excluded_po_count})</span>
          </div>
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between">
            <span className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Payment terms needing review</span>
            <Badge variant={data.terms_needing_review.length > 0 ? 'destructive' : 'secondary'} className="font-mono">
              {data.terms_needing_review.length}
            </Badge>
          </div>
          {data.terms_needing_review.length === 0 ? (
            <p className="text-sm text-muted-foreground">Every payment term in the current PO data is already in the master.</p>
          ) : (
            <ul className="flex flex-col gap-2.5">
              {data.terms_needing_review.map((term) => (
                <li
                  key={term.terms_description}
                  className="flex items-center justify-between gap-4 border-b border-border/50 pb-2.5 last:border-0 last:pb-0"
                >
                  <div>
                    <p className="text-sm font-medium">{term.terms_description}</p>
                    <p className="text-xs text-muted-foreground">
                      Auto-calculated: {formatDays(term.weighted_payable_days)} · {term.affected_po_count} PO
                      {term.affected_po_count === 1 ? '' : 's'}
                    </p>
                  </div>
                  <span className="font-mono text-sm tabular-nums text-amber-600 dark:text-amber-400">
                    {formatIndianCurrency(term.affected_po_value)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
