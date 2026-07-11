const CRORE = 1_00_00_000
const LAKH = 1_00_000

export function formatIndianCurrency(value: number): string {
  const abs = Math.abs(value)
  const sign = value < 0 ? '-' : ''
  if (abs >= CRORE) return `${sign}₹${(abs / CRORE).toFixed(2)} Cr`
  if (abs >= LAKH) return `${sign}₹${(abs / LAKH).toFixed(2)} L`
  return `${sign}₹${abs.toLocaleString('en-IN')}`
}

export function formatDays(value: number): string {
  return `${value.toFixed(1)}d`
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`
}

export type Direction = 'up' | 'down' | 'flat'

export function directionOf(value: number): Direction {
  if (value > 0) return 'up'
  if (value < 0) return 'down'
  return 'flat'
}

export function directionArrow(direction: Direction): string {
  if (direction === 'up') return '↑'
  if (direction === 'down') return '↓'
  return '='
}
