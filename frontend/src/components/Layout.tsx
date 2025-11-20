import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { FileText, Settings, Home } from 'lucide-react'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      {/* Header */}
      <header className="bg-slate-900/50 backdrop-blur-sm border-b border-slate-700">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileText className="w-8 h-8 text-blue-500" />
              <h1 className="text-2xl font-bold text-white">DocumentFiller</h1>
              <span className="text-sm text-slate-400">AI-Powered Document Generation</span>
            </div>
            <nav className="flex items-center space-x-4">
              <Link
                to="/"
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  isActive('/')
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                <Home className="w-4 h-4" />
                <span>Dashboard</span>
              </Link>
              <Link
                to="/config"
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  isActive('/config')
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                <Settings className="w-4 h-4" />
                <span>Configuration</span>
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="mt-auto py-6 text-center text-slate-400 text-sm">
        <p>DocumentFiller v1.0 - DoD Cybersecurity Documentation Tool</p>
      </footer>
    </div>
  )
}
