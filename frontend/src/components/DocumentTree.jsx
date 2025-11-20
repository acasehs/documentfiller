import { ChevronRight, ChevronDown, FileText, MessageCircle } from 'lucide-react'
import { useState } from 'react'

function TreeNode({ section, selectedSection, onSelectSection, level = 0 }) {
  const [isExpanded, setIsExpanded] = useState(true)
  const hasChildren = section.children && section.children.length > 0
  const isSelected = selectedSection?.id === section.id

  return (
    <div>
      <div
        className={`
          flex items-center gap-2 py-2 px-3 cursor-pointer hover:bg-gray-50 transition-colors
          ${isSelected ? 'bg-primary-50 border-l-4 border-primary-600' : 'border-l-4 border-transparent'}
        `}
        style={{ paddingLeft: `${level * 1.5 + 0.75}rem` }}
        onClick={() => onSelectSection(section)}
      >
        {hasChildren && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              setIsExpanded(!isExpanded)
            }}
            className="p-0.5 hover:bg-gray-200 rounded"
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4 text-gray-600" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-600" />
            )}
          </button>
        )}
        {!hasChildren && <div className="w-5" />}

        <FileText className={`w-4 h-4 ${section.has_content ? 'text-green-600' : 'text-gray-400'}`} />

        <span className={`text-sm flex-1 ${isSelected ? 'font-semibold text-primary-900' : 'text-gray-700'}`}>
          {section.text}
        </span>

        {section.comments && section.comments.length > 0 && (
          <MessageCircle className="w-4 h-4 text-blue-500" title={`${section.comments.length} comments`} />
        )}
      </div>

      {hasChildren && isExpanded && (
        <div>
          {section.children.map((child) => (
            <TreeNode
              key={child.id}
              section={child}
              selectedSection={selectedSection}
              onSelectSection={onSelectSection}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default function DocumentTree({ sections, selectedSection, onSelectSection, isLoading }) {
  if (isLoading) {
    return (
      <div className="p-4">
        <div className="animate-pulse space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-8 bg-gray-200 rounded" />
          ))}
        </div>
      </div>
    )
  }

  if (!sections || sections.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        <FileText className="w-12 h-12 mx-auto mb-2 text-gray-300" />
        <p className="text-sm">No sections found</p>
      </div>
    )
  }

  return (
    <div className="py-2">
      <div className="px-3 py-2 border-b border-gray-200 mb-2">
        <h3 className="font-semibold text-sm text-gray-700">Document Structure</h3>
        <p className="text-xs text-gray-500 mt-1">{sections.length} top-level sections</p>
      </div>

      {sections.map((section) => (
        <TreeNode
          key={section.id}
          section={section}
          selectedSection={selectedSection}
          onSelectSection={onSelectSection}
        />
      ))}
    </div>
  )
}
