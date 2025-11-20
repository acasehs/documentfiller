import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  ChevronRight,
  ChevronDown,
  Sparkles,
  Save,
  Download,
  RefreshCw,
  Eye,
  Loader2
} from 'lucide-react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'

interface Section {
  id: string
  title: string
  level: number
  content: string
  children?: Section[]
}

interface Document {
  id: string
  filename: string
  sections: Section[]
  upload_time: string
}

export default function DocumentEditor() {
  const { id } = useParams<{ id: string }>()
  const [document, setDocument] = useState<Document | null>(null)
  const [selectedSection, setSelectedSection] = useState<Section | null>(null)
  const [generatedContent, setGeneratedContent] = useState('')
  const [operationMode, setOperationMode] = useState<'REPLACE' | 'REWORK' | 'APPEND'>('REPLACE')
  const [generating, setGenerating] = useState(false)
  const [reviewing, setReviewing] = useState(false)
  const [reviewResult, setReviewResult] = useState<any>(null)
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (id) {
      loadDocument(id)
    }
  }, [id])

  const loadDocument = async (documentId: string) => {
    try {
      const response = await axios.get(`/api/documents/${documentId}`)
      setDocument(response.data)

      // Expand all sections by default
      const allSectionIds = new Set<string>()
      const expandAll = (sections: Section[]) => {
        sections.forEach(section => {
          allSectionIds.add(section.id)
          if (section.children) {
            expandAll(section.children)
          }
        })
      }
      expandAll(response.data.sections)
      setExpandedSections(allSectionIds)
    } catch (err) {
      console.error('Failed to load document:', err)
    }
  }

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId)
    } else {
      newExpanded.add(sectionId)
    }
    setExpandedSections(newExpanded)
  }

  const handleGenerate = async () => {
    if (!selectedSection || !document) return

    setGenerating(true)
    setGeneratedContent('')

    try {
      const response = await axios.post('/api/generate', {
        section_id: selectedSection.id,
        section_title: selectedSection.title,
        existing_content: selectedSection.content,
        operation_mode: operationMode,
        model: 'default', // Get from config
        temperature: 0.7,
        max_tokens: 4000,
        use_rag: false,
      })

      setGeneratedContent(response.data.generated_content)
    } catch (err) {
      console.error('Generation failed:', err)
      alert('Failed to generate content. Please check your configuration.')
    } finally {
      setGenerating(false)
    }
  }

  const handleReview = async () => {
    if (!generatedContent && !selectedSection?.content) return

    setReviewing(true)
    setReviewResult(null)

    try {
      const response = await axios.post('/api/review', {
        content: generatedContent || selectedSection?.content,
        section_title: selectedSection?.title || 'Untitled',
      })

      setReviewResult(response.data)
    } catch (err) {
      console.error('Review failed:', err)
      alert('Failed to review content.')
    } finally {
      setReviewing(false)
    }
  }

  const handleCommit = async () => {
    if (!selectedSection || !generatedContent || !document) return

    try {
      await axios.post(`/api/documents/${document.id}/commit`, null, {
        params: {
          section_id: selectedSection.id,
          content: generatedContent,
        },
      })

      // Reload document
      await loadDocument(document.id)
      setGeneratedContent('')
      alert('Content committed successfully!')
    } catch (err) {
      console.error('Commit failed:', err)
      alert('Failed to commit content.')
    }
  }

  const handleDownload = async () => {
    if (!document) return

    try {
      const response = await axios.get(`/api/documents/${document.id}/download`, {
        responseType: 'blob',
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = window.document.createElement('a')
      link.href = url
      link.setAttribute('download', document.filename)
      window.document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      console.error('Download failed:', err)
      alert('Failed to download document.')
    }
  }

  const renderSectionTree = (sections: Section[], level = 0) => {
    return sections.map((section) => {
      const isExpanded = expandedSections.has(section.id)
      const isSelected = selectedSection?.id === section.id
      const hasChildren = section.children && section.children.length > 0

      return (
        <div key={section.id} style={{ marginLeft: `${level * 1.5}rem` }}>
          <div
            className={`flex items-center space-x-2 py-2 px-3 rounded cursor-pointer transition-colors ${
              isSelected
                ? 'bg-blue-600 text-white'
                : 'hover:bg-slate-700 text-slate-300'
            }`}
            onClick={() => setSelectedSection(section)}
          >
            {hasChildren && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  toggleSection(section.id)
                }}
                className="p-1 hover:bg-slate-600 rounded"
              >
                {isExpanded ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
              </button>
            )}
            {!hasChildren && <div className="w-6" />}
            <span className="text-sm font-medium truncate">{section.title}</span>
          </div>
          {isExpanded && hasChildren && renderSectionTree(section.children!, level + 1)}
        </div>
      )
    })
  }

  if (!document) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="grid grid-cols-12 gap-6 h-[calc(100vh-12rem)]">
      {/* Left Sidebar - Document Structure */}
      <div className="col-span-3 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 overflow-hidden flex flex-col">
        <div className="p-4 border-b border-slate-700">
          <h3 className="font-semibold text-white">Document Structure</h3>
          <p className="text-sm text-slate-400 mt-1">{document.filename}</p>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {renderSectionTree(document.sections)}
        </div>

        {/* Operation Mode */}
        <div className="p-4 border-t border-slate-700">
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
                  className="text-blue-600"
                />
                <span className="text-sm text-slate-300">{mode}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="p-4 border-t border-slate-700 space-y-2">
          <button
            onClick={handleGenerate}
            disabled={!selectedSection || generating}
            className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {generating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate</span>
              </>
            )}
          </button>

          <button
            onClick={handleDownload}
            className="w-full flex items-center justify-center space-x-2 bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Download</span>
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="col-span-9 space-y-6">
        {/* Section Header */}
        {selectedSection && (
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-700">
            <h2 className="text-2xl font-bold text-white">{selectedSection.title}</h2>
            <p className="text-slate-400 text-sm mt-1">
              Level {selectedSection.level} - {operationMode} mode
            </p>
          </div>
        )}

        {/* Content Comparison */}
        <div className="grid grid-cols-2 gap-4 h-[calc(100%-8rem)]">
          {/* Existing Content */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 overflow-hidden flex flex-col">
            <div className="p-4 border-b border-slate-700">
              <h3 className="font-semibold text-white">Existing Content</h3>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              <div className="prose prose-invert max-w-none">
                <ReactMarkdown>{selectedSection?.content || 'No content'}</ReactMarkdown>
              </div>
            </div>
          </div>

          {/* Generated Content */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 overflow-hidden flex flex-col">
            <div className="p-4 border-b border-slate-700 flex items-center justify-between">
              <h3 className="font-semibold text-white">Generated Content</h3>
              {generatedContent && (
                <div className="flex space-x-2">
                  <button
                    onClick={handleReview}
                    disabled={reviewing}
                    className="flex items-center space-x-1 text-sm bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded transition-colors disabled:opacity-50"
                  >
                    {reviewing ? (
                      <>
                        <Loader2 className="w-3 h-3 animate-spin" />
                        <span>Reviewing...</span>
                      </>
                    ) : (
                      <>
                        <Eye className="w-3 h-3" />
                        <span>Review</span>
                      </>
                    )}
                  </button>
                  <button
                    onClick={handleCommit}
                    className="flex items-center space-x-1 text-sm bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded transition-colors"
                  >
                    <Save className="w-3 h-3" />
                    <span>Commit</span>
                  </button>
                </div>
              )}
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              {generatedContent ? (
                <div className="prose prose-invert max-w-none">
                  <ReactMarkdown>{generatedContent}</ReactMarkdown>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-slate-500">
                  <div className="text-center">
                    <Sparkles className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>Generated content will appear here</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Review Results */}
        {reviewResult && (
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
            <h3 className="text-xl font-semibold text-white mb-4">Review Results</h3>
            <div className="grid grid-cols-5 gap-4 mb-4">
              {Object.entries(reviewResult.scores || {}).map(([key, value]) => (
                <div key={key} className="text-center">
                  <div className="text-2xl font-bold text-blue-400">{value as number}/10</div>
                  <div className="text-sm text-slate-400 capitalize">{key}</div>
                </div>
              ))}
            </div>
            {reviewResult.feedback && (
              <div className="mt-4">
                <h4 className="font-semibold text-white mb-2">Feedback</h4>
                <p className="text-slate-300 whitespace-pre-wrap">{reviewResult.feedback}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
