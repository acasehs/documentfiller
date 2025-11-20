import { useState, useEffect } from 'react'
import { FileText, Plus, Edit, Trash2, Copy, Globe, Lock, Save, X } from 'lucide-react'
import axios from 'axios'

interface Template {
  id: number
  name: string
  description: string
  content: string
  is_public: boolean
  is_owner: boolean
  created_at: string
  updated_at: string
}

export default function PromptTemplates() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [loading, setLoading] = useState(false)

  // Form state
  const [formName, setFormName] = useState('')
  const [formDescription, setFormDescription] = useState('')
  const [formContent, setFormContent] = useState('')
  const [formIsPublic, setFormIsPublic] = useState(false)

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      const response = await axios.get('/api/templates/')
      setTemplates(response.data)
    } catch (err) {
      console.error('Failed to load templates:', err)
    }
  }

  const handleCreateNew = () => {
    setIsCreating(true)
    setIsEditing(false)
    setSelectedTemplate(null)
    setFormName('')
    setFormDescription('')
    setFormContent('')
    setFormIsPublic(false)
  }

  const handleEdit = (template: Template) => {
    if (!template.is_owner) return

    setIsEditing(true)
    setIsCreating(false)
    setSelectedTemplate(template)
    setFormName(template.name)
    setFormDescription(template.description)
    setFormContent(template.content)
    setFormIsPublic(template.is_public)
  }

  const handleSave = async () => {
    setLoading(true)
    try {
      if (isCreating) {
        await axios.post('/api/templates/', {
          name: formName,
          description: formDescription,
          content: formContent,
          is_public: formIsPublic,
        })
      } else if (isEditing && selectedTemplate) {
        await axios.put(`/api/templates/${selectedTemplate.id}`, {
          name: formName,
          description: formDescription,
          content: formContent,
          is_public: formIsPublic,
        })
      }

      await loadTemplates()
      handleCancel()
    } catch (err) {
      console.error('Failed to save template:', err)
      alert('Failed to save template')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this template?')) return

    setLoading(true)
    try {
      await axios.delete(`/api/templates/${id}`)
      await loadTemplates()
      if (selectedTemplate?.id === id) {
        setSelectedTemplate(null)
      }
    } catch (err) {
      console.error('Failed to delete template:', err)
      alert('Failed to delete template')
    } finally {
      setLoading(false)
    }
  }

  const handleDuplicate = async (template: Template) => {
    const newName = prompt('Enter name for duplicated template:', `${template.name} (Copy)`)
    if (!newName) return

    setLoading(true)
    try {
      await axios.post(`/api/templates/${template.id}/duplicate`, null, {
        params: { new_name: newName }
      })
      await loadTemplates()
    } catch (err) {
      console.error('Failed to duplicate template:', err)
      alert('Failed to duplicate template')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setIsCreating(false)
    setIsEditing(false)
    setSelectedTemplate(null)
  }

  const handleSelectTemplate = (template: Template) => {
    if (!isEditing && !isCreating) {
      setSelectedTemplate(template)
    }
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FileText className="w-8 h-8 text-purple-500" />
            <div>
              <h2 className="text-3xl font-bold text-white">Prompt Templates</h2>
              <p className="text-slate-400">Create and manage reusable prompt templates</p>
            </div>
          </div>
          <button
            onClick={handleCreateNew}
            disabled={isEditing || isCreating}
            className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            <Plus className="w-5 h-5" />
            <span>New Template</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Template List */}
        <div className="col-span-4 space-y-3">
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 overflow-hidden">
            <div className="p-4 border-b border-slate-700">
              <h3 className="font-semibold text-white">Templates ({templates.length})</h3>
            </div>
            <div className="max-h-[600px] overflow-y-auto">
              {templates.length === 0 ? (
                <div className="p-8 text-center text-slate-400">
                  <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>No templates yet</p>
                  <p className="text-sm mt-1">Click "New Template" to create one</p>
                </div>
              ) : (
                templates.map((template) => (
                  <div
                    key={template.id}
                    onClick={() => handleSelectTemplate(template)}
                    className={`p-4 border-b border-slate-700/50 cursor-pointer transition-colors ${
                      selectedTemplate?.id === template.id
                        ? 'bg-purple-600/20 border-l-4 border-l-purple-600'
                        : 'hover:bg-slate-700/30'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-semibold text-white">{template.name}</h4>
                          {template.is_public ? (
                            <Globe className="w-4 h-4 text-green-400" title="Public" />
                          ) : (
                            <Lock className="w-4 h-4 text-slate-400" title="Private" />
                          )}
                        </div>
                        {template.description && (
                          <p className="text-sm text-slate-400 mt-1 line-clamp-2">
                            {template.description}
                          </p>
                        )}
                        <p className="text-xs text-slate-500 mt-2">
                          {template.is_owner ? 'Your template' : 'Public template'}
                        </p>
                      </div>
                      {template.is_owner && (
                        <div className="flex items-center space-x-1 ml-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleEdit(template)
                            }}
                            className="p-1 hover:bg-slate-600 rounded transition-colors"
                            title="Edit"
                          >
                            <Edit className="w-4 h-4 text-slate-400" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDelete(template.id)
                            }}
                            className="p-1 hover:bg-red-600 rounded transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4 text-red-400" />
                          </button>
                        </div>
                      )}
                      {!template.is_owner && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDuplicate(template)
                          }}
                          className="p-1 hover:bg-slate-600 rounded transition-colors"
                          title="Duplicate to your templates"
                        >
                          <Copy className="w-4 h-4 text-slate-400" />
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Template Editor/Viewer */}
        <div className="col-span-8">
          {isCreating || isEditing ? (
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-white">
                  {isCreating ? 'Create New Template' : 'Edit Template'}
                </h3>
                <button
                  onClick={handleCancel}
                  className="p-2 hover:bg-slate-700 rounded transition-colors"
                >
                  <X className="w-5 h-5 text-slate-400" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Template Name
                  </label>
                  <input
                    type="text"
                    value={formName}
                    onChange={(e) => setFormName(e.target.value)}
                    className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="e.g., DoD Compliance Template"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formDescription}
                    onChange={(e) => setFormDescription(e.target.value)}
                    className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                    rows={2}
                    placeholder="Brief description of this template..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Prompt Content
                  </label>
                  <textarea
                    value={formContent}
                    onChange={(e) => setFormContent(e.target.value)}
                    className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
                    rows={15}
                    placeholder="You are a technical writer specializing in {{TOPIC}}...&#10;&#10;Available variables:&#10;- {{SECTION_TITLE}}&#10;- {{DOCUMENT_TITLE}}&#10;- {{TOPIC}}&#10;- {{CUSTOM_VAR}}"
                  />
                  <p className="text-sm text-slate-400 mt-2">
                    Use {`{{VARIABLE_NAME}}`} for dynamic values
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="is_public"
                    checked={formIsPublic}
                    onChange={(e) => setFormIsPublic(e.target.checked)}
                    className="rounded"
                  />
                  <label htmlFor="is_public" className="text-sm text-slate-300 cursor-pointer">
                    Make this template public (others can view and duplicate)
                  </label>
                </div>

                <div className="flex items-center justify-end space-x-3 pt-4">
                  <button
                    onClick={handleCancel}
                    className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={loading || !formName || !formContent}
                    className="flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50"
                  >
                    <Save className="w-4 h-4" />
                    <span>{loading ? 'Saving...' : 'Save Template'}</span>
                  </button>
                </div>
              </div>
            </div>
          ) : selectedTemplate ? (
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-2xl font-bold text-white">{selectedTemplate.name}</h3>
                    {selectedTemplate.is_public ? (
                      <Globe className="w-5 h-5 text-green-400" title="Public template" />
                    ) : (
                      <Lock className="w-5 h-5 text-slate-400" title="Private template" />
                    )}
                  </div>
                  {selectedTemplate.description && (
                    <p className="text-slate-400 mt-2">{selectedTemplate.description}</p>
                  )}
                  <p className="text-sm text-slate-500 mt-2">
                    {selectedTemplate.is_owner ? 'Your template' : 'Public template'} •
                    Created {new Date(selectedTemplate.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  {!selectedTemplate.is_owner && (
                    <button
                      onClick={() => handleDuplicate(selectedTemplate)}
                      className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                    >
                      <Copy className="w-4 h-4" />
                      <span>Duplicate</span>
                    </button>
                  )}
                  {selectedTemplate.is_owner && (
                    <button
                      onClick={() => handleEdit(selectedTemplate)}
                      className="flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                    >
                      <Edit className="w-4 h-4" />
                      <span>Edit</span>
                    </button>
                  )}
                </div>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-slate-300 mb-2">Prompt Content</h4>
                <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
                  <pre className="text-sm text-slate-300 whitespace-pre-wrap font-mono">
                    {selectedTemplate.content}
                  </pre>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-12 border border-slate-700 flex items-center justify-center h-full">
              <div className="text-center text-slate-400">
                <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg">Select a template to view details</p>
                <p className="text-sm mt-2">Or create a new one to get started</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
