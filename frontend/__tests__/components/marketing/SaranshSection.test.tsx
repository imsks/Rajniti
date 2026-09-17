import { render, screen, fireEvent } from '@testing-library/react'

const trackEvent = jest.fn()

jest.mock('@/hooks/useAnalytics', () => ({
  useAnalytics: () => ({ trackEvent }),
}))

const DEFAULT_URL = 'https://saransh-app.vercel.app'

async function renderSection(saranshUrl?: string) {
  jest.resetModules()
  if (saranshUrl) {
    process.env.NEXT_PUBLIC_SARANSH_URL = saranshUrl
  } else {
    delete process.env.NEXT_PUBLIC_SARANSH_URL
  }

  const SaranshSection = (await import('@/components/marketing/SaranshSection'))
    .default
  render(<SaranshSection />)
}

describe('SaranshSection', () => {
  const originalUrl = process.env.NEXT_PUBLIC_SARANSH_URL

  afterEach(() => {
    if (originalUrl === undefined) {
      delete process.env.NEXT_PUBLIC_SARANSH_URL
    } else {
      process.env.NEXT_PUBLIC_SARANSH_URL = originalUrl
    }
  })

  it('renders the cross-promo copy and a safe external link to the default URL', async () => {
    await renderSection()

    expect(
      screen.getByRole('heading', { name: /Meet Saransh/i })
    ).toBeInTheDocument()

    const link = screen.getByRole('link', { name: /Read the news on Saransh/i })
    expect(link).toHaveAttribute('href', DEFAULT_URL)
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('resolves the href from NEXT_PUBLIC_SARANSH_URL when set', async () => {
    await renderSection('https://saransh.example.com')

    expect(
      screen.getByRole('link', { name: /Read the news on Saransh/i })
    ).toHaveAttribute('href', 'https://saransh.example.com')
  })

  it('fires the saransh_click analytics event on click', async () => {
    await renderSection('https://saransh.example.com')

    fireEvent.click(
      screen.getByRole('link', { name: /Read the news on Saransh/i })
    )

    expect(trackEvent).toHaveBeenCalledWith('saransh_click', {
      link_url: 'https://saransh.example.com',
      page_location: 'home_saransh',
    })
  })
})
