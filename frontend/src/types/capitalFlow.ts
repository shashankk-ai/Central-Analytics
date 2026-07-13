export interface TermNeedingReview {
  terms_description: string
  weighted_payable_days: number
  affected_po_value: number
  affected_po_count: number
  newly_auto_created: boolean
}

export interface DpoResult {
  dpo: number | null
  total_po_value: number
  blank_term_po_value: number
  blank_term_po_count: number
  terms_needing_review: TermNeedingReview[]
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
  updated_at: string
}
