import { render, screen, fireEvent } from '@testing-library/react'

const trackEvent = jest.fn()

jest.mock('@/hooks/useAnalytics', () => ({
  useAnalytics: () => ({ trackEvent }),
}))

const DEFAULT_URL = 'https://saransh-app.vercel.app'

async function renderBanner(props = {}) {
  jest.resetModules()
  const SaranshBanner = (await import('@/components/marketing/SaranshBanner'))
    .default
  render(<SaranshBanner {...props} />)
}

describe('SaranshBanner', () => {
  beforeEach(() => {
    trackEvent.mockClear()
  })

  it('renders a safe external link to Saransh', async () => {
    await renderBanner()

    const link = screen.getByRole('link', { name: /Meet Saransh/i })
    expect(link).toHaveAttribute('href', DEFAULT_URL)
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('fires saransh_click with the dashboard page location by default', async () => {
    await renderBanner()

    fireEvent.click(screen.getByRole('link', { name: /Meet Saransh/i }))

    expect(trackEvent).toHaveBeenCalledWith('saransh_click', {
      link_url: DEFAULT_URL,
      page_location: 'dashboard_saransh',
    })
  })

  it('allows overriding the analytics page location', async () => {
    await renderBanner({ pageLocation: 'profile_saransh' })

    fireEvent.click(screen.getByRole('link', { name: /Meet Saransh/i }))

    expect(trackEvent).toHaveBeenCalledWith('saransh_click', {
      link_url: DEFAULT_URL,
      page_location: 'profile_saransh',
    })
  })
})
