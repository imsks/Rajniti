import type { Page } from '@playwright/test'
import { mockMp, mockPoliticianList } from '../../helpers/politicianFixtures'
import { TEST_USER_EMAIL, TEST_USER_ID, TEST_USER_NAME } from './auth'

export type SavedPolitician = { politician_id: string; role: string }

export interface DashboardMockState {
  savedPoliticians: SavedPolitician[]
}

export function createDashboardMockState(
  initialSaved: SavedPolitician[] = [],
): DashboardMockState {
  return { savedPoliticians: [...initialSaved] }
}

export async function installDashboardApiMocks(
  page: Page,
  state: DashboardMockState,
): Promise<void> {
  await page.route('**/api/auth/session', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        user: {
          id: TEST_USER_ID,
          name: TEST_USER_NAME,
          email: TEST_USER_EMAIL,
          onboardingCompleted: true,
        },
        expires: new Date(Date.now() + 60 * 60 * 1000).toISOString(),
      }),
    })
  })

  await page.route('**/api/v1/**', async (route) => {
    const request = route.request()
    const url = request.url()
    const method = request.method()

    if (url.includes(`/users/${TEST_USER_ID}`) && method === 'GET' && !url.includes('/politicians')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: { onboarding_completed: true },
        }),
      })
      return
    }

    if (url.includes(`/users/${TEST_USER_ID}/politicians`) && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: state.savedPoliticians,
        }),
      })
      return
    }

    if (url.includes(`/users/${TEST_USER_ID}/politicians`) && method === 'POST') {
      const body = request.postDataJSON() as {
        politician_id: string
        role: string
      }
      state.savedPoliticians = state.savedPoliticians.filter(
        (item) => item.role !== body.role,
      )
      state.savedPoliticians.push({
        politician_id: body.politician_id,
        role: body.role,
      })
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      })
      return
    }

    if (
      url.includes(`/users/${TEST_USER_ID}/politicians/`) &&
      method === 'DELETE'
    ) {
      const politicianId = url.split('/').pop()
      state.savedPoliticians = state.savedPoliticians.filter(
        (item) => item.politician_id !== politicianId,
      )
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      })
      return
    }

    if (url.includes('/politicians/search') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: { politicians: [mockMp] },
        }),
      })
      return
    }

    if (url.includes('/politicians?') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: { politicians: mockPoliticianList },
        }),
      })
      return
    }

    if (url.includes('/politicians/') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: mockMp,
        }),
      })
      return
    }

    await route.continue()
  })
}
