import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Edit3, Eye } from 'lucide-react'
import { useState } from 'react'

export default function ContentPreview({ content, onChange, section }) {
  const [isEditing, setIsEditing] = useState(false)

  if (!section) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <div className="text-center">
          <Eye className="w-12 h-12 mx-auto mb-2 text-gray-300" />
          <p>Select a section to view content</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h2 className="font-semibold text-lg text-gray-900">{section.text}</h2>
            <p className="text-sm text-gray-500 mt-1">{section.full_path}</p>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => setIsEditing(!isEditing)}
              className={`btn-secondary text-sm ${isEditing ? 'bg-primary-100' : ''}`}
            >
              {isEditing ? (
                <>
                  <Eye className="w-4 h-4 mr-1 inline" />
                  Preview
                </>
              ) : (
                <>
                  <Edit3 className="w-4 h-4 mr-1 inline" />
                  Edit
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto p-6">
        {isEditing ? (
          <textarea
            value={content || ''}
            onChange={(e) => onChange(e.target.value)}
            className="w-full h-full min-h-[500px] p-4 border border-gray-300 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Generated content will appear here..."
          />
        ) : (
          <div className="prose max-w-none">
            {content ? (
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '')
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={vscDarkPlus}
                        language={match[1]}
                        PreTag="div"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    )
                  },
                }}
              >
                {content}
              </ReactMarkdown>
            ) : (
              <div className="text-gray-400 text-center py-12">
                <p>No content generated yet.</p>
                <p className="text-sm mt-2">Use the generation panel to create content.</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Existing Content Display */}
      {section.existing_content && (
        <div className="border-t border-gray-200 bg-gray-50 p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Existing Content:</h3>
          <div className="text-sm text-gray-600 bg-white p-3 rounded border border-gray-200 max-h-32 overflow-auto">
            {section.existing_content}
          </div>
        </div>
      )}
    </div>
  )
}
