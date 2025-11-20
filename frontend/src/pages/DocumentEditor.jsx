import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Upload, FileText, Save, Download } from 'lucide-react'
import { documentApi, contentApi } from '../services/api'
import DocumentTree from '../components/DocumentTree'
import ContentPreview from '../components/ContentPreview'
import GenerationPanel from '../components/GenerationPanel'
import StatusBar from '../components/StatusBar'

export default function DocumentEditor() {
  const [documentId, setDocumentId] = useState(null)
  const [selectedSection, setSelectedSection] = useState(null)
  const [generatedContent, setGeneratedContent] = useState('')
  const [status, setStatus] = useState({ message: 'Ready', type: 'info' })

  // Document structure query
  const { data: structure, isLoading, refetch } = useQuery({
    queryKey: ['documentStructure', documentId],
    queryFn: () => documentApi.getStructure(documentId),
    enabled: !!documentId,
  })

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: (file) => documentApi.upload(file),
    onSuccess: (data) => {
      setDocumentId(data.document_id)
      setStatus({ message: `Document uploaded: ${data.filename}`, type: 'success' })
    },
    onError: (error) => {
      setStatus({ message: `Upload failed: ${error.message}`, type: 'error' })
    },
  })

  // Save mutation
  const saveMutation = useMutation({
    mutationFn: ({ documentId, sections }) =>
      documentApi.save(documentId, sections, true),
    onSuccess: (data) => {
      setStatus({ message: data.message, type: 'success' })
    },
    onError: (error) => {
      setStatus({ message: `Save failed: ${error.message}`, type: 'error' })
    },
  })

  const handleFileUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      uploadMutation.mutate(file)
    }
  }

  const handleDownload = async () => {
    if (!documentId) return
    try {
      const blob = await documentApi.download(documentId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = structure?.filename || 'document.docx'
      a.click()
      window.URL.revokeObjectURL(url)
      setStatus({ message: 'Document downloaded', type: 'success' })
    } catch (error) {
      setStatus({ message: `Download failed: ${error.message}`, type: 'error' })
    }
  }

  const handleSave = () => {
    if (!documentId || !selectedSection || !generatedContent) return

    const sectionsToUpdate = {
      [selectedSection.id]: generatedContent,
    }

    saveMutation.mutate({ documentId, sections: sectionsToUpdate })
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex gap-3">
          <label className="btn-primary cursor-pointer inline-flex items-center gap-2">
            <Upload className="w-4 h-4" />
            Upload Document
            <input
              type="file"
              accept=".docx"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>

          {documentId && (
            <>
              <button
                onClick={handleSave}
                disabled={!generatedContent}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                Save Changes
              </button>

              <button
                onClick={handleDownload}
                className="btn-secondary inline-flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download
              </button>
            </>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {!documentId ? (
          <div className="flex-1 flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-700 mb-2">
                No Document Loaded
              </h2>
              <p className="text-gray-500 mb-6">
                Upload a Word document (.docx) to get started
              </p>
              <label className="btn-primary cursor-pointer inline-flex items-center gap-2">
                <Upload className="w-4 h-4" />
                Upload Document
                <input
                  type="file"
                  accept=".docx"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
            </div>
          </div>
        ) : (
          <>
            {/* Left Panel - Document Structure */}
            <div className="w-1/4 border-r border-gray-200 overflow-auto bg-white">
              <DocumentTree
                sections={structure?.sections || []}
                selectedSection={selectedSection}
                onSelectSection={setSelectedSection}
                isLoading={isLoading}
              />
            </div>

            {/* Middle Panel - Content Preview */}
            <div className="flex-1 overflow-auto bg-gray-50">
              <ContentPreview
                content={generatedContent}
                onChange={setGeneratedContent}
                section={selectedSection}
              />
            </div>

            {/* Right Panel - Generation Controls */}
            <div className="w-1/4 border-l border-gray-200 overflow-auto bg-white">
              <GenerationPanel
                documentId={documentId}
                selectedSection={selectedSection}
                onGenerated={setGeneratedContent}
                onStatusChange={setStatus}
              />
            </div>
          </>
        )}
      </div>

      {/* Status Bar */}
      <StatusBar status={status} />
    </div>
  )
}
