import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Wand2, RefreshCw, Settings as SettingsIcon } from 'lucide-react'
import { contentApi } from '../services/api'

export default function GenerationPanel({ documentId, selectedSection, onGenerated, onStatusChange }) {
  const [mode, setMode] = useState('replace')
  const [model, setModel] = useState('llama3.2:latest')
  const [temperature, setTemperature] = useState(0.7)
  const [maxTokens, setMaxTokens] = useState(2000)
  const [showAdvanced, setShowAdvanced] = useState(false)

  // Fetch available models
  const { data: modelsData } = useQuery({
    queryKey: ['models'],
    queryFn: contentApi.getModels,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const models = modelsData?.models || []

  // Generate content mutation
  const generateMutation = useMutation({
    mutationFn: (request) => contentApi.generate(request),
    onSuccess: (data) => {
      if (data.success) {
        onGenerated(data.generated_content)
        onStatusChange({
          message: `Content generated successfully (${data.processing_time.toFixed(1)}s)`,
          type: 'success',
        })
      } else {
        onStatusChange({
          message: `Generation failed: ${data.error}`,
          type: 'error',
        })
      }
    },
    onError: (error) => {
      onStatusChange({
        message: `Generation error: ${error.message}`,
        type: 'error',
      })
    },
  })

  const handleGenerate = () => {
    if (!selectedSection) {
      onStatusChange({ message: 'Please select a section first', type: 'warning' })
      return
    }

    const request = {
      document_id: documentId,
      section_id: selectedSection.id,
      mode,
      model,
      temperature,
      max_tokens: maxTokens,
      use_master_prompt: true,
      include_document_context: true,
      include_comments: true,
      knowledge_collections: [],
    }

    onStatusChange({ message: 'Generating content...', type: 'info' })
    generateMutation.mutate(request)
  }

  return (
    <div className="p-4 space-y-4">
      <div className="border-b border-gray-200 pb-3">
        <h3 className="font-semibold text-gray-900">Content Generation</h3>
        <p className="text-xs text-gray-500 mt-1">
          {selectedSection ? selectedSection.text : 'No section selected'}
        </p>
      </div>

      {/* Operation Mode */}
      <div>
        <label className="label">Operation Mode</label>
        <select
          value={mode}
          onChange={(e) => setMode(e.target.value)}
          className="input text-sm"
        >
          <option value="replace">Replace - Generate new content</option>
          <option value="rework">Rework - Enhance existing</option>
          <option value="append">Append - Add to existing</option>
        </select>
      </div>

      {/* Model Selection */}
      <div>
        <label className="label">AI Model</label>
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="input text-sm"
        >
          {models.length > 0 ? (
            models.map((m) => (
              <option key={m.id || m.name} value={m.id || m.name}>
                {m.name || m.id}
              </option>
            ))
          ) : (
            <option value="llama3.2:latest">llama3.2:latest</option>
          )}
        </select>
      </div>

      {/* Advanced Settings Toggle */}
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
      >
        <SettingsIcon className="w-4 h-4" />
        {showAdvanced ? 'Hide' : 'Show'} Advanced Settings
      </button>

      {/* Advanced Settings */}
      {showAdvanced && (
        <div className="space-y-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
          <div>
            <label className="label">
              Temperature: {temperature}
              <span className="text-xs text-gray-500 ml-2">(creativity)</span>
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Precise</span>
              <span>Creative</span>
            </div>
          </div>

          <div>
            <label className="label">Max Tokens</label>
            <input
              type="number"
              value={maxTokens}
              onChange={(e) => setMaxTokens(parseInt(e.target.value))}
              className="input text-sm"
              min="100"
              max="100000"
              step="100"
            />
          </div>
        </div>
      )}

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={!selectedSection || generateMutation.isPending}
        className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {generateMutation.isPending ? (
          <>
            <RefreshCw className="w-4 h-4 mr-2 inline animate-spin" />
            Generating...
          </>
        ) : (
          <>
            <Wand2 className="w-4 h-4 mr-2 inline" />
            Generate Content
          </>
        )}
      </button>

      {/* Section Info */}
      {selectedSection && (
        <div className="mt-6 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">Section Info</h4>
          <dl className="text-xs space-y-1">
            <div className="flex justify-between">
              <dt className="text-gray-600">Level:</dt>
              <dd className="font-medium">Heading {selectedSection.level}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">Has Content:</dt>
              <dd className="font-medium">
                {selectedSection.has_content ? 'Yes' : 'No'}
              </dd>
            </div>
            {selectedSection.comments && selectedSection.comments.length > 0 && (
              <div className="flex justify-between">
                <dt className="text-gray-600">Comments:</dt>
                <dd className="font-medium">{selectedSection.comments.length}</dd>
              </div>
            )}
          </dl>
        </div>
      )}
    </div>
  )
}
