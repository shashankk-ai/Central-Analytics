// Fixed categorical order (validated for CVD-safety) — never cycled, never
// reassigned by filtering. See dataviz skill: color-formula.md.
export const INSTRUMENT_COLORS: Record<string, string> = {
  'Clean Credit': 'var(--chart-1)',
  Advance: 'var(--chart-2)',
  LC: 'var(--chart-3)',
  DA: 'var(--chart-4)',
  Unclassified: 'var(--chart-5)',
}

export function instrumentColor(instrument: string | null): string {
  return INSTRUMENT_COLORS[instrument ?? 'Unclassified'] ?? INSTRUMENT_COLORS.Unclassified
}
