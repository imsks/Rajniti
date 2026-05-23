import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { useSession } from 'next-auth/react'
import MyPoliticiansSection from '@/components/MyPoliticiansSection'
import { useMyPoliticians } from '@/hooks/useMyPoliticians'
import { usePoliticianSearch } from '@/hooks/usePoliticianSearch'
import { userService } from '@/lib/api/user'
import {
  getCurrentPosition,
  getPincodeFromCoords,
} from '@/lib/locationPincode'
import { mockMp, mockMla, mockPoliticianList } from '@/__tests__/helpers/politicianFixtures'

jest.mock('framer-motion', () => ({
  motion: {
    section: ({
      children,
      ...props
    }: React.PropsWithChildren<Record<string, unknown>>) => (
      <section {...props}>{children}</section>
    ),
    div: ({
      children,
      ...props
    }: React.PropsWithChildren<Record<string, unknown>>) => (
      <div {...props}>{children}</div>
    ),
  },
}))

jest.mock('@/hooks/useAnalytics', () => ({
  useAnalytics: () => ({
    trackEvent: jest.fn(),
    trackSearch: jest.fn(),
  }),
}))

jest.mock('@/hooks/useMyPoliticians')
jest.mock('@/hooks/usePoliticianSearch')

jest.mock('@/lib/locationPincode', () => ({
  getCurrentPosition: jest.fn(),
  getPincodeFromCoords: jest.fn(),
  buildGoogleSearchUrlForMlaMp: jest.fn(
    (pincode: string) => `https://google.test/search?q=${pincode}`,
  ),
}))

jest.mock('@/lib/api/user', () => ({
  userService: {
    addUserPolitician: jest.fn(),
    removeUserPolitician: jest.fn(),
  },
}))

const mockUseSession = useSession as jest.Mock
const mockUseMyPoliticians = useMyPoliticians as jest.Mock
const mockUsePoliticianSearch = usePoliticianSearch as jest.Mock
const mockAddUserPolitician = userService.addUserPolitician as jest.Mock
const mockRemoveUserPolitician = userService.removeUserPolitician as jest.Mock
const mockGetCurrentPosition = getCurrentPosition as jest.Mock
const mockGetPincodeFromCoords = getPincodeFromCoords as jest.Mock

function setupEmptyPoliticians() {
  const setMyMP = jest.fn()
  const setMyMLA = jest.fn()

  mockUseMyPoliticians.mockReturnValue({
    myMP: null,
    myMLA: null,
    setMyMP,
    setMyMLA,
  })

  return { setMyMP, setMyMLA }
}

function setupPopulatedPoliticians() {
  const setMyMP = jest.fn()
  const setMyMLA = jest.fn()

  mockUseMyPoliticians.mockReturnValue({
    myMP: mockMp,
    myMLA: mockMla,
    setMyMP,
    setMyMLA,
  })

  return { setMyMP, setMyMLA }
}

beforeEach(() => {
  jest.clearAllMocks()

  mockUseSession.mockReturnValue({
    data: { user: { id: 'user-1' } },
    status: 'authenticated',
  })

  mockUsePoliticianSearch.mockReturnValue({
    results: [],
    loading: false,
    error: null,
  })

  mockAddUserPolitician.mockResolvedValue({ success: true })
  mockRemoveUserPolitician.mockResolvedValue({ success: true })
})

