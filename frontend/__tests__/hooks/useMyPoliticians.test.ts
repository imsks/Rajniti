import { renderHook, waitFor } from '@testing-library/react'

import { useMyPoliticians } from '@/hooks/useMyPoliticians'
import { userService } from '@/lib/api/user'
import type { Politician } from '@/types/politician'

jest.mock('@/lib/api/user', () => ({
    userService: {
        getUserPoliticians: jest.fn(),
    },
}))

const mockedUserService = userService as jest.Mocked<typeof userService>

function mkPolitician(overrides: Partial<Politician> & Pick<Politician, 'id' | 'type'>): Politician {
    return {
        id: overrides.id,
        name: overrides.name || overrides.id,
        state: overrides.state || 'DL',
        constituency: overrides.constituency || 'Delhi',
        type: overrides.type,
        political_background: { elections: [] },
        ...overrides,
    }
}

describe('useMyPoliticians', () => {
    beforeEach(() => {
        mockedUserService.getUserPoliticians.mockReset()
        window.localStorage.clear()
    })

    it('hydrates MP/MLA from backend user data', async () => {
        mockedUserService.getUserPoliticians.mockResolvedValueOnce([
            { politician_id: 'mp-1', role: 'MP' },
            { politician_id: 'mla-1', role: 'MLA' },
        ])

        const allPoliticians: Politician[] = [
            mkPolitician({ id: 'mp-1', type: 'MP' }),
            mkPolitician({ id: 'mla-1', type: 'MLA' }),
        ]

        const { result } = renderHook(() => useMyPoliticians(allPoliticians, 'user-1'))

        await waitFor(() => {
            expect(result.current.myMP?.id).toBe('mp-1')
            expect(result.current.myMLA?.id).toBe('mla-1')
        })
    })

    it('does not call backend when user is unavailable', () => {
        renderHook(() => useMyPoliticians([], undefined))
        expect(mockedUserService.getUserPoliticians).not.toHaveBeenCalled()
    })
})
