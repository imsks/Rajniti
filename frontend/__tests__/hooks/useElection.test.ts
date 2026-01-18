/**
 * Unit tests for useElection and useElections hooks
 */

import { renderHook, waitFor } from '@testing-library/react'
import { useElection, useElections } from '@/hooks/useElection'

// Mock fetch globally
const mockFetch = jest.fn()
global.fetch = mockFetch

describe('useElection', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('should return null when electionId is null', () => {
    const { result } = renderHook(() => useElection(null))
    
    expect(result.current.election).toBeNull()
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('should fetch election data successfully', async () => {
    const mockElection = {
      id: 'lok-sabha-2024',
      name: 'Lok Sabha Elections 2024',
      year: 2024,
      type: 'LOK_SABHA',
      statistics: {
        total_candidates: 8000,
        total_constituencies: 543,
        total_parties: 450,
        total_winners: 543,
      },
    }

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true, data: mockElection }),
    })

    const { result } = renderHook(() => useElection('lok-sabha-2024'))

    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.election).toEqual(mockElection)
    expect(result.current.error).toBeNull()
  })

  it('should handle API error response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: false, error: 'Election not found' }),
    })

    const { result } = renderHook(() => useElection('nonexistent'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.election).toBeNull()
    expect(result.current.error).toBe('Election not found')
  })

  it('should handle network error', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => useElection('lok-sabha-2024'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.election).toBeNull()
    expect(result.current.error).toBe('Error connecting to API')
  })

  it('should refetch when electionId changes', async () => {
    const election1 = { id: 'election-1', name: 'Election 1', year: 2024, type: 'LOK_SABHA' }
    const election2 = { id: 'election-2', name: 'Election 2', year: 2024, type: 'VIDHAN_SABHA' }

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true, data: election1 }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true, data: election2 }),
      })

    const { result, rerender } = renderHook(
      ({ id }) => useElection(id),
      { initialProps: { id: 'election-1' } }
    )

    await waitFor(() => {
      expect(result.current.election?.id).toBe('election-1')
    })

    rerender({ id: 'election-2' })

    await waitFor(() => {
      expect(result.current.election?.id).toBe('election-2')
    })
  })
})

describe('useElections', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('should fetch all elections successfully', async () => {
    const mockElections = [
      { id: 'election-1', name: 'Election 1', year: 2024, type: 'LOK_SABHA' },
      { id: 'election-2', name: 'Election 2', year: 2024, type: 'VIDHAN_SABHA' },
    ]

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true, data: mockElections }),
    })

    const { result } = renderHook(() => useElections())

    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.elections).toEqual(mockElections)
    expect(result.current.error).toBeNull()
  })

  it('should handle empty elections list', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true, data: [] }),
    })

    const { result } = renderHook(() => useElections())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.elections).toEqual([])
    expect(result.current.error).toBeNull()
  })

  it('should handle API error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: false, error: 'Server error' }),
    })

    const { result } = renderHook(() => useElections())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.elections).toEqual([])
    expect(result.current.error).toBe('Server error')
  })

  it('should handle network error', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => useElections())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.elections).toEqual([])
    expect(result.current.error).toBe('Error connecting to API')
  })
})
