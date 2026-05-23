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

  it('opens menu with profile links and navigates to dashboard', () => {
    mockUseSession.mockReturnValue({
      data: { user: { name: 'Sachin Shukla', image: '/avatar.png' } },
      status: 'authenticated',
    })

    render(<UserButton />)
    fireEvent.click(screen.getByRole('button', { name: /Sachin/i }))

    expect(screen.getByRole('menuitem', { name: 'Politicians' })).toHaveAttribute(
      'href',
      '/politicians',
    )
    const dashboardLink = screen.getByRole('menuitem', { name: 'Dashboard' })
    expect(dashboardLink).toHaveAttribute('href', '/dashboard')
    expect(screen.getByRole('menuitem', { name: 'Join Community' })).toHaveAttribute(
      'href',
      'https://chat.whatsapp.com/IceA98FSHHuDmXOwv8WH7v',
    )

    fireEvent.click(dashboardLink)
    expect(screen.queryByRole('menuitem', { name: 'Dashboard' })).not.toBeInTheDocument()
  })

  it('calls signOut when Sign Out is clicked', () => {
    mockUseSession.mockReturnValue({
      data: { user: { name: 'Sachin Shukla', image: '/avatar.png' } },
      status: 'authenticated',
    })

    render(<UserButton />)
    fireEvent.click(screen.getByRole('button', { name: /Sachin/i }))
    fireEvent.click(screen.getByRole('menuitem', { name: 'Sign Out' }))

    expect(signOut).toHaveBeenCalledWith({ callbackUrl: '/' })
  })
})
