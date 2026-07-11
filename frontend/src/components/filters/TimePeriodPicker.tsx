import { format } from 'date-fns'
import { CalendarDays } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Calendar } from '@/components/ui/calendar'
import { useFilterStore } from '@/store/filterStore'
import type { TimePeriodPreset } from '@/types/filters'
import { cn } from '@/lib/utils'

const PRESETS: { value: TimePeriodPreset; label: string }[] = [
  { value: 'this_week', label: 'This week' },
  { value: 'this_month', label: 'This month' },
  { value: 'this_quarter', label: 'This quarter' },
  { value: 'this_fy', label: 'This FY' },
  { value: 'custom', label: 'Custom' },
]

export function TimePeriodPicker() {
  const { filters, setTimePeriodPreset, setCustomRange } = useFilterStore()
  const { preset, range } = filters.timePeriod

  const label =
    preset === 'custom' && range.from
      ? `${format(new Date(range.from), 'd MMM')} – ${range.to ? format(new Date(range.to), 'd MMM yyyy') : '…'}`
      : PRESETS.find((p) => p.value === preset)?.label ?? 'This month'

  return (
    <Popover>
      <PopoverTrigger
        render={
          <Button variant="outline" size="sm" className="h-9 gap-2 border-border/60 bg-white/40 font-normal dark:bg-white/5" />
        }
      >
        <CalendarDays className="h-3.5 w-3.5 text-muted-foreground" />
        {label}
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <div className="flex">
          <div className="flex flex-col gap-1 border-r border-border/60 p-2">
            {PRESETS.map((p) => (
              <Button
                key={p.value}
                variant="ghost"
                size="sm"
                className={cn('justify-start', preset === p.value && 'bg-accent text-accent-foreground')}
                onClick={() => setTimePeriodPreset(p.value)}
              >
                {p.label}
              </Button>
            ))}
          </div>
          {preset === 'custom' && (
            <Calendar
              mode="range"
              selected={{
                from: range.from ? new Date(range.from) : undefined,
                to: range.to ? new Date(range.to) : undefined,
              }}
              onSelect={(value) =>
                setCustomRange(
                  value?.from ? value.from.toISOString() : null,
                  value?.to ? value.to.toISOString() : null,
                )
              }
            />
          )}
        </div>
      </PopoverContent>
    </Popover>
  )
}
