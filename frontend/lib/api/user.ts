const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000/api/v1"

export interface UserData {
    id?: string
    email?: string
    name?: string
    profile_picture?: string
    username?: string
    political_ideology?: string
    onboarding_completed?: boolean
    [key: string]: string | boolean | undefined
}

interface UserPoliticianRecord {
    politician_id: string
    role: "MP" | "MLA" | string
}

export const userService = {
    /**
     * Sync user with backend (Get or Create)
     * Used during authentication
     */
    async syncUser(userData: UserData) {
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
    },

    async getUserPoliticians(userId: string): Promise<UserPoliticianRecord[] | null> {
        try {
            const response = await fetch(`${API_BASE_URL}/users/${userId}/politicians`)
            if (!response.ok) {
                return null
            }

            const data = await response.json()
            if (!data?.success || !Array.isArray(data.data)) {
                return null
            }

            return data.data as UserPoliticianRecord[]
        } catch {
            return null
        }
    },


/**
 * Add politician to user
 */
addUserPolitician: async (userId: string, politicianId: string, role: string) => {
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/politicians`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                politician_id: politicianId,
                role: role
            })
        })

        // 🔥 handle empty response safely
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        let data: any = {}
        try {
            data = await response.json()
        } catch {
            data = {}
        }

        console.warn("ADD RESPONSE:", response.status, data)

        // ❗ don't break UI even if backend sends {}
        if (!response.ok) {
            console.error("❌ BACKEND ERROR:", data)
            return { success: false }
        }

        return data || { success: true }

    } catch (err) {
        console.error("❌ FETCH ERROR:", err)
        return { success: false }
    }
},

/**
 * Remove politician from user
 */
removeUserPolitician: async (userId: string, politicianId: string) => {
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/politicians/${politicianId}`, {
            method: "DELETE"
        })

        // 🔥 handle empty response safely
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        let data: any = {}
        try {
            data = await response.json()
        } catch {
            data = {}
        }

        console.warn("DELETE RESPONSE:", response.status, data)

        // ❗ don't crash UI
        if (!response.ok) {
            console.error("❌ BACKEND ERROR:", data)
            return { success: false }
        }

        return data || { success: true }

    } catch (err) {
        console.error("❌ FETCH ERROR:", err)
        return { success: false }
    }
}
}
