import { useQuery } from '@tanstack/react-query'
import { getAllPaymentTerms } from '@/api/capitalFlow'

export function usePaymentTerms() {
  return useQuery({
    queryKey: ['payment-terms'],
    queryFn: getAllPaymentTerms,
    staleTime: 60 * 1000,
  })
}
