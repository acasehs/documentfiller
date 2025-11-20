import { useState } from 'react'
import { Sparkles, Copy, CheckCircle, GitCompare } from 'lucide-react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'

interface ComparisonResult {
  model: string
  content: string
  tokens_used: number
  timestamp: string
  error?: string
}

export default function ModelComparison() {
  const [sectionTitle, setSectionTitle] = useState('')
  const [existingContent, setExistingContent] = useState('')
  const [operationMode, setOperationMode] = useState<'REPLACE' | 'REWORK' | 'APPEND'>('REPLACE')
  const [models, setModels] = useState<string[]>([])
  const [selectedModels, setSelectedModels] = useState<string[]>([])
  const [temperature, setTemperature] = useState(0.7)
  const [maxTokens, setMaxTokens] = useState(4000)
  const [generating, setGenerating] = useState(false)
  const [results, setResults] = useState<ComparisonResult[]>([])
  const [winner, setWinner] = useState<number | null>(null)

  const loadModels = async () => {
    try {
      const response = await axios.get('/api/models')
      const modelList = response.data.data?.map((m: any) => m.id) || []
      setModels(modelList)
    } catch (err) {
      console.error('Failed to load models:', err)
    }
  }

  const handleModelToggle = (model: string) => {
    setSelectedModels(prev => {
      if (prev.includes(model)) {
        return prev.filter(m => m !== model)
      } else if (prev.length < 3) {
        return [...prev, model]
      }
      return prev
    })
  }

  const handleGenerate = async () => {
    if (selectedModels.length === 0) {
      alert('Please select at least one model')
      return
    }

    setGenerating(true)
    setResults([])
    setWinner(null)

    const promises = selectedModels.map(async (model) => {
      try {
        const response = await axios.post('/api/generate', {
          section_id: 'comparison',
          section_title: sectionTitle,
          existing_content: existingContent,
          operation_mode: operationMode,
          model: model,
          temperature: temperature,
          max_tokens: maxTokens,
        })

        return {
          model: model,
          content: response.data.generated_content,
          tokens_used: response.data.tokens_used,
          timestamp: response.data.timestamp,
        }
      } catch (error: any) {
        return {
          model: model,
          content: '',
          tokens_used: 0,
          timestamp: new Date().toISOString(),
          error: error.response?.data?.detail || 'Generation failed',
        }
      }
    })

    const comparisonResults = await Promise.all(promises)
    setResults(comparisonResults)
    setGenerating(false)
  }

  const handleCopyContent = (index: number) => {
    const content = results[index].content
    navigator.clipboard.writeText(content)
  }

  const handleSelectWinner = (index: number) => {
    setWinner(index)
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <GitCompare className="w-8 h-8 text-purple-500" />
          <h2 className="text-3xl font-bold text-white">Model Comparison</h2>
        </div>
        <p className="text-slate-400">
          Generate content with up to 3 models simultaneously and compare results
        </p>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Configuration Panel */}
        <div className="col-span-4 space-y-6">
          {/* Section Details */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
            <h3 className="text-lg font-semibold text-white mb-4">Section Details</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Section Title
                </label>
                <input
                  type="text"
                  value={sectionTitle}
                  onChange={(e) => setSectionTitle(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="e.g., System Security Plan"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Existing Content (Optional)
                </label>
                <textarea
                  value={existingContent}
                  onChange={(e) => setExistingContent(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows={4}
                  placeholder="Paste existing content here..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Operation Mode
                </label>
                <div className="space-y-2">
                  {['REPLACE', 'REWORK', 'APPEND'].map((mode) => (
                    <label key={mode} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="radio"
                        value={mode}
                        checked={operationMode === mode}
                        onChange={(e) => setOperationMode(e.target.value as any)}
                        className="text-purple-600"
                      />
                      <span className="text-sm text-slate-300">{mode}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Model Selection */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">
                Select Models (max 3)
              </h3>
              <button
                onClick={loadModels}
                className="text-sm text-purple-400 hover:text-purple-300"
              >
                Refresh
              </button>
            </div>

            <div className="space-y-2 max-h-64 overflow-y-auto">
              {models.length === 0 ? (
                <p className="text-slate-400 text-sm">
                  Click "Refresh" to load models
                </p>
              ) : (
                models.map((model) => (
                  <label
                    key={model}
                    className={`flex items-center space-x-2 p-2 rounded cursor-pointer transition-colors ${
                      selectedModels.includes(model)
                        ? 'bg-purple-600/20 border border-purple-600'
                        : 'hover:bg-slate-700'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedModels.includes(model)}
                      onChange={() => handleModelToggle(model)}
                      disabled={!selectedModels.includes(model) && selectedModels.length >= 3}
                      className="text-purple-600"
                    />
                    <span className="text-sm text-slate-300 truncate">{model}</span>
                  </label>
                ))
              )}
            </div>

            <div className="mt-4 text-sm text-slate-400">
              Selected: {selectedModels.length}/3
            </div>
          </div>

          {/* Generation Parameters */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
            <h3 className="text-lg font-semibold text-white mb-4">Parameters</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Temperature: {temperature}
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
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  min="100"
                  max="32000"
                />
              </div>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={generating || selectedModels.length === 0 || !sectionTitle}
            className="w-full flex items-center justify-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {generating ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Generate & Compare</span>
              </>
            )}
          </button>
        </div>

        {/* Results Panel */}
        <div className="col-span-8">
          {results.length === 0 ? (
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-12 border border-slate-700 flex items-center justify-center h-full">
              <div className="text-center text-slate-400">
                <GitCompare className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg">Configure settings and click "Generate & Compare"</p>
                <p className="text-sm mt-2">Results will appear here side-by-side</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {results.map((result, index) => (
                <div
                  key={index}
                  className={`bg-slate-800/50 backdrop-blur-sm rounded-xl border overflow-hidden transition-all ${
                    winner === index
                      ? 'border-green-500 shadow-lg shadow-green-500/20'
                      : 'border-slate-700'
                  }`}
                >
                  <div className="p-4 border-b border-slate-700 flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-white">{result.model}</h4>
                      <p className="text-sm text-slate-400">
                        {result.tokens_used} tokens
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleCopyContent(index)}
                        className="p-2 hover:bg-slate-700 rounded transition-colors"
                        title="Copy content"
                      >
                        <Copy className="w-4 h-4 text-slate-400" />
                      </button>
                      <button
                        onClick={() => handleSelectWinner(index)}
                        className={`flex items-center space-x-1 px-3 py-1 rounded transition-colors ${
                          winner === index
                            ? 'bg-green-600 text-white'
                            : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                        }`}
                      >
                        <CheckCircle className="w-4 h-4" />
                        <span className="text-sm">
                          {winner === index ? 'Winner' : 'Select'}
                        </span>
                      </button>
                    </div>
                  </div>

                  <div className="p-6 max-h-96 overflow-y-auto">
                    {result.error ? (
                      <div className="text-red-400 text-sm">
                        Error: {result.error}
                      </div>
                    ) : (
                      <div className="prose prose-invert max-w-none">
                        <ReactMarkdown>{result.content}</ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {winner !== null && (
                <div className="bg-green-900/20 border border-green-700 rounded-xl p-4 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-6 h-6 text-green-400" />
                    <div>
                      <p className="font-semibold text-white">
                        Winner: {results[winner].model}
                      </p>
                      <p className="text-sm text-slate-400">
                        You can copy this content to use in your document
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleCopyContent(winner)}
                    className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                    <span>Copy Winner</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