describe('MyPoliticiansSection', () => {
  it('shows empty state with Add Your Local Politicians heading', () => {
    setupEmptyPoliticians()

    render(<MyPoliticiansSection allPoliticians={mockPoliticianList} />)

    expect(
      screen.getByRole('heading', { name: 'Add Your Local Politicians' }),
    ).toBeInTheDocument()
    expect(
      screen.getByText('Track their performance and know their progress'),
    ).toBeInTheDocument()
    expect(screen.getByText('Your MP')).toBeInTheDocument()
    expect(screen.getByText('Your MLA')).toBeInTheDocument()
    expect(screen.getAllByText('Search above to add')).toHaveLength(2)
  })

  it('shows populated state with Your Politicians heading', () => {
    setupPopulatedPoliticians()

    render(<MyPoliticiansSection allPoliticians={mockPoliticianList} />)

    expect(
      screen.getByRole('heading', { name: 'Your Politicians' }),
    ).toBeInTheDocument()
    expect(screen.getByText('Narendra Modi')).toBeInTheDocument()
    expect(screen.getByText('Example MLA')).toBeInTheDocument()
  })

  it('shows search dropdown with results when query is long enough', () => {
    setupEmptyPoliticians()
    mockUsePoliticianSearch.mockReturnValue({
      results: [mockMp],
      loading: false,
      error: null,
    })

    render(<MyPoliticiansSection allPoliticians={mockPoliticianList} />)

    const input = screen.getByPlaceholderText('Find your MP or MLA, e.g. Modi')
    fireEvent.change(input, { target: { value: 'Mod' } })

    expect(screen.getByText('Narendra Modi')).toBeInTheDocument()
    expect(screen.getByText(/MP · Varanasi/)).toBeInTheDocument()
  })

  it('selects a search result and calls addUserPolitician', async () => {
    const { setMyMP } = setupEmptyPoliticians()
    mockUsePoliticianSearch.mockReturnValue({
      results: [mockMp],
      loading: false,
      error: null,
    })

    render(<MyPoliticiansSection allPoliticians={mockPoliticianList} />)

    const input = screen.getByPlaceholderText('Find your MP or MLA, e.g. Modi')
    fireEvent.change(input, { target: { value: 'Modi' } })

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Narendra Modi/i }))
    })

    await waitFor(() => {
      expect(mockAddUserPolitician).toHaveBeenCalledWith('user-1', 'mp-1', 'MP')
      expect(setMyMP).toHaveBeenCalledWith(mockMp)
    })
  })

  it('shows not found message when search returns no results', () => {
    setupEmptyPoliticians()
    mockUsePoliticianSearch.mockReturnValue({
      results: [],
      loading: false,
      error: null,
    })

    render(<MyPoliticiansSection allPoliticians={mockPoliticianList} />)

    fireEvent.change(
      screen.getByPlaceholderText('Find your MP or MLA, e.g. Modi'),
      { target: { value: 'xyz' } },
    )

    expect(
      screen.getByText(/Not found\? Some MLAs may not be in our dataset yet/),
    ).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Request addition/i })).toBeInTheDocument()
  })

  it('shows search error in dropdown', () => {
    setupEmptyPoliticians()
    mockUsePoliticianSearch.mockReturnValue({
      results: [],
      loading: false,
      error: 'Search failed',
    })

    render(<MyPoliticiansSection allPoliticians={mockPoliticianList} />)

    fireEvent.change(
      screen.getByPlaceholderText('Find your MP or MLA, e.g. Modi'),
      { target: { value: 'ab' } },
    )

    expect(screen.getByText('Search failed')).toBeInTheDocument()
  })

  it('removes MP when remove button is clicked', async () => {
    const { setMyMP } = setupPopulatedPoliticians()

    render(<MyPoliticiansSection allPoliticians={mockPoliticianList} />)

    const removeButtons = screen.getAllByRole('button', {
      name: 'Remove from your politicians',
    })

    await act(async () => {
      fireEvent.click(removeButtons[0])
    })

    await waitFor(() => {
      expect(mockRemoveUserPolitician).toHaveBeenCalledWith('user-1', 'mp-1')
      expect(setMyMP).toHaveBeenCalledWith(null)
    })
  })

  it('focuses search when placeholder Add button is clicked', () => {
    setupEmptyPoliticians()

    render(<MyPoliticiansSection allPoliticians={mockPoliticianList} />)

    const searchInput = screen.getByPlaceholderText(
      'Find your MP or MLA, e.g. Modi',
    )
    const addButtons = screen.getAllByRole('button', { name: '+ Add' })

    fireEvent.click(addButtons[0])

    expect(document.activeElement).toBe(searchInput)
  })

  it('shows pincode fallback when location lookup fails', async () => {
    setupEmptyPoliticians()
    mockGetCurrentPosition.mockResolvedValue(null)

    render(<MyPoliticiansSection allPoliticians={mockPoliticianList} />)

    await act(async () => {
      fireEvent.click(
        screen.getByRole('button', { name: 'Use location to find by pincode' }),
      )
    })

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter pincode')).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Search on Google' }),
      ).toBeInTheDocument()
    })
  })

  it('shows pincode fallback when geolocation succeeds but reverse geocode fails', async () => {
    setupEmptyPoliticians()
    mockGetCurrentPosition.mockResolvedValue({ lat: 28.6, lon: 77.2 })
    mockGetPincodeFromCoords.mockResolvedValue(null)

    render(<MyPoliticiansSection allPoliticians={mockPoliticianList} />)

    await act(async () => {
      fireEvent.click(
        screen.getByRole('button', { name: 'Use location to find by pincode' }),
      )
    })

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter pincode')).toBeInTheDocument()
    })
  })
})
