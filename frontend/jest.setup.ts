/**
 * Jest Setup File
 * 
 * Runs before each test file. Configures global test utilities and mocks.
 */

import '@testing-library/jest-dom'

// Mock Next.js router
jest.mock('next/navigation', () => ({
    useRouter: () => ({
        push: jest.fn(),
        replace: jest.fn(),
        prefetch: jest.fn(),
        back: jest.fn(),
        forward: jest.fn(),
    }),
    usePathname: () => '/',
    useSearchParams: () => new URLSearchParams(),
}))

// Mock next-auth
jest.mock('next-auth/react', () => ({
    useSession: jest.fn(() => ({
        data: null,
        status: 'unauthenticated',
    })),
    signIn: jest.fn(),
    signOut: jest.fn(),
    SessionProvider: ({ children }: { children: React.ReactNode }) => children,
}))

// Mock fetch globally
global.fetch = jest.fn()

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
    })),
})

// Mock IntersectionObserver
class MockIntersectionObserver {
    observe = jest.fn()
    disconnect = jest.fn()
    unobserve = jest.fn()
}

Object.defineProperty(window, 'IntersectionObserver', {
    writable: true,
    configurable: true,
    value: MockIntersectionObserver,
})

// Mock ResizeObserver
class MockResizeObserver {
    observe = jest.fn()
    disconnect = jest.fn()
    unobserve = jest.fn()
}

Object.defineProperty(window, 'ResizeObserver', {
    writable: true,
    configurable: true,
    value: MockResizeObserver,
})

// Reset mocks before each test
beforeEach(() => {
    jest.clearAllMocks()
        ; (global.fetch as jest.Mock).mockReset()
})

// Console error suppression for expected errors in tests
const originalConsoleError = console.error
beforeAll(() => {
    console.error = (...args: any[]) => {
        // Suppress React act warnings and known test errors
        if (
            typeof args[0] === 'string' &&
            (args[0].includes('Warning: ReactDOM.render is no longer supported') ||
                args[0].includes('Warning: An update to') ||
                args[0].includes('act(...)'))
        ) {
            return
        }
        originalConsoleError.call(console, ...args)
    }
})

afterAll(() => {
    console.error = originalConsoleError
})

// Helper to create mock API responses
export const createMockResponse = (data: any, ok = true, status = 200) => ({
    ok,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
})

// Helper to mock successful fetch
export const mockFetchSuccess = (data: any) => {
    ; (global.fetch as jest.Mock).mockResolvedValueOnce(createMockResponse(data))
}

// Helper to mock failed fetch
export const mockFetchError = (error: string, status = 500) => {
    ; (global.fetch as jest.Mock).mockResolvedValueOnce(
        createMockResponse({ success: false, error }, false, status)
    )
}

// Helper to mock network error
export const mockNetworkError = () => {
    ; (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))
}
