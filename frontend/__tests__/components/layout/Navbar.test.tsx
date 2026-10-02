import { render, screen, fireEvent } from '@testing-library/react'
import Navbar from '@/components/layout/Navbar'

const trackEvent = jest.fn()

jest.mock('@/hooks/useAnalytics', () => ({
  useAnalytics: () => ({ trackEvent }),
}))

const SARANSH_URL = 'https://saransh-app.vercel.app'
const SARANSH_NAV_URL = `${SARANSH_URL}?utm_source=rajniti&utm_medium=referral&utm_campaign=saransh_cross_promo&utm_content=navbar`

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

  it('renders public nav links on every page', () => {
    render(<Navbar />)

    expect(screen.getByRole('link', { name: 'About' })).toHaveAttribute('href', '/#about')
    expect(screen.getByRole('link', { name: 'Contribute' })).toHaveAttribute(
      'href',
      '/#contribute',
    )
    expect(screen.queryByRole('link', { name: 'Politicians' })).not.toBeInTheDocument()
  })

  it('links to Saransh in a new tab with campaign attribution', () => {
    render(<Navbar />)

    const link = screen.getByRole('link', { name: /Saransh/i })
    expect(link).toHaveAttribute('href', SARANSH_NAV_URL)
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('fires nav_click and saransh_click once each on a Saransh click', () => {
    trackEvent.mockClear()
    render(<Navbar />)

    fireEvent.click(screen.getByRole('link', { name: /Saransh/i }))

    expect(trackEvent).toHaveBeenCalledTimes(2)
    expect(trackEvent).toHaveBeenCalledWith('nav_click', {
      link_text: 'Saransh',
      link_url: SARANSH_URL,
      nav_section: 'navbar',
    })
    expect(trackEvent).toHaveBeenCalledWith('saransh_click', {
      link_url: SARANSH_NAV_URL,
      page_location: 'navbar',
      placement: 'navbar',
    })
  })

  it('counts a middle-click on the Saransh link', () => {
    trackEvent.mockClear()
    render(<Navbar />)

    fireEvent(
      screen.getByRole('link', { name: /Saransh/i }),
      new MouseEvent('auxclick', { bubbles: true, cancelable: true, button: 1 })
    )

    expect(trackEvent).toHaveBeenCalledTimes(2)
    expect(trackEvent).toHaveBeenCalledWith('saransh_click', {
      link_url: SARANSH_NAV_URL,
      page_location: 'navbar',
      placement: 'navbar',
    })
  })

  it('does not fire saransh_click for other nav links', () => {
    trackEvent.mockClear()
    render(<Navbar />)

    fireEvent.click(screen.getByRole('link', { name: 'About' }))

    expect(trackEvent).toHaveBeenCalledTimes(1)
    expect(trackEvent).toHaveBeenCalledWith('nav_click', {
      link_text: 'About',
      link_url: '/#about',
      nav_section: 'navbar',
    })
  })

  it('applies sticky positioning when sticky prop is true', () => {
    render(<Navbar sticky />)

    const header = screen.getByRole('banner')
    expect(header).toHaveClass('sticky', 'top-0', 'relative', 'z-50')
  })
})
