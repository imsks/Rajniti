/**
 * Integration tests for onboarding gating — real useOnboardingCheck + OnboardingGate
 * with mocked session, router, and backend user API.
 */
import { render, screen, waitFor } from '@testing-library/react'
import { usePathname, useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import OnboardingGate from '@/components/auth/OnboardingGate'
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

function mockAuthenticatedSession(onboardingCompleted = false) {
  ;(useSession as jest.Mock).mockReturnValue({
    status: 'authenticated',
    data: {
      user: { id: 'user-1', onboardingCompleted },
    },
    update: mockUpdate,
  })
}

beforeEach(() => {
  jest.clearAllMocks()
  ;(useRouter as jest.Mock).mockReturnValue({ replace: mockReplace })
  mockUpdate.mockResolvedValue(undefined)
})

describe('onboarding gating integration', () => {
  it('incomplete user on dashboard redirects to onboarding', async () => {
    ;(usePathname as jest.Mock).mockReturnValue(ROUTES.dashboard)
    mockAuthenticatedSession(false)
    ;(userService.getUser as jest.Mock).mockResolvedValue({
      data: { onboarding_completed: false },
    })

    render(
      <OnboardingGate
        fallback={<div data-testid="gate-loading">Loading</div>}
      >
        <div data-testid="protected-content">Protected</div>
      </OnboardingGate>
    )

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith(ROUTES.onboarding)
    })
    expect(screen.getByTestId('gate-loading')).toBeInTheDocument()
    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()
  })

  it('complete user on dashboard stays on dashboard', async () => {
    ;(usePathname as jest.Mock).mockReturnValue(ROUTES.dashboard)
    mockAuthenticatedSession(true)
    ;(userService.getUser as jest.Mock).mockResolvedValue({
      data: { onboarding_completed: true },
    })

    render(
      <OnboardingGate
        fallback={<div data-testid="gate-loading">Loading</div>}
      >
        <div data-testid="protected-content">Protected</div>
      </OnboardingGate>
    )

    await waitFor(() => {
      expect(screen.getByTestId('protected-content')).toBeInTheDocument()
    })
    expect(mockReplace).not.toHaveBeenCalled()
  })

  it('incomplete user on onboarding stays on onboarding', async () => {
    ;(usePathname as jest.Mock).mockReturnValue(ROUTES.onboarding)
    mockAuthenticatedSession(false)
    ;(userService.getUser as jest.Mock).mockResolvedValue({
      data: { onboarding_completed: false },
    })

    render(
      <OnboardingGate
        redirectIfIncomplete={false}
        redirectIfComplete
        blockUntilReady={false}
        fallback={<div data-testid="gate-loading">Loading</div>}
      >
        <div data-testid="onboarding-wizard">Wizard</div>
      </OnboardingGate>
    )

    await waitFor(() => {
      expect(screen.getByTestId('onboarding-wizard')).toBeInTheDocument()
    })
    expect(mockReplace).not.toHaveBeenCalled()
  })

  it('complete user on onboarding redirects to dashboard', async () => {
    ;(usePathname as jest.Mock).mockReturnValue(ROUTES.onboarding)
    mockAuthenticatedSession(true)
    ;(userService.getUser as jest.Mock).mockResolvedValue({
      data: { onboarding_completed: true },
    })

    render(
      <OnboardingGate
        redirectIfIncomplete={false}
        redirectIfComplete
        blockUntilReady={false}
        fallback={<div data-testid="gate-loading">Loading</div>}
      >
        <div data-testid="onboarding-wizard">Wizard</div>
      </OnboardingGate>
    )

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith(ROUTES.dashboard)
    })
  })
})
