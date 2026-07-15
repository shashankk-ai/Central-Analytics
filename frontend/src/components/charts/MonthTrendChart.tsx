import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { GroupedDpo } from '@/types/capitalFlow'
import { formatDays, formatIndianCurrency } from '@/lib/format'

function TooltipContent({ active, payload }: { active?: boolean; payload?: { payload: GroupedDpo }[] }) {
  if (!active || !payload?.length) return null
  const point = payload[0].payload
  return (
    <div className="glass-panel-soft rounded-lg border-0 px-3 py-2 text-xs shadow-lg">
      <p className="font-medium">{point.group}</p>
      <p className="font-mono text-primary">{point.weighted_payable_days !== null ? formatDays(point.weighted_payable_days) : '—'}</p>
      <p className="font-mono text-muted-foreground">{formatIndianCurrency(point.po_value)}</p>
    </div>
  )
}

export function MonthTrendChart({ data }: { data: GroupedDpo[] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
        <XAxis
          dataKey="group"
          tickLine={false}
          axisLine={false}
          tick={{ fill: 'var(--muted-foreground)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
        />
        <YAxis
          tickLine={false}
          axisLine={false}
          width={36}
          tick={{ fill: 'var(--muted-foreground)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
        />
        <Tooltip content={<TooltipContent />} cursor={{ stroke: 'var(--muted-foreground)', strokeDasharray: '3 3' }} />
        <Line
          type="monotone"
          dataKey="weighted_payable_days"
          stroke="var(--chart-1)"
          strokeWidth={2}
          dot={{ r: 3, fill: 'var(--chart-1)', strokeWidth: 0 }}
          activeDot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
