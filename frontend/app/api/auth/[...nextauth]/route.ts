import NextAuth, { NextAuthOptions } from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import CredentialsProvider from "next-auth/providers/credentials"
import { userService } from "@/lib/api/user"
import {
  applyOnboardingCompleted,
  onboardingCompletedFromUserResponse,
} from "@/lib/auth/onboarding-token"

function buildProviders(): NextAuthOptions["providers"] {
  const providers: NextAuthOptions["providers"] = [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
  ]

  if (process.env.ENABLE_TEST_AUTH === "true") {
    providers.push(
      CredentialsProvider({
        id: "test-credentials",
        name: "Test",
        credentials: {
          userId: { label: "User ID", type: "text" },
          onboardingCompleted: { label: "Onboarding Completed", type: "text" },
        },
        async authorize(credentials) {
          const userId = credentials?.userId
          if (!userId) return null

          return {
            id: userId,
            email: `${userId}@test.local`,
            name: "Test User",
            onboardingCompleted: credentials?.onboardingCompleted === "true",
          }
        },
      })
    )
  }

  return providers
}

const authOptions: NextAuthOptions = {
  providers: buildProviders(),

  callbacks: {
    async jwt({ token, account, profile, user, trigger, session }) {
      if (account?.provider === "test-credentials" && user) {
        token.userId = user.id
        token.onboardingCompleted = Boolean(user.onboardingCompleted)
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

          const data = await userService.syncUser({
            id: profile.sub,
            email: profile.email,
            name: profile.name,
            profile_picture:
              profileData.picture || profileData.image,
          })

          token.onboardingCompleted =
            onboardingCompletedFromUserResponse(data)
        } catch (error) {
          console.error("❌ Sync error:", error)
          token.onboardingCompleted = false
        }

        return token
      }

      if (
        trigger === "update" &&
        session?.onboardingCompleted !== undefined
      ) {
        return applyOnboardingCompleted(token, session.onboardingCompleted)
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
    },
  },

  pages: {
    signIn: "/auth/signin",
    newUser: "/onboarding",
  },

  secret: process.env.NEXTAUTH_SECRET,
}

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST }
