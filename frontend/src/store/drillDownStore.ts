import { create } from 'zustand'
import type { DrillDownLevel } from '@/types/common'

interface DrillDownStore {
  isOpen: boolean
  metricId: string | null
  path: DrillDownLevel[]
  open: (metricId: string, rootLabel: string) => void
  pushLevel: (level: DrillDownLevel) => void
  popToIndex: (index: number) => void
  close: () => void
}

export const useDrillDownStore = create<DrillDownStore>((set) => ({
  isOpen: false,
  metricId: null,
  path: [],
  open: (metricId, rootLabel) =>
    set({
      isOpen: true,
      metricId,
      path: [{ label: rootLabel, dimension: 'company', value: null }],
    }),
  pushLevel: (level) => set((state) => ({ path: [...state.path, level] })),
  popToIndex: (index) => set((state) => ({ path: state.path.slice(0, index + 1) })),
  close: () => set({ isOpen: false, metricId: null, path: [] }),
}))
