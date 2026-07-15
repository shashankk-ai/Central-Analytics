import { useQuery } from '@tanstack/react-query'
import { getDpo } from '@/api/capitalFlow'
import { useFilterStore } from '@/store/filterStore'
import { resolveDateRange } from '@/lib/dateRange'
import type { DpoFilters } from '@/types/capitalFlow'

export function useDpo() {
  const { filters } = useFilterStore()
  const { from, to } = resolveDateRange(filters.timePeriod)

  const dpoFilters: DpoFilters = {
    date_from: from,
    date_to: to,
    business_verticals: filters.businessVerticals,
    products: filters.products,
    suppliers: filters.suppliers,
  }

  return useQuery({
    queryKey: ['capital-flow', 'dpo', dpoFilters],
    queryFn: () => getDpo(dpoFilters),
    staleTime: 60 * 1000,
  })
}
