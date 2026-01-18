/**
 * Unit tests for useCandidate and useSearchCandidates hooks
 */

import { renderHook, waitFor, act } from '@testing-library/react'
import { useCandidate, useSearchCandidates } from '@/hooks/useCandidate'

// Mock fetch globally
const mockFetch = jest.fn()
global.fetch = mockFetch

describe('useCandidate', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('should return null when candidateId is null', () => {
    const { result } = renderHook(() => useCandidate(null))
    
    expect(result.current.candidate).toBeNull()
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('should fetch candidate data successfully', async () => {
    const mockCandidate = {
      id: 'candidate-123',
      name: 'Test Candidate',
      party_name: 'Test Party',
      party_short_name: 'TP',
      constituency_name: 'Test Constituency',
      constituency_id: 'TC-1',
      state_id: 'TS',
      status: 'WON',
      type: 'MLA',
      election_id: 'election-2024',
    }

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true, data: mockCandidate }),
    })

    const { result } = renderHook(() => useCandidate('candidate-123'))

    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.candidate).toEqual(mockCandidate)
    expect(result.current.error).toBeNull()
  })

  it('should fetch candidate with detailed information', async () => {
    const mockCandidate = {
      id: 'candidate-123',
      name: 'Test Candidate',
      party_name: 'Test Party',
      party_short_name: 'TP',
      constituency_name: 'Test Constituency',
      constituency_id: 'TC-1',
      state_id: 'TS',
      status: 'WON',
      type: 'MLA',
      election_id: 'election-2024',
      education_background: [
        { year: '2000', college: 'Test University', stream: 'Political Science' }
      ],
      political_background: [
        { election_year: '2019', party: 'TP', result: 'WON' }
      ],
      assets: [
        { type: 'CASH', amount: 1000000, description: 'Savings' }
      ],
    }

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true, data: mockCandidate }),
    })

    const { result } = renderHook(() => useCandidate('candidate-123'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.candidate?.education_background).toHaveLength(1)
    expect(result.current.candidate?.political_background).toHaveLength(1)
    expect(result.current.candidate?.assets).toHaveLength(1)
  })

  it('should handle candidate not found', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: false, error: 'Candidate not found' }),
    })

    const { result } = renderHook(() => useCandidate('nonexistent'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.candidate).toBeNull()
    expect(result.current.error).toBe('Candidate not found')
  })

  it('should handle network error', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => useCandidate('candidate-123'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.candidate).toBeNull()
    expect(result.current.error).toBe('Error connecting to API')
  })
})

describe('useSearchCandidates', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('should initialize with empty state', () => {
    const { result } = renderHook(() => useSearchCandidates())
    
    expect(result.current.candidates).toEqual([])
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('should search candidates successfully', async () => {
    const mockCandidates = [
      { id: '1', name: 'Candidate 1', party_name: 'Party A' },
      { id: '2', name: 'Candidate 2', party_name: 'Party B' },
    ]

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ 
        success: true, 
        data: { candidates: mockCandidates } 
      }),
    })

    const { result } = renderHook(() => useSearchCandidates())

    await act(async () => {
      await result.current.search('test')
    })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.candidates).toEqual(mockCandidates)
    expect(result.current.error).toBeNull()
  })

  it('should not search with empty query', async () => {
    const { result } = renderHook(() => useSearchCandidates())

    await act(async () => {
      await result.current.search('')
    })

    expect(result.current.candidates).toEqual([])
    expect(mockFetch).not.toHaveBeenCalled()
  })

  it('should not search with whitespace-only query', async () => {
    const { result } = renderHook(() => useSearchCandidates())

    await act(async () => {
      await result.current.search('   ')
    })

    expect(result.current.candidates).toEqual([])
    expect(mockFetch).not.toHaveBeenCalled()
  })

  it('should search with limit parameter', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ 
        success: true, 
        data: { candidates: [] } 
      }),
    })

    const { result } = renderHook(() => useSearchCandidates())

    await act(async () => {
      await result.current.search('test', 5)
    })

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('limit=5')
    )
  })

  it('should handle search API error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: false, error: 'Search failed' }),
    })

    const { result } = renderHook(() => useSearchCandidates())

    await act(async () => {
      await result.current.search('test')
    })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.candidates).toEqual([])
    expect(result.current.error).toBe('Search failed')
  })

  it('should handle network error during search', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => useSearchCandidates())

    await act(async () => {
      await result.current.search('test')
    })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBe('Error connecting to API')
  })

  it('should clear search results', async () => {
    const mockCandidates = [{ id: '1', name: 'Candidate 1' }]

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ 
        success: true, 
        data: { candidates: mockCandidates } 
      }),
    })

    const { result } = renderHook(() => useSearchCandidates())

    // First, search for candidates
    await act(async () => {
      await result.current.search('test')
    })

    await waitFor(() => {
      expect(result.current.candidates).toHaveLength(1)
    })

    // Then clear
    act(() => {
      result.current.clear()
    })

    expect(result.current.candidates).toEqual([])
    expect(result.current.error).toBeNull()
  })

  it('should encode search query properly', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ 
        success: true, 
        data: { candidates: [] } 
      }),
    })

    const { result } = renderHook(() => useSearchCandidates())

    await act(async () => {
      await result.current.search('test query with spaces')
    })

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('q=test%20query%20with%20spaces')
    )
  })
})
