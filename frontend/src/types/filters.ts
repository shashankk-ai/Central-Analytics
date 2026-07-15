export type TimePeriodPreset = 'this_week' | 'this_month' | 'this_quarter' | 'this_fy' | 'custom'

export interface DateRange {
  from: string | null
  to: string | null
}

export interface TimePeriodFilter {
  preset: TimePeriodPreset
  range: DateRange
}

export interface GlobalFilters {
  timePeriod: TimePeriodFilter
  businessVerticals: string[]
  products: string[]
  suppliers: string[]
  customers: string[]
}
