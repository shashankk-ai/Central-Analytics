import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { InstrumentBifurcation } from '@/types/capitalFlow'
import { formatDays, formatIndianCurrency } from '@/lib/format'
import { instrumentColor } from '@/lib/instrumentColors'

function TooltipContent({ active, payload }: { active?: boolean; payload?: { payload: InstrumentBifurcation }[] }) {
  if (!active || !payload?.length) return null
  const bar = payload[0].payload
  return (
    <div className="glass-panel-soft rounded-lg border-0 px-3 py-2 text-xs shadow-lg">
      <p className="font-medium">{bar.instrument}</p>
      <p className="font-mono text-muted-foreground">{formatIndianCurrency(bar.po_value)}</p>
      <p className="font-mono text-muted-foreground">
        {bar.weighted_payable_days !== null ? formatDays(bar.weighted_payable_days) : '—'} ·{' '}
        {bar.share_of_total_value_pct.toFixed(1)}%
      </p>
    </div>
  )
}

export function InstrumentBifurcationChart({ data }: { data: InstrumentBifurcation[] }) {
  return (
    <ResponsiveContainer width="100%" height={data.length * 56 + 24}>
      <BarChart data={data} layout="vertical" margin={{ top: 8, right: 24, bottom: 8, left: 8 }}>
        <XAxis type="number" hide />
        <YAxis
          type="category"
          dataKey="instrument"
          width={100}
          tickLine={false}
          axisLine={false}
          tick={{ fill: 'var(--muted-foreground)', fontSize: 12, fontFamily: 'var(--font-mono)' }}
        />
        <Tooltip content={<TooltipContent />} cursor={{ fill: 'var(--muted)', opacity: 0.4 }} />
        <Bar dataKey="po_value" radius={[4, 4, 4, 4]} barSize={20}>
          {data.map((entry) => (
            <Cell key={entry.instrument} fill={instrumentColor(entry.instrument)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
