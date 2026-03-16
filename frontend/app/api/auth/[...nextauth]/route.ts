import NextAuth, { NextAuthOptions } from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import { userService } from "@/lib/api/user"

const authOptions: NextAuthOptions = {
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID || "",
            clientSecret: process.env.GOOGLE_CLIENT_SECRET || ""
        })
    ],
    callbacks: {
        async jwt({ token, account, profile, trigger, session }) {
            // Initial sign in
            if (account && profile) {
                token.accessToken = account.access_token
                token.userId = profile.sub

                try {
                    const profileData = profile as {
                        picture?: string
                        image?: string
                    }
                    const data = await userService.syncUser({
                        id: profile.sub,
                        email: profile.email,
                        name: profile.name,
                        profile_picture:
                            profileData.picture || profileData.image
                    })

                    // Store onboarding status in token
                    token.onboardingCompleted =
                        data.data?.onboarding_completed || false
                } catch (error) {
                    console.error("Error syncing user with backend:", error)
                }
            }

            // Handle session update trigger from client
            if (
                trigger === "update" &&
                session?.onboardingCompleted !== undefined
            ) {
                token.onboardingCompleted = session.onboardingCompleted
            }

            return token
        },
        async session({ session, token }) {
            // Send properties to the client
            if (session.user) {
                session.user.id = token.userId as string
                session.user.onboardingCompleted =
                    token.onboardingCompleted as boolean
                session.accessToken = token.accessToken as string
            }
            return session
        }
    },
    pages: {
        signIn: "/auth/signin",
        newUser: "/onboarding"
    },
    secret: process.env.NEXTAUTH_SECRET
}

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST }
