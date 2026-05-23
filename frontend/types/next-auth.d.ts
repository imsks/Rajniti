import  { DefaultSession } from "next-auth"

declare module "next-auth" {
  interface Session {
    user: {
      id: string
      onboardingCompleted: boolean
    } & DefaultSession["user"]
    accessToken?: string
  }

  interface User {
    onboardingCompleted?: boolean
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    userId?: string
    accessToken?: string
    onboardingCompleted?: boolean
  }
}
