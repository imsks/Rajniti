/**
 * Integration tests — heavier or cross-module checks (Jest + jsdom).
 * Add API/route tests under this folder; keep fast unit tests in __tests__/lib.
 */
describe('integration smoke', () => {
  it('runs in jsdom', () => {
    expect(typeof window).toBe('object')
  })
})
