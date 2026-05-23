import { renderHook, waitFor } from '@testing-library/react'
import { usePathname, useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { useOnboardingCheck } from '@/hooks/useOnboardingCheck'
import { userService } from '@/lib/api/user'
import { ROUTES } from '@/lib/routes'

jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
  useRouter: jest.fn(),
}))

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
}))

jest.mock('@/lib/api/user', () => ({
  userService: {
    getUser: jest.fn(),
  },
}))

const mockReplace = jest.fn()
const mockUpdate = jest.fn()

beforeEach(() => {
  jest.clearAllMocks()
  ;(useRouter as jest.Mock).mockReturnValue({ replace: mockReplace })
  mockUpdate.mockResolvedValue(undefined)
  ;(useSession as jest.Mock).mockReturnValue({
    status: 'authenticated',
    data: { user: { id: 'user-1', onboardingCompleted: false } },
    update: mockUpdate,
  })
})

describe('useOnboardingCheck', () => {
  it('does not fetch or redirect when unauthenticated', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      status: 'unauthenticated',
      data: null,
      update: mockUpdate,
    })
    ;(usePathname as jest.Mock).mockReturnValue(ROUTES.dashboard)

    renderHook(() => useOnboardingCheck())

    await waitFor(() => {
      expect(userService.getUser).not.toHaveBeenCalled()
    })
    expect(mockReplace).not.toHaveBeenCalled()
  })

  it('shows loading while backend check is in progress', async () => {
    ;(usePathname as jest.Mock).mockReturnValue(ROUTES.dashboard)
    ;(userService.getUser as jest.Mock).mockImplementation(
      () => new Promise(() => {})
    )

    const { result } = renderHook(() => useOnboardingCheck())

    expect(result.current.sessionLoading).toBe(true)
  })

  it('redirects to onboarding when backend reports incomplete profile', async () => {
    ;(usePathname as jest.Mock).mockReturnValue(ROUTES.dashboard)
    ;(userService.getUser as jest.Mock).mockResolvedValue({
      data: { onboarding_completed: false },
    })

    renderHook(() => useOnboardingCheck())

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith(ROUTES.onboarding)
    })
  })

  it('does not redirect when backend reports onboarding complete', async () => {
    ;(usePathname as jest.Mock).mockReturnValue(ROUTES.dashboard)
    ;(userService.getUser as jest.Mock).mockResolvedValue({
      data: { onboarding_completed: true },
    })

    const { result } = renderHook(() => useOnboardingCheck())

    await waitFor(() => {
      expect(result.current.isOnboarded).toBe(true)
    })
    expect(mockReplace).not.toHaveBeenCalled()
  })

  it('syncs session when backend is ahead of JWT', async () => {
    ;(usePathname as jest.Mock).mockReturnValue(ROUTES.dashboard)
    ;(userService.getUser as jest.Mock).mockResolvedValue({
      data: { onboarding_completed: true },
    })

    renderHook(() => useOnboardingCheck())

    await waitFor(() => {
      expect(mockUpdate).toHaveBeenCalledWith({ onboardingCompleted: true })
    })
  })

  it('redirects completed users away from onboarding', async () => {
    ;(usePathname as jest.Mock).mockReturnValue(ROUTES.onboarding)
    ;(userService.getUser as jest.Mock).mockResolvedValue({
      data: { onboarding_completed: true },
    })

    renderHook(() =>
      useOnboardingCheck({
        redirectIfIncomplete: false,
        redirectIfComplete: true,
      })
    )

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith(ROUTES.dashboard)
    })
  })

  it('does not redirect incomplete users already on onboarding', async () => {
    ;(usePathname as jest.Mock).mockReturnValue(ROUTES.onboarding)
    ;(userService.getUser as jest.Mock).mockResolvedValue({
      data: { onboarding_completed: false },
    })

    const { result } = renderHook(() => useOnboardingCheck())

    await waitFor(() => {
      expect(result.current.needsOnboarding).toBe(true)
    })
    expect(mockReplace).not.toHaveBeenCalled()
  })

  it('falls back to JWT when backend fetch fails', async () => {
    ;(usePathname as jest.Mock).mockReturnValue(ROUTES.dashboard)
    ;(useSession as jest.Mock).mockReturnValue({
      status: 'authenticated',
      data: { user: { id: 'user-1', onboardingCompleted: true } },
      update: mockUpdate,
    })
    ;(userService.getUser as jest.Mock).mockRejectedValue(new Error('network'))

    const { result } = renderHook(() => useOnboardingCheck())

    await waitFor(() => {
      expect(result.current.isOnboarded).toBe(true)
    })
    expect(mockReplace).not.toHaveBeenCalled()
  })
})
