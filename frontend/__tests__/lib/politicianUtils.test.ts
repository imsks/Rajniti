import {
    getPoliticianProfileHref,
    getPoliticianProfileSegment,
    getParty,
} from '@/lib/politicianUtils'
import type { Politician } from '@/types/politician'

const base: Politician = {
    id: 'ef8a4654-1d09-4a06-bae7-14377bc08387',
    name: 'NARENDRA MODI',
    slug: 'narendra-modi',
    state: 'Gujarat',
    constituency: 'Varanasi',
    type: 'MP',
    political_background: {
        elections: [{ year: 2024, type: 'LS', state: 'UP', constituency: 'V', party: 'BJP', status: 'WON' }],
    },
}

describe('politicianUtils', () => {
    it('getPoliticianProfileSegment prefers slug', () => {
        expect(getPoliticianProfileSegment(base)).toBe('narendra-modi')
    })

    it('getPoliticianProfileSegment falls back to id', () => {
        const { slug: _s, ...noSlug } = base
        expect(getPoliticianProfileSegment({ ...noSlug, slug: null })).toBe(base.id)
    })

    it('getPoliticianProfileHref encodes segment', () => {
        expect(getPoliticianProfileHref(base)).toBe('/politician/narendra-modi')
    })

    it('getParty returns latest election party', () => {
        expect(getParty(base)).toBe('BJP')
    })

    it('getParty returns em dash when no elections', () => {
        expect(getParty({ ...base, political_background: { elections: [] } })).toBe('—')
    })
})
