'use client'

import { ReactNode } from 'react'
import AuthProvider from '@/components/auth/AuthProvider'
import { ThemeProvider } from '@/contexts/ThemeContext'

export default function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <AuthProvider>
        {children}
      </AuthProvider>
    </ThemeProvider>
  )
}
