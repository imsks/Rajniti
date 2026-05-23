import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { useSession } from 'next-auth/react'
import OnboardingPage from '@/app/onboarding/page'
import { userService } from '@/lib/api/user'

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
}))

jest.mock('@/hooks/useOnboardingCheck', () => ({
  useOnboardingCheck: jest.fn(() => ({
    sessionLoading: false,
    needsOnboarding: true,
    isOnboarded: false,
  })),
}))

jest.mock('@/hooks/useAnalytics', () => ({
  useAnalytics: () => ({ trackEvent: jest.fn() }),
}))

jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => (
      <div {...props}>{children}</div>
    ),
    button: ({
      children,
      onClick,
      disabled,
      ...props
    }: React.PropsWithChildren<
      Record<string, unknown> & { onClick?: () => void; disabled?: boolean }
    >) => (
      <button type="button" onClick={onClick} disabled={disabled} {...props}>
        {children}
      </button>
    ),
  },
  AnimatePresence: ({ children }: React.PropsWithChildren) => <>{children}</>,
}))

jest.mock('@/components/onboarding/PoliticalInclinationStep', () => ({
  __esModule: true,
  default: ({ onChange }: { onChange: (value: string) => void }) => (
    <button type="button" onClick={() => onChange('Neutral')}>
      Pick ideology
    </button>
  ),
}))

jest.mock('@/components/onboarding/UserDetailsStep', () => ({
  __esModule: true,
  default: ({
    onChange,
  }: {
    onChange: (field: string, value: string) => void
  }) => (
    <button
      type="button"
      onClick={() => {
        onChange('state', 'DL')
        onChange('age_group', '25-35')
      }}
    >
      Fill details
    </button>
  ),
}))

jest.mock('@/components/onboarding/PreferencesStep', () => ({
  __esModule: true,
  default: () => <div>Preferences</div>,
}))

jest.mock('@/components/onboarding/UsernameStep', () => ({
  __esModule: true,
  default: ({
    onChange,
    onValidation,
  }: {
    onChange: (value: string) => void
    onValidation: (valid: boolean) => void
  }) => (
    <button
      type="button"
      onClick={() => {
        onChange('testuser')
        onValidation(true)
      }}
    >
      Set username
    </button>
  ),
}))

jest.mock('@/lib/api/user', () => ({
  userService: {
    updateUser: jest.fn(),
  },
}))

const mockUpdate = jest.fn()

beforeEach(() => {
  jest.clearAllMocks()
  mockUpdate.mockResolvedValue(undefined)
  ;(useSession as jest.Mock).mockReturnValue({
    status: 'authenticated',
    data: { user: { id: 'user-1', onboardingCompleted: false } },
    update: mockUpdate,
  })
  ;(userService.updateUser as jest.Mock).mockResolvedValue({
    success: true,
    data: { onboarding_completed: true },
  })
  delete (window as Window & { location?: Location }).location
  window.location = { href: '' } as Location
})

async function completeAllSteps() {
  fireEvent.click(screen.getByRole('button', { name: 'Pick ideology' }))
  fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
  fireEvent.click(screen.getByRole('button', { name: 'Fill details' }))
  fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
  fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
  fireEvent.click(screen.getByRole('button', { name: 'Set username' }))
}

describe('OnboardingPage', () => {
  it('submits onboarding with onboarding_completed true and updates session', async () => {
    render(<OnboardingPage />)

    await completeAllSteps()

    fireEvent.click(
      screen.getByRole('button', { name: /complete onboarding/i })
    )

    await waitFor(() => {
      expect(userService.updateUser).toHaveBeenCalledWith(
        'user-1',
        expect.objectContaining({
          onboarding_completed: true,
          username: 'testuser',
          state: 'DL',
        })
      )
    })

    await waitFor(() => {
      expect(mockUpdate).toHaveBeenCalledWith({ onboardingCompleted: true })
    })

    expect(window.location.href).toBe('/dashboard')
  })
})
