import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText, Clock } from 'lucide-react'
import axios from 'axios'

export default function Dashboard() {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith('.docx')) {
      setError('Please upload a .docx file')
      return
    }

    setUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      // Navigate to document editor
      navigate(`/document/${response.data.document_id}`)
    } catch (err) {
      setError('Failed to upload document. Please try again.')
      console.error('Upload error:', err)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-white mb-4">
          AI-Powered Document Generation
        </h2>
        <p className="text-xl text-slate-300">
          Transform your DoD cybersecurity documentation with intelligent content generation
        </p>
      </div>

      {/* Upload Section */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-8 border border-slate-700 mb-8">
        <div className="text-center">
          <Upload className="w-16 h-16 text-blue-500 mx-auto mb-4" />
          <h3 className="text-2xl font-semibold text-white mb-2">
            Upload Your Document
          </h3>
          <p className="text-slate-400 mb-6">
            Upload a DOCX file to start generating content with AI
          </p>

          <div className="flex justify-center">
            <label className="cursor-pointer">
              <input
                type="file"
                accept=".docx"
                onChange={handleFileUpload}
                className="hidden"
                disabled={uploading}
              />
              <div className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition-colors flex items-center space-x-2">
                {uploading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Uploading...</span>
                  </>
                ) : (
                  <>
                    <Upload className="w-5 h-5" />
                    <span>Choose Document</span>
                  </>
                )}
              </div>
            </label>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-900/20 border border-red-700 rounded-lg">
              <p className="text-red-400">{error}</p>
            </div>
          )}
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-6 mb-12">
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
          <FileText className="w-12 h-12 text-green-500 mb-4" />
          <h4 className="text-lg font-semibold text-white mb-2">
            Smart Content Generation
          </h4>
          <p className="text-slate-400">
            Generate DoD-compliant content using advanced AI with RAG support
          </p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
          <Clock className="w-12 h-12 text-purple-500 mb-4" />
          <h4 className="text-lg font-semibold text-white mb-2">
            Batch Processing
          </h4>
          <p className="text-slate-400">
            Process multiple document sections automatically with real-time progress tracking
          </p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
          <Settings className="w-12 h-12 text-orange-500 mb-4" />
          <h4 className="text-lg font-semibold text-white mb-2">
            Technical Review
          </h4>
          <p className="text-slate-400">
            Comprehensive quality analysis with readability metrics and improvement suggestions
          </p>
        </div>
      </div>

      {/* Info Section */}
      <div className="bg-blue-900/20 border border-blue-700 rounded-xl p-6">
        <h4 className="text-lg font-semibold text-white mb-3">Getting Started</h4>
        <ol className="list-decimal list-inside space-y-2 text-slate-300">
          <li>Configure your OpenWebUI API connection in Settings</li>
          <li>Upload a DOCX document with structured headings</li>
          <li>Select sections and generate content using AI</li>
          <li>Review, edit, and commit changes back to your document</li>
          <li>Download the enhanced document</li>
        </ol>
      </div>
    </div>
  )
}
