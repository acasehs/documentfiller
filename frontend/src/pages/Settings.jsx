import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Save, Server, Key } from 'lucide-react'
import { configApi } from '../services/api'

export default function Settings() {
  const [config, setConfig] = useState({
    base_url: 'http://172.16.27.122:3000',
    api_key: '',
    default_model: 'llama3.2:latest',
    default_temperature: 0.7,
    default_max_tokens: 2000,
  })

  const [saved, setSaved] = useState(false)

  // Fetch current config
  const { data: currentConfig } = useQuery({
    queryKey: ['openwebuiConfig'],
    queryFn: configApi.getOpenWebUI,
    onSuccess: (data) => {
      setConfig(data)
    },
  })

  // Save config mutation
  const saveMutation = useMutation({
    mutationFn: (newConfig) => configApi.updateOpenWebUI(newConfig),
    onSuccess: () => {
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    },
  })

  const handleSave = () => {
    saveMutation.mutate(config)
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">Configure your Document Filler application</p>
      </div>

      <div className="space-y-6">
        {/* OpenWebUI Configuration */}
        <div className="card">
          <div className="flex items-center gap-3 mb-6">
            <Server className="w-6 h-6 text-primary-600" />
            <h2 className="text-xl font-semibold">OpenWebUI Configuration</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="label">Base URL</label>
              <input
                type="text"
                value={config.base_url}
                onChange={(e) => setConfig({ ...config, base_url: e.target.value })}
                className="input"
                placeholder="http://172.16.27.122:3000"
              />
              <p className="text-xs text-gray-500 mt-1">
                The URL of your OpenWebUI instance
              </p>
            </div>

            <div>
              <label className="label">
                <Key className="w-4 h-4 inline mr-1" />
                API Key (Optional)
              </label>
              <input
                type="password"
                value={config.api_key}
                onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
                className="input"
                placeholder="Enter your API key if required"
              />
            </div>

            <div>
              <label className="label">Default Model</label>
              <input
                type="text"
                value={config.default_model}
                onChange={(e) => setConfig({ ...config, default_model: e.target.value })}
                className="input"
                placeholder="llama3.2:latest"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Default Temperature</label>
                <input
                  type="number"
                  value={config.default_temperature}
                  onChange={(e) =>
                    setConfig({ ...config, default_temperature: parseFloat(e.target.value) })
                  }
                  className="input"
                  min="0"
                  max="2"
                  step="0.1"
                />
              </div>

              <div>
                <label className="label">Default Max Tokens</label>
                <input
                  type="number"
                  value={config.default_max_tokens}
                  onChange={(e) =>
                    setConfig({ ...config, default_max_tokens: parseInt(e.target.value) })
                  }
                  className="input"
                  min="100"
                  max="100000"
                  step="100"
                />
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200 flex justify-between items-center">
            {saved && (
              <span className="text-green-600 text-sm font-medium">
                Settings saved successfully!
              </span>
            )}
            <div className="flex-1"></div>
            <button
              onClick={handleSave}
              disabled={saveMutation.isPending}
              className="btn-primary"
            >
              <Save className="w-4 h-4 mr-2 inline" />
              {saveMutation.isPending ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>

        {/* About */}
        <div className="card bg-gray-50">
          <h3 className="font-semibold mb-2">About Document Filler</h3>
          <p className="text-sm text-gray-600">
            AI-powered document content generation and analysis tool.
          </p>
          <p className="text-xs text-gray-500 mt-2">Version 1.0.0</p>
        </div>
      </div>
    </div>
  )
}
