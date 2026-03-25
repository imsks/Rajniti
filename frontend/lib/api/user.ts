const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export interface UserData {
    id?: string
    email?: string
    name?: string
    profile_picture?: string
    username?: string
    political_interest?: string
    onboarding_completed?: boolean
    [key: string]: string | boolean | undefined
}

export const userService = {
    /**
     * Sync user with backend (Get or Create)
     * Used during authentication
     */
    async syncUser(userData: UserData) {
        console.log("userData", `${API_BASE_URL}/users/sync`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(userData)
        })
        const response = await fetch(`${API_BASE_URL}/users/sync`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(userData)
        })

        if (!response.ok) {
            throw new Error(`Failed to sync user: ${response.statusText}`)
        }

        return response.json()
    },

    /**
     * Update user profile (PATCH)
     * Used for onboarding and profile updates
     */
    async updateUser(userId: string, data: UserData) {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.error || "Failed to update user")
        }

        return response.json()
    },

    async checkUsername(username: string, userId?: string) {
        const response = await fetch(`${API_BASE_URL}/users/check-username`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, user_id: userId })
        })

        if (!response.ok) {
            throw new Error("Failed to check username")
        }

        return response.json()
    }
}
