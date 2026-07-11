export type Status = 'green' | 'amber' | 'red' | 'neutral'

export interface DrillDownLevel {
  label: string
  dimension: 'company' | 'vertical' | 'product' | 'supplier' | 'customer'
  value: string | null
}

export interface Pillar {
  id: string
  index: string
  name: string
  description: string
  route: string
}

export const PILLARS: Pillar[] = [
  { id: 'capital-flow', index: '01', name: 'Capital flow', description: 'Is capital moving or stuck?', route: '/capital-flow' },
  { id: 'sales-vs-aop', index: '02', name: 'Sales vs AOP', description: 'Revenue against annual plan', route: '/sales-vs-aop' },
  { id: 'margin-vs-aop', index: '03', name: 'Margin vs AOP', description: 'CM1 · CM2 · CM3 vs plan', route: '/margin-vs-aop' },
  { id: 'expense-vs-aop', index: '04', name: 'Expense vs AOP', description: 'Actual spend vs budget', route: '/expense-vs-aop' },
  { id: 'support-kpis', index: '05', name: 'Support KPIs', description: 'Function targets vs AOP', route: '/support-kpis' },
]
