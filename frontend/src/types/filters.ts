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

export const BUSINESS_VERTICALS = ['Pharma', 'Agro', 'F&F', 'Industrial', 'Personal Care'] as const
export type BusinessVertical = (typeof BUSINESS_VERTICALS)[number]
