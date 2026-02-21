/**
 * Unit tests for userService API functions
 */

import { userService } from '@/lib/api/user'

// Mock fetch globally
const mockFetch = jest.fn()
global.fetch = mockFetch

describe('userService', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  describe('syncUser', () => {
    it('should sync user successfully', async () => {
      const userData = {
        id: 'user-123',
        email: 'test@example.com',
        name: 'Test User',
        profile_picture: 'https://example.com/pic.jpg',
      }

      const expectedResponse = { success: true, data: userData }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(expectedResponse),
      })

      const result = await userService.syncUser(userData)

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/users/sync'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(userData),
        })
      )
      expect(result).toEqual(expectedResponse)
    })

    it('should throw error on sync failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        statusText: 'Bad Request',
      })

      await expect(
        userService.syncUser({ id: 'user-123', email: 'test@example.com' })
      ).rejects.toThrow('Failed to sync user')
    })

    it('should handle network error', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(
        userService.syncUser({ id: 'user-123', email: 'test@example.com' })
      ).rejects.toThrow('Network error')
    })
  })

  describe('updateUser', () => {
    it('should update user successfully', async () => {
      const userId = 'user-123'
      const updateData = { name: 'Updated Name', state: 'DL' }
      const expectedResponse = { 
        success: true, 
        data: { ...updateData, id: userId },
        message: 'User updated successfully'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(expectedResponse),
      })

      const result = await userService.updateUser(userId, updateData)

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining(`/users/${userId}`),
        expect.objectContaining({
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updateData),
        })
      )
      expect(result).toEqual(expectedResponse)
    })

    it('should complete onboarding', async () => {
      const userId = 'user-123'
      const onboardingData = {
        username: 'newuser',
        state: 'DL',
        city: 'Delhi',
        age_group: '25-35',
        political_ideology: 'Neutral',
        onboarding_completed: true,
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true, data: onboardingData }),
      })

      const result = await userService.updateUser(userId, onboardingData)

      expect(result.data.onboarding_completed).toBe(true)
    })

    it('should throw error with API error message', async () => {
      const errorMessage = 'Username already taken'

      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ error: errorMessage }),
      })

      await expect(
        userService.updateUser('user-123', { username: 'taken' })
      ).rejects.toThrow(errorMessage)
    })

    it('should throw generic error when no message', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({}),
      })

      await expect(
        userService.updateUser('user-123', { name: 'Test' })
      ).rejects.toThrow('Failed to update user')
    })
  })

  describe('checkUsername', () => {
    it('should return available true for free username', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true, available: true }),
      })

      const result = await userService.checkUsername('newusername')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/users/check-username'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ username: 'newusername', user_id: undefined }),
        })
      )
      expect(result.available).toBe(true)
    })

    it('should return available false for taken username', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true, available: false }),
      })

      const result = await userService.checkUsername('takenusername')

      expect(result.available).toBe(false)
    })

    it('should check username excluding current user', async () => {
      const userId = 'user-123'

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true, available: true }),
      })

      await userService.checkUsername('myusername', userId)

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({ username: 'myusername', user_id: userId }),
        })
      )
    })

    it('should throw error on check failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
      })

      await expect(
        userService.checkUsername('test')
      ).rejects.toThrow('Failed to check username')
    })
  })
})

describe('userService API URL', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('should use correct API base URL', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    })

    await userService.checkUsername('test')

    // Should use the API URL from environment or default
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/v1\/users\/check-username$/),
      expect.any(Object)
    )
  })
})
