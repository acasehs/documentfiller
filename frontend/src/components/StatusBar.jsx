import { Info, CheckCircle, AlertCircle, XCircle } from 'lucide-react'

export default function StatusBar({ status }) {
  const { message, type } = status

  const icons = {
    info: Info,
    success: CheckCircle,
    warning: AlertCircle,
    error: XCircle,
  }

  const colors = {
    info: 'bg-blue-50 text-blue-700 border-blue-200',
    success: 'bg-green-50 text-green-700 border-green-200',
    warning: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    error: 'bg-red-50 text-red-700 border-red-200',
  }

  const Icon = icons[type] || Info
  const colorClass = colors[type] || colors.info

  return (
    <div className={`border-t px-4 py-2 flex items-center gap-2 ${colorClass}`}>
      <Icon className="w-4 h-4 flex-shrink-0" />
      <span className="text-sm font-medium">{message}</span>
    </div>
  )
}
