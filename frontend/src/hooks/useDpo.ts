import { useQuery } from '@tanstack/react-query'
import { getDpo } from '@/api/capitalFlow'

export function useDpo() {
  return useQuery({
    queryKey: ['capital-flow', 'dpo'],
    queryFn: getDpo,
    staleTime: 60 * 1000,
  })
}
