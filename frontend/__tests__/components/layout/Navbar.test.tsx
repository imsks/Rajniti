import { render, screen } from '@testing-library/react'
import Navbar from '@/components/layout/Navbar'

jest.mock('@/hooks/useAnalytics', () => ({
  useAnalytics: () => ({ trackEvent: jest.fn() }),
}))

jest.mock('@/components/auth/UserButton', () => {
  return function MockUserButton() {
    return <div data-testid="user-button" />
  }
})

jest.mock('@/components/ui/ThemeToggle', () => {
  return function MockThemeToggle() {
    return <div data-testid="theme-toggle" />
  }
})

describe('Navbar', () => {
  it('renders header above page content with z-50 stacking', () => {
    render(
      <>
        <Navbar />
        <section data-testid="hero" className="relative z-2">
          Hero content
        </section>
      </>
    )

    const header = screen.getByRole('banner')
    expect(header).toHaveClass('relative', 'z-50')
    expect(screen.getByTestId('hero')).toBeInTheDocument()
  })

  it('renders primary nav links on every page', () => {
    render(<Navbar />)

    expect(screen.getByRole('link', { name: 'Politicians' })).toHaveAttribute(
      'href',
      '/politicians',
    )
    expect(screen.getByRole('link', { name: 'Dashboard' })).toHaveAttribute(
      'href',
      '/dashboard',
    )
  })

  it('applies sticky positioning when sticky prop is true', () => {
    render(<Navbar sticky />)

    const header = screen.getByRole('banner')
    expect(header).toHaveClass('sticky', 'top-0', 'relative', 'z-50')
  })
})
