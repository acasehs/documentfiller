import { ReactNode, useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { isAuthenticated, initAuth } from '../utils/auth'

interface ProtectedRouteProps {
  children: ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const [isAuth, setIsAuth] = useState<boolean | null>(null)

  useEffect(() => {
    initAuth()
    setIsAuth(isAuthenticated())
  }, [])

  if (isAuth === null) {
    // Loading
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
        <div className="text-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuth) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
