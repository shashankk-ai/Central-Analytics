import { create } from 'zustand'
import type { GlobalFilters, TimePeriodPreset } from '@/types/filters'

interface FilterStore {
  filters: GlobalFilters
  setTimePeriodPreset: (preset: TimePeriodPreset) => void
  setCustomRange: (from: string | null, to: string | null) => void
  setBusinessVerticals: (values: string[]) => void
  setProducts: (values: string[]) => void
  setSuppliers: (values: string[]) => void
  setCustomers: (values: string[]) => void
  clearAll: () => void
}

const defaultFilters: GlobalFilters = {
  timePeriod: { preset: 'this_month', range: { from: null, to: null } },
  businessVerticals: [],
  products: [],
  suppliers: [],
  customers: [],
}

export const useFilterStore = create<FilterStore>((set) => ({
  filters: defaultFilters,
  setTimePeriodPreset: (preset) =>
    set((state) => ({ filters: { ...state.filters, timePeriod: { ...state.filters.timePeriod, preset } } })),
  setCustomRange: (from, to) =>
    set((state) => ({
      filters: { ...state.filters, timePeriod: { preset: 'custom', range: { from, to } } },
    })),
  setBusinessVerticals: (values) => set((state) => ({ filters: { ...state.filters, businessVerticals: values } })),
  setProducts: (values) => set((state) => ({ filters: { ...state.filters, products: values } })),
  setSuppliers: (values) => set((state) => ({ filters: { ...state.filters, suppliers: values } })),
  setCustomers: (values) => set((state) => ({ filters: { ...state.filters, customers: values } })),
  clearAll: () => set({ filters: defaultFilters }),
}))
