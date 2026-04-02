import NextAuth, { NextAuthOptions } from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import CredentialsProvider from "next-auth/providers/credentials"
import { userService } from "@/lib/api/user"

const e2eAuthEnabled = process.env.E2E_AUTH === "true"

const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || ""
    }),
    ...(e2eAuthEnabled
      ? [
          CredentialsProvider({
            id: "e2e-credentials",
            name: "E2E Test Account",
            credentials: {},
            async authorize() {
              return {
                id: "e2e-playwright-user",
                name: "E2E User",
                email: "e2e@test.local",
                image: null,
              }
            },
          }),
        ]
      : []),
  ],

  callbacks: {
    async jwt({ token, account, profile, user, trigger, session }) {
      // Must match CredentialsProvider `id` (not the default "credentials")
      if (account?.provider === "e2e-credentials" && user) {
        token.userId = user.id
        token.onboardingCompleted = true
        return token
      }

      if (account && profile) {
        token.accessToken = account.access_token
        token.userId = profile.sub

        try {
          const profileData = profile as {
            picture?: string
            image?: string
          }

          // 🔥 SINGLE CALL (FIXED)
          const data = await userService.syncUser({
            id: profile.sub,
            email: profile.email,
            name: profile.name,
            profile_picture:
              profileData.picture || profileData.image
          })

          token.onboardingCompleted =
            data?.data?.onboarding_completed || false

        } catch (error) {
          console.error("❌ Sync error:", error)
          token.onboardingCompleted = false
        }
      }

      if (
        trigger === "update" &&
        session?.onboardingCompleted !== undefined
      ) {
        token.onboardingCompleted = session.onboardingCompleted
      }

      return token
    },

    async session({ session, token }) {
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