import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/api/client'

interface FilterOptions {
  products: string[]
  suppliers: string[]
  customers: string[]
}

const EMPTY_OPTIONS: FilterOptions = { products: [], suppliers: [], customers: [] }

export function useFilterOptions() {
  const query = useQuery({
    queryKey: ['filter-options'],
    queryFn: () => apiGet<FilterOptions>('/filters/options'),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  })

  return {
    options: query.data ?? EMPTY_OPTIONS,
    isLoading: query.isLoading,
    isError: query.isError,
  }
}
