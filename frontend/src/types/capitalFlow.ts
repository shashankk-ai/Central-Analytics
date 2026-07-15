export interface TermNeedingReview {
  terms_description: string
  weighted_payable_days: number
  affected_po_value: number
  affected_po_count: number
  newly_auto_created: boolean
}

export interface GroupedDpo {
  group: string
  po_value: number
  weighted_payable_days: number | null
  share_of_total_value_pct: number
}

export interface DpoResult {
  dpo: number | null
  total_po_value: number
  blank_term_po_value: number
  blank_term_po_count: number
  ar_ap_excluded_po_value: number
  ar_ap_excluded_po_count: number
  terms_needing_review: TermNeedingReview[]
  by_instrument: GroupedDpo[]
  by_month: GroupedDpo[]
  by_supplier: GroupedDpo[]
  by_business_unit: GroupedDpo[]
  by_term_bucket: GroupedDpo[]
}

export interface PaymentTermOut {
  id: number
  termskey: string | null
  terms_description: string
  instrument: string | null
  weighted_payable_days: number
  calculation_trace: string | null
  remarks: string | null
  source: string
  needs_review: boolean
  excluded_from_dpo: boolean
  updated_at: string
}

export interface DpoFilters {
  date_from?: string | null
  date_to?: string | null
  business_verticals?: string[]
  products?: string[]
  suppliers?: string[]
}
