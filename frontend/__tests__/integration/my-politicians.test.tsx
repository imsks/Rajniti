import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { useSession } from 'next-auth/react'
import MyPoliticiansSection from '@/components/MyPoliticiansSection'
import { mockMp, mockPoliticianList } from '@/__tests__/helpers/politicianFixtures'

jest.mock('@/hooks/useAnalytics', () => ({
  useAnalytics: () => ({
    trackEvent: jest.fn(),
    trackSearch: jest.fn(),
  }),
}))

jest.mock('@/lib/locationPincode', () => ({
  getCurrentPosition: jest.fn(),
  getPincodeFromCoords: jest.fn(),
  buildGoogleSearchUrlForMlaMp: jest.fn(
    (pincode: string) => `https://google.test/search?q=${pincode}`,
  ),
}))

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
}))

const mockUseSession = useSession as jest.Mock

type SavedPolitician = { politician_id: string; role: string }

function createFetchRouter(initialSaved: SavedPolitician[] = []) {
  const saved = [...initialSaved]

  return (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input)
    const method = init?.method ?? 'GET'

    if (url.includes('/politicians/search')) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            success: true,
            data: { politicians: [mockMp] },
          }),
      })
    }

    if (url.includes('/users/user-1/politicians') && method === 'GET') {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            success: true,
            data: saved,
          }),
      })
    }

    if (url.includes('/users/user-1/politicians') && method === 'POST') {
      const body = JSON.parse(String(init?.body))
      saved.push({
        politician_id: body.politician_id,
        role: body.role,
      })
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      })
    }

    if (url.includes('/users/user-1/politicians/') && method === 'DELETE') {
      const politicianId = url.split('/').pop()
      const index = saved.findIndex((item) => item.politician_id === politicianId)
      if (index >= 0) saved.splice(index, 1)
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      })
    }

    if (url.includes('/politicians/')) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            success: true,
            data: mockMp,
          }),
      })
    }

    return Promise.reject(new Error(`unexpected url: ${url}`))
  }
}

beforeEach(() => {
  jest.useFakeTimers({ advanceTimers: true })
  window.localStorage.clear()

  mockUseSession.mockReturnValue({
    data: { user: { id: 'user-1' } },
    status: 'authenticated',
  })
})

afterEach(() => {
  jest.useRealTimers()
})

describe('my politicians integration', () => {
  it('adds MP via search and updates section heading', async () => {
    ;(global.fetch as jest.Mock).mockImplementation(createFetchRouter())

    render(<MyPoliticiansSection allPoliticians={mockPoliticianList} />)

    expect(
      screen.getByRole('heading', { name: 'Add Your Local Politicians' }),
    ).toBeInTheDocument()

    const input = screen.getByPlaceholderText('Find your MP or MLA, e.g. Modi')
    fireEvent.change(input, { target: { value: 'Modi' } })

    await act(async () => {
      jest.advanceTimersByTime(1600)
    })

    await waitFor(() => {
      expect(screen.getByText('Narendra Modi')).toBeInTheDocument()
    })

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Narendra Modi/i }))
    })

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Your Politicians' }),
      ).toBeInTheDocument()
      expect(screen.getAllByText('Narendra Modi').length).toBeGreaterThanOrEqual(1)
    })

    const postCall = (global.fetch as jest.Mock).mock.calls.find(
      ([url, opts]: [string, RequestInit | undefined]) =>
        String(url).includes('/users/user-1/politicians') && opts?.method === 'POST',
    )
    expect(postCall).toBeTruthy()
  })

  it('removes MP and restores placeholder', async () => {
    ;(global.fetch as jest.Mock).mockImplementation(
      createFetchRouter([{ politician_id: 'mp-1', role: 'MP' }]),
    )

    render(<MyPoliticiansSection allPoliticians={mockPoliticianList} />)

    await waitFor(() => {
      expect(screen.getByText('Narendra Modi')).toBeInTheDocument()
    })

    const removeButton = screen.getAllByRole('button', {
      name: 'Remove from your politicians',
    })[0]

    await act(async () => {
      fireEvent.click(removeButton)
    })

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Add Your Local Politicians' }),
      ).toBeInTheDocument()
      expect(screen.getAllByText('Search above to add')).toHaveLength(2)
    })

    const deleteCall = (global.fetch as jest.Mock).mock.calls.find(
      ([url, opts]: [string, RequestInit | undefined]) =>
        String(url).includes('/users/user-1/politicians/mp-1') &&
        opts?.method === 'DELETE',
    )
    expect(deleteCall).toBeTruthy()
  })

  it('shows search error when fetch rejects', async () => {
    ;(global.fetch as jest.Mock).mockImplementation((url: string) => {
      if (String(url).includes('/politicians/search')) {
        return Promise.reject(new Error('network'))
      }
      if (String(url).includes('/users/user-1/politicians')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ success: true, data: [] }),
        })
      }
      return Promise.reject(new Error(`unexpected url: ${url}`))
    })

    render(<MyPoliticiansSection allPoliticians={mockPoliticianList} />)

    fireEvent.change(
      screen.getByPlaceholderText('Find your MP or MLA, e.g. Modi'),
      { target: { value: 'ab' } },
    )

    await act(async () => {
      jest.advanceTimersByTime(1600)
    })

    await waitFor(() => {
      expect(screen.getByText('Search failed')).toBeInTheDocument()
    })
  })

  it('hydrates MP from backend on mount', async () => {
    ;(global.fetch as jest.Mock).mockImplementation(
      createFetchRouter([{ politician_id: 'mp-1', role: 'MP' }]),
    )

    render(<MyPoliticiansSection allPoliticians={mockPoliticianList} />)

    await waitFor(() => {
      expect(screen.getByText('Narendra Modi')).toBeInTheDocument()
      expect(
        screen.getByRole('heading', { name: 'Your Politicians' }),
      ).toBeInTheDocument()
    })
  })

  it('shows empty state when backend fetch fails on mount', async () => {
    ;(global.fetch as jest.Mock).mockImplementation((url: string) => {
      if (String(url).includes('/users/user-1/politicians')) {
        return Promise.resolve({
          ok: false,
          status: 500,
          json: () =>
            Promise.resolve({
              success: false,
              error: 'Failed to fetch politicians',
            }),
        })
      }
      return Promise.reject(new Error(`unexpected url: ${url}`))
    })

    render(<MyPoliticiansSection allPoliticians={mockPoliticianList} />)

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Add Your Local Politicians' }),
      ).toBeInTheDocument()
    })
  })
})
