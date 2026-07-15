import { apiGet } from '@/api/client'
import type { DpoFilters, DpoResult, PaymentTermOut } from '@/types/capitalFlow'

export function getDpo(filters?: DpoFilters) {
  return apiGet<DpoResult>('/capital-flow/dpo', {
    date_from: filters?.date_from ?? undefined,
    date_to: filters?.date_to ?? undefined,
    business_verticals: filters?.business_verticals,
    products: filters?.products,
    suppliers: filters?.suppliers,
  })
}

export function getPaymentTermsNeedingReview() {
  return apiGet<PaymentTermOut[]>('/payment-terms/needing-review')
}

export function getAllPaymentTerms() {
  return apiGet<PaymentTermOut[]>('/payment-terms')
}

export const PAYMENT_TERMS_EXPORT_URL = `${import.meta.env.VITE_API_BASE_URL ?? '/api'}/payment-terms/export`
