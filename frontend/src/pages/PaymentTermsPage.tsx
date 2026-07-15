import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { AlertTriangle, ArrowLeft, CircleDashed, Download } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { PAYMENT_TERMS_EXPORT_URL } from '@/api/capitalFlow'
import { usePaymentTerms } from '@/hooks/usePaymentTerms'
import { formatDays } from '@/lib/format'
import { instrumentColor } from '@/lib/instrumentColors'

const SOURCE_LABEL: Record<string, string> = {
  seed: 'Seed',
  auto: 'Auto-calculated',
  manual: 'Manual',
}

export function PaymentTermsPage() {
  const { data, isLoading, isError } = usePaymentTerms()
  const [search, setSearch] = useState('')

  const filtered = useMemo(() => {
    if (!data) return []
    const query = search.trim().toLowerCase()
    if (!query) return data
    return data.filter((term) => term.terms_description.toLowerCase().includes(query))
  }, [data, search])

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-5">
      <motion.div
        className="flex items-center justify-between gap-4"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
      >
        <div>
          <Button variant="ghost" size="sm" className="mb-2 gap-1.5 text-muted-foreground" nativeButton={false} render={<Link to="/capital-flow" />}>
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to Capital Flow
          </Button>
          <h2 className="font-heading text-2xl font-semibold">Payment Terms Master</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {data ? `${data.length} terms` : '—'} · resolves each PO's payment term to a weighted payable-days figure for DPO
          </p>
        </div>
        <Button variant="outline" size="sm" className="gap-2" nativeButton={false} render={<a href={PAYMENT_TERMS_EXPORT_URL} download />}>
          <Download className="h-3.5 w-3.5" />
          Export CSV
        </Button>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25, delay: 0.05 }}>
        <Card className="glass-panel border-0">
          <CardHeader>
            <Input
              placeholder="Search terms…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="max-w-xs bg-white/40 dark:bg-white/5"
            />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex justify-center py-10">
                <CircleDashed className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            ) : isError ? (
              <div className="flex flex-col items-center gap-2 py-10 text-muted-foreground">
                <AlertTriangle className="h-6 w-6 text-destructive" />
                Couldn't load the master.
              </div>
            ) : (
              <ScrollArea className="h-[60vh]">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-background/95 text-left font-mono text-[10px] uppercase tracking-widest text-muted-foreground backdrop-blur">
                    <tr>
                      <th className="py-2 pr-3">Terms description</th>
                      <th className="py-2 pr-3">Instrument</th>
                      <th className="py-2 pr-3 text-right">Weighted days</th>
                      <th className="py-2 pr-3">Calculation</th>
                      <th className="py-2 pr-3">Source</th>
                      <th className="py-2 pr-3">Flags</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((term) => (
                      <tr key={term.id} className="border-b border-border/40 last:border-0">
                        <td className="max-w-xs py-2.5 pr-3 font-medium">{term.terms_description}</td>
                        <td className="py-2.5 pr-3">
                          <Badge
                            variant="outline"
                            className="font-mono text-[10px]"
                            style={{ borderColor: instrumentColor(term.instrument), color: instrumentColor(term.instrument) }}
                          >
                            {term.instrument ?? 'Unclassified'}
                          </Badge>
                        </td>
                        <td className="py-2.5 pr-3 text-right font-mono tabular-nums">
                          {formatDays(term.weighted_payable_days)}
                        </td>
                        <td className="max-w-xs truncate py-2.5 pr-3 font-mono text-xs text-muted-foreground">
                          {term.calculation_trace ?? '—'}
                        </td>
                        <td className="py-2.5 pr-3 text-xs text-muted-foreground">{SOURCE_LABEL[term.source] ?? term.source}</td>
                        <td className="py-2.5 pr-3">
                          <div className="flex gap-1.5">
                            {term.needs_review && (
                              <Badge variant="destructive" className="font-mono text-[10px]">
                                Needs review
                              </Badge>
                            )}
                            {term.excluded_from_dpo && (
                              <Badge variant="outline" className="font-mono text-[10px]">
                                Excluded from DPO
                              </Badge>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </ScrollArea>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
