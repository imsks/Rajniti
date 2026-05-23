import { fireEvent, render, screen } from '@testing-library/react'
import { useSession, signIn, signOut } from 'next-auth/react'
import UserButton from '@/components/auth/UserButton'

jest.mock('@/hooks/useAnalytics', () => ({
  useAnalytics: () => ({ trackEvent: jest.fn() }),
}))

const mockUseSession = useSession as jest.Mock

describe('UserButton', () => {
  it('shows Sign In when unauthenticated', () => {
    mockUseSession.mockReturnValue({ data: null, status: 'unauthenticated' })

    render(<UserButton />)

    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument()
  })

  it('calls signIn when Sign In is clicked', () => {
    mockUseSession.mockReturnValue({ data: null, status: 'unauthenticated' })

    render(<UserButton />)
    fireEvent.click(screen.getByRole('button', { name: 'Sign In' }))

    expect(signIn).toHaveBeenCalled()
  })

  it('opens menu and navigates to dashboard from Dashboard link', () => {
    mockUseSession.mockReturnValue({
      data: { user: { name: 'Sachin Shukla', image: '/avatar.png' } },
      status: 'authenticated',
    })

    render(<UserButton />)
    fireEvent.click(screen.getByRole('button', { name: /Sachin/i }))

    const dashboardLink = screen.getByRole('link', { name: 'Dashboard' })
    expect(dashboardLink).toHaveAttribute('href', '/dashboard')

    fireEvent.click(dashboardLink)
    expect(screen.queryByRole('link', { name: 'Dashboard' })).not.toBeInTheDocument()
  })

  it('calls signOut when Sign Out is clicked', () => {
    mockUseSession.mockReturnValue({
      data: { user: { name: 'Sachin Shukla', image: '/avatar.png' } },
      status: 'authenticated',
    })

    render(<UserButton />)
    fireEvent.click(screen.getByRole('button', { name: /Sachin/i }))
    fireEvent.click(screen.getByRole('button', { name: 'Sign Out' }))

    expect(signOut).toHaveBeenCalledWith({ callbackUrl: '/' })
  })
})
