import { format, startOfMonth, startOfQuarter, startOfWeek } from 'date-fns'
import type { TimePeriodFilter } from '@/types/filters'

const ISO_DATE = 'yyyy-MM-dd'

export function resolveDateRange(timePeriod: TimePeriodFilter): { from: string | null; to: string | null } {
  const today = new Date()
  const to = format(today, ISO_DATE)

  switch (timePeriod.preset) {
    case 'this_week':
      return { from: format(startOfWeek(today, { weekStartsOn: 1 }), ISO_DATE), to }
    case 'this_month':
      return { from: format(startOfMonth(today), ISO_DATE), to }
    case 'this_quarter':
      return { from: format(startOfQuarter(today), ISO_DATE), to }
    case 'this_fy': {
      // Indian fiscal year: 1 April - 31 March
      const fyStartYear = today.getMonth() >= 3 ? today.getFullYear() : today.getFullYear() - 1
      return { from: format(new Date(fyStartYear, 3, 1), ISO_DATE), to }
    }
    case 'custom':
      return {
        from: timePeriod.range.from ? format(new Date(timePeriod.range.from), ISO_DATE) : null,
        to: timePeriod.range.to ? format(new Date(timePeriod.range.to), ISO_DATE) : null,
      }
  }
}
