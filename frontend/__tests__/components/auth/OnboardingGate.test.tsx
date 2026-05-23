import { render, screen } from '@testing-library/react'
import OnboardingGate from '@/components/auth/OnboardingGate'
import { useOnboardingCheck } from '@/hooks/useOnboardingCheck'

jest.mock('@/hooks/useOnboardingCheck', () => ({
  useOnboardingCheck: jest.fn(),
}))

const mockUseOnboardingCheck = useOnboardingCheck as jest.Mock

describe('OnboardingGate', () => {
  it('shows fallback while session is loading', () => {
    mockUseOnboardingCheck.mockReturnValue({
      sessionLoading: true,
      needsOnboarding: false,
      isOnboarded: false,
    })

    render(
      <OnboardingGate fallback={<div data-testid="loading">Loading</div>}>
        <div data-testid="content">Dashboard</div>
      </OnboardingGate>
    )

    expect(screen.getByTestId('loading')).toBeInTheDocument()
    expect(screen.queryByTestId('content')).not.toBeInTheDocument()
  })

  it('blocks children when user needs onboarding', () => {
    mockUseOnboardingCheck.mockReturnValue({
      sessionLoading: false,
      needsOnboarding: true,
      isOnboarded: false,
    })

    render(
      <OnboardingGate fallback={<div data-testid="loading">Loading</div>}>
        <div data-testid="content">Dashboard</div>
      </OnboardingGate>
    )

    expect(screen.getByTestId('loading')).toBeInTheDocument()
    expect(screen.queryByTestId('content')).not.toBeInTheDocument()
  })

  it('renders children when onboarded', () => {
    mockUseOnboardingCheck.mockReturnValue({
      sessionLoading: false,
      needsOnboarding: false,
      isOnboarded: true,
    })

    render(
      <OnboardingGate>
        <div data-testid="content">Dashboard</div>
      </OnboardingGate>
    )

    expect(screen.getByTestId('content')).toBeInTheDocument()
  })

  it('allows incomplete users through when blockUntilReady is false', () => {
    mockUseOnboardingCheck.mockReturnValue({
      sessionLoading: false,
      needsOnboarding: true,
      isOnboarded: false,
    })

    render(
      <OnboardingGate blockUntilReady={false}>
        <div data-testid="content">Onboarding wizard</div>
      </OnboardingGate>
    )

    expect(screen.getByTestId('content')).toBeInTheDocument()
  })

  it('passes redirect options to useOnboardingCheck', () => {
    mockUseOnboardingCheck.mockReturnValue({
      sessionLoading: false,
      needsOnboarding: false,
      isOnboarded: true,
    })

    render(
      <OnboardingGate redirectIfIncomplete={false} redirectIfComplete>
        <div>Onboarding</div>
      </OnboardingGate>
    )

    expect(mockUseOnboardingCheck).toHaveBeenCalledWith({
      redirectIfIncomplete: false,
      redirectIfComplete: true,
    })
  })
})
