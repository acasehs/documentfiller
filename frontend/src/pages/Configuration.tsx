import { useState, useEffect } from 'react'
import { Save, CheckCircle, AlertCircle } from 'lucide-react'
import axios from 'axios'

interface ConfigData {
  api_url: string
  api_key: string
  model: string
  temperature: number
  max_tokens: number
}

export default function Configuration() {
  const [config, setConfig] = useState<ConfigData>({
    api_url: 'http://localhost:3000',
    api_key: '',
    model: '',
    temperature: 0.7,
    max_tokens: 4000,
  })
  const [models, setModels] = useState<string[]>([])
  const [saving, setSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      const response = await axios.get('/api/config')
      if (response.data) {
        setConfig(response.data)
      }
    } catch (err) {
      console.error('Failed to load config:', err)
    }
  }

  const fetchModels = async () => {
    if (!config.api_url || !config.api_key) {
      setErrorMessage('Please enter API URL and API Key first')
      return
    }

    try {
      const response = await axios.get('/api/models')
      const modelList = response.data.data?.map((m: any) => m.id) || []
      setModels(modelList)
      if (modelList.length > 0 && !config.model) {
        setConfig({ ...config, model: modelList[0] })
      }
    } catch (err) {
      setErrorMessage('Failed to fetch models. Check your API configuration.')
      console.error('Failed to fetch models:', err)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setSaveStatus('idle')
    setErrorMessage('')

    try {
      await axios.post('/api/config', config)
      setSaveStatus('success')
      setTimeout(() => setSaveStatus('idle'), 3000)
    } catch (err) {
      setSaveStatus('error')
      setErrorMessage('Failed to save configuration')
      console.error('Save error:', err)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Configuration</h2>
        <p className="text-slate-400">
          Configure your OpenWebUI connection and AI model settings
        </p>
      </div>

      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-8 border border-slate-700">
        {/* API Configuration */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-white mb-4">OpenWebUI API</h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                API URL
              </label>
              <input
                type="text"
                value={config.api_url}
                onChange={(e) => setConfig({ ...config, api_url: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="http://localhost:3000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                API Key
              </label>
              <input
                type="password"
                value={config.api_key}
                onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="sk-..."
              />
            </div>

            <button
              onClick={fetchModels}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
            >
              Fetch Available Models
            </button>
          </div>
        </div>

        {/* Model Configuration */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-white mb-4">Model Settings</h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Model
              </label>
              {models.length > 0 ? (
                <select
                  value={config.model}
                  onChange={(e) => setConfig({ ...config, model: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {models.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  value={config.model}
                  onChange={(e) => setConfig({ ...config, model: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="llama2, mistral, etc."
                />
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Temperature: {config.temperature}
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={config.temperature}
                onChange={(e) => setConfig({ ...config, temperature: parseFloat(e.target.value) })}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-slate-400 mt-1">
                <span>Precise</span>
                <span>Creative</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Max Tokens
              </label>
              <input
                type="number"
                value={config.max_tokens}
                onChange={(e) => setConfig({ ...config, max_tokens: parseInt(e.target.value) })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="100"
                max="32000"
              />
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex items-center justify-between pt-6 border-t border-slate-700">
          <div>
            {saveStatus === 'success' && (
              <div className="flex items-center text-green-400">
                <CheckCircle className="w-5 h-5 mr-2" />
                <span>Configuration saved successfully</span>
              </div>
            )}
            {saveStatus === 'error' && (
              <div className="flex items-center text-red-400">
                <AlertCircle className="w-5 h-5 mr-2" />
                <span>{errorMessage}</span>
              </div>
            )}
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50"
          >
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Saving...</span>
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                <span>Save Configuration</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
