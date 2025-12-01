// /frontend/src/tests/gantt.test.ts
/**
 * Tests for Gantt chart utility functions.
 */
import { describe, it, expect } from 'vitest'
import type { SubTaskStatus } from '@/types'

// Status to color mapping function (extracted for testing)
function getStatusColor(status: SubTaskStatus, isPast: boolean = false): string {
  const opacity = isPast ? ' opacity-60' : ''

  switch (status) {
    case 'PLANNED':
      return `bg-sky-400 dark:bg-sky-500${opacity}`
    case 'IN_PROGRESS':
      return `bg-blue-500 dark:bg-blue-400${opacity}`
    case 'COMPLETED':
      return 'bg-emerald-500 dark:bg-emerald-400 opacity-70'
    case 'OVERDUE':
      return 'bg-rose-500 dark:bg-rose-400'
    default:
      return 'bg-slate-400'
  }
}

// Scale calculation function (matching backend logic)
function calculateScale(startDate: Date, endDate: Date): 'day' | 'week' | 'month' {
  const totalDays = Math.ceil(
    (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)
  ) + 1

  if (totalDays <= 30) return 'day'
  if (totalDays <= 180) return 'week'
  return 'month'
}

describe('Status Color Mapping', () => {
  it('should return sky color for PLANNED status', () => {
    const color = getStatusColor('PLANNED')
    expect(color).toContain('sky')
  })

  it('should return blue color for IN_PROGRESS status', () => {
    const color = getStatusColor('IN_PROGRESS')
    expect(color).toContain('blue')
  })

  it('should return emerald color for COMPLETED status', () => {
    const color = getStatusColor('COMPLETED')
    expect(color).toContain('emerald')
  })

  it('should return rose color for OVERDUE status', () => {
    const color = getStatusColor('OVERDUE')
    expect(color).toContain('rose')
  })

  it('should add opacity for past tasks', () => {
    const color = getStatusColor('PLANNED', true)
    expect(color).toContain('opacity-60')
  })
})

describe('Scale Calculation', () => {
  it('should return "day" for ranges <= 30 days', () => {
    const start = new Date('2025-01-01')
    const end = new Date('2025-01-15')
    expect(calculateScale(start, end)).toBe('day')
  })

  it('should return "week" for ranges 31-180 days', () => {
    const start = new Date('2025-01-01')
    const end = new Date('2025-03-15')
    expect(calculateScale(start, end)).toBe('week')
  })

  it('should return "month" for ranges > 180 days', () => {
    const start = new Date('2025-01-01')
    const end = new Date('2025-08-01')
    expect(calculateScale(start, end)).toBe('month')
  })
})

describe('Date Delta Calculation for Drag', () => {
  // FAZ-2: Drag & drop delta hesaplama için test
  function calculateDateDelta(
    originalStart: Date,
    originalEnd: Date,
    pixelDelta: number,
    columnWidth: number
  ): { newStart: Date; newEnd: Date } {
    const daysDelta = Math.round(pixelDelta / columnWidth)

    const newStart = new Date(originalStart)
    newStart.setDate(newStart.getDate() + daysDelta)

    const newEnd = new Date(originalEnd)
    newEnd.setDate(newEnd.getDate() + daysDelta)

    return { newStart, newEnd }
  }

  it('should calculate correct date delta from pixel movement', () => {
    const originalStart = new Date('2025-01-10')
    const originalEnd = new Date('2025-01-15')
    const pixelDelta = 80 // 2 days at 40px per day
    const columnWidth = 40

    const { newStart, newEnd } = calculateDateDelta(
      originalStart,
      originalEnd,
      pixelDelta,
      columnWidth
    )

    expect(newStart.getDate()).toBe(12)
    expect(newEnd.getDate()).toBe(17)
  })

  it('should handle negative delta (drag left)', () => {
    const originalStart = new Date('2025-01-10')
    const originalEnd = new Date('2025-01-15')
    const pixelDelta = -120 // -3 days
    const columnWidth = 40

    const { newStart, newEnd } = calculateDateDelta(
      originalStart,
      originalEnd,
      pixelDelta,
      columnWidth
    )

    expect(newStart.getDate()).toBe(7)
    expect(newEnd.getDate()).toBe(12)
  })
})

