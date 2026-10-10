import { fireEvent, render, screen, within } from '@testing-library/react'
import Navbar from '@/components/layout/Navbar'

const trackEvent = jest.fn()

jest.mock('@/hooks/useAnalytics', () => ({
  useAnalytics: () => ({ trackEvent }),
}))

const SARANSH_URL = 'https://saransh-app.vercel.app'
const SARANSH_NAV_URL = `${SARANSH_URL}?utm_source=rajniti&utm_medium=referral&utm_campaign=saransh_cross_promo&utm_content=navbar`
const SARANSH_MOBILE_URL = `${SARANSH_URL}?utm_source=rajniti&utm_medium=referral&utm_campaign=saransh_cross_promo&utm_content=navbar_mobile`

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
  beforeEach(() => {
    trackEvent.mockClear()
  })

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

describe('Navbar mobile menu', () => {
  const openMenu = () => {
    fireEvent.click(screen.getByRole('button', { name: 'Open menu' }))
    return screen.getByRole('button', { name: 'Close menu' })
  }

  beforeEach(() => {
    trackEvent.mockClear()
  })

  it('renders a closed, labelled menu button by default', () => {
    render(<Navbar />)

    const button = screen.getByRole('button', { name: 'Open menu' })
    expect(button).toHaveAttribute('aria-expanded', 'false')
    expect(screen.queryByRole('navigation', { name: 'Mobile' })).not.toBeInTheDocument()
  })

  it('opens the menu with every NAV_LINKS entry and toggles aria-expanded', () => {
    render(<Navbar />)
    const button = openMenu()

    expect(button).toHaveAttribute('aria-expanded', 'true')
    expect(button).toHaveAttribute('aria-controls', screen.getByRole('navigation', { name: 'Mobile' }).parentElement?.id)

    const menu = screen.getByRole('navigation', { name: 'Mobile' })
    const labels = Array.from(menu.querySelectorAll('a')).map((a) => a.textContent)
    expect(labels).toEqual(['About', 'Contribute', 'Saransh', 'Found a Bug?'])
  })

  it('fires mobile_menu_toggle once per tap of the menu button', () => {
    render(<Navbar />)

    const button = openMenu()
    expect(trackEvent).toHaveBeenCalledWith('mobile_menu_toggle', { action: 'open' })
    expect(trackEvent).toHaveBeenCalledTimes(1)

    fireEvent.click(button)
    expect(trackEvent).toHaveBeenCalledWith('mobile_menu_toggle', { action: 'close' })
    expect(trackEvent).toHaveBeenCalledTimes(2)
  })

  it('closes on Escape and returns focus to the menu button', () => {
    render(<Navbar />)
    const button = openMenu()

    fireEvent.keyDown(document, { key: 'Escape' })

    expect(screen.queryByRole('navigation', { name: 'Mobile' })).not.toBeInTheDocument()
    expect(button).toHaveFocus()
    expect(trackEvent).toHaveBeenCalledTimes(1)
  })

  it('closes when a tap lands outside the menu', () => {
    render(<Navbar />)
    openMenu()

    fireEvent.pointerDown(document.body)

    expect(screen.queryByRole('navigation', { name: 'Mobile' })).not.toBeInTheDocument()
  })

  it('fires nav_click with navbar_mobile and closes on link click', () => {
    render(<Navbar />)
    openMenu()

    const menu = screen.getByRole('navigation', { name: 'Mobile' })
    fireEvent.click(within(menu).getByRole('link', { name: 'About' }))

    expect(trackEvent).toHaveBeenCalledWith('nav_click', {
      link_text: 'About',
      link_url: '/#about',
      nav_section: 'navbar_mobile',
    })
    expect(trackEvent).toHaveBeenCalledTimes(2)
    expect(menu).not.toBeInTheDocument()
  })

  it('fires saransh_click with placement navbar_mobile and a UTM-tagged url', () => {
    render(<Navbar />)
    openMenu()

    const menu = screen.getByRole('navigation', { name: 'Mobile' })
    const saransh = within(menu).getByRole('link', { name: /Saransh/i })

    expect(saransh).toHaveAttribute('href', SARANSH_MOBILE_URL)
    expect(saransh).toHaveAttribute('target', '_blank')
    expect(saransh).toHaveAttribute('rel', 'noopener noreferrer')

    fireEvent.click(saransh)

    expect(trackEvent).toHaveBeenCalledWith('nav_click', {
      link_text: 'Saransh',
      link_url: SARANSH_URL,
      nav_section: 'navbar_mobile',
    })
    expect(trackEvent).toHaveBeenCalledWith('saransh_click', {
      link_url: SARANSH_MOBILE_URL,
      page_location: 'navbar_mobile',
      placement: 'navbar_mobile',
    })
    expect(trackEvent).toHaveBeenCalledTimes(3)
  })

  it('keeps contribute_click for the bug link inside the mobile menu', () => {
    render(<Navbar />)
    openMenu()

    const menu = screen.getByRole('navigation', { name: 'Mobile' })
    fireEvent.click(within(menu).getByRole('link', { name: 'Found a Bug?' }))

    expect(trackEvent).toHaveBeenCalledWith('contribute_click', {
      contribute_type: 'bug',
      page_location: 'navbar_mobile',
    })
    expect(menu).not.toBeInTheDocument()
  })
})
