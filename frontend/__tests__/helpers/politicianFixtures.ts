import type { Politician } from '@/types/politician'

export function mkPolitician(
  overrides: Partial<Politician> & Pick<Politician, 'id' | 'type'>,
): Politician {
  const name =
    overrides.name ??
    (overrides.type === 'MP' ? 'Test MP Name' : 'Test MLA Name')

  return {
    political_background: {
      elections: [
        {
          year: 2024,
          type: overrides.type === 'MP' ? 'G' : 'A',
          state: overrides.state ?? 'DL',
          constituency: overrides.constituency ?? 'Delhi',
          party: 'BJP',
          status: 'Won',
        },
      ],
    },
    state: 'Delhi',
    constituency: 'Delhi',
    name,
    ...overrides,
  }
}

export const mockMp = mkPolitician({
  id: 'mp-1',
  type: 'MP',
  name: 'Narendra Modi',
  constituency: 'Varanasi',
  state: 'Uttar Pradesh',
})

export const mockMla = mkPolitician({
  id: 'mla-1',
  type: 'MLA',
  name: 'Example MLA',
  constituency: 'South Delhi',
  state: 'Delhi',
})

export const mockPoliticianList: Politician[] = [mockMp, mockMla]
