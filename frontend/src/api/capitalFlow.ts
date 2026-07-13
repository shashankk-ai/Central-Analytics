import { apiGet } from '@/api/client'
import type { DpoResult, PaymentTermOut } from '@/types/capitalFlow'

export function getDpo() {
  return apiGet<DpoResult>('/capital-flow/dpo')
}

export function getPaymentTermsNeedingReview() {
  return apiGet<PaymentTermOut[]>('/payment-terms/needing-review')
}
