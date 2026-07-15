import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { GroupedDpo } from '@/types/capitalFlow'
import { formatDays, formatIndianCurrency } from '@/lib/format'

function TooltipContent({ active, payload }: { active?: boolean; payload?: { payload: GroupedDpo }[] }) {
  if (!active || !payload?.length) return null
  const bar = payload[0].payload
  return (
    <div className="glass-panel-soft rounded-lg border-0 px-3 py-2 text-xs shadow-lg">
      <p className="max-w-[220px] truncate font-medium">{bar.group}</p>
      <p className="font-mono text-muted-foreground">{formatIndianCurrency(bar.po_value)}</p>
      <p className="font-mono text-muted-foreground">
        {bar.weighted_payable_days !== null ? formatDays(bar.weighted_payable_days) : '—'} ·{' '}
        {bar.share_of_total_value_pct.toFixed(1)}%
      </p>
    </div>
  )
}

// Single-hue magnitude encoding — these bars compare "how much", not
// identity, so one color (not a categorical palette) is the correct form.
export function GroupedBarChart({ data, labelWidth = 140 }: { data: GroupedDpo[]; labelWidth?: number }) {
  return (
    <ResponsiveContainer width="100%" height={data.length * 34 + 24}>
      <BarChart data={data} layout="vertical" margin={{ top: 8, right: 24, bottom: 8, left: 8 }}>
        <XAxis type="number" hide />
        <YAxis
          type="category"
          dataKey="group"
          width={labelWidth}
          tickLine={false}
          axisLine={false}
          tick={{ fill: 'var(--muted-foreground)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
          tickFormatter={(value: string) => (value.length > 20 ? `${value.slice(0, 19)}…` : value)}
        />
        <Tooltip content={<TooltipContent />} cursor={{ fill: 'var(--muted)', opacity: 0.4 }} />
        <Bar dataKey="po_value" radius={[3, 3, 3, 3]} barSize={14} fill="var(--chart-1)" />
      </BarChart>
    </ResponsiveContainer>
  )
}
