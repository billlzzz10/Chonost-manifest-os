import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Plus, Edit, Trash2, Search, XCircle } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

export function AgentTemplates() {
  const { apiRequest } = useAuth()
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [currentTemplate, setCurrentTemplate] = useState(null)
  const [form, setForm] = useState({
    name: '',
    description: '',
    role: '',
    goal: '',
    initial_prompt: '',
    constraints: [],
    tools: [],
    knowledge_base_ids: [],
    output_format_instruction: '',
    custom_fields: {}
  })
  const [formError, setFormError] = useState('')

  useEffect(() => {
    fetchTemplates()
  }, [])

  const fetchTemplates = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await apiRequest('/api/agents/templates', { method: 'GET' })
      const result = await response.json()
      if (result.success) {
        setTemplates(result.data.templates)
      } else {
        setError(result.message || 'ไม่สามารถดึงรายการ Agent Templates ได้')
      }
    } catch (err) {
      setError('เกิดข้อผิดพลาดในการเชื่อมต่อ: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setForm(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleArrayInputChange = (name, value) => {
    setForm(prev => ({
      ...prev,
      [name]: value.split(',').map(item => item.trim()).filter(item => item !== '')
    }))
  }

  const handleCustomFieldsChange = (key, value) => {
    setForm(prev => ({
      ...prev,
      custom_fields: {
        ...prev.custom_fields,
        [key]: value
      }
    }))
  }

  const handleSaveTemplate = async () => {
    setFormError('')
    if (!form.name) {
      setFormError('กรุณาระบุชื่อ Template')
      return
    }

    try {
      let response
      if (currentTemplate) {
        response = await apiRequest(`/api/agents/templates/${currentTemplate.id}`, {
          method: 'PUT',
          body: JSON.stringify(form)
        })
      } else {
        response = await apiRequest('/api/agents/templates', {
          method: 'POST',
          body: JSON.stringify(form)
        })
      }
      const result = await response.json()
      if (result.success) {
        fetchTemplates()
        setIsDialogOpen(false)
        setCurrentTemplate(null)
        setFormError('')
      } else {
        setFormError(result.message || 'เกิดข้อผิดพลาดในการบันทึก Template')
      }
    } catch (err) {
      setFormError('เกิดข้อผิดพลาดในการเชื่อมต่อ: ' + err.message)
    }
  }

  const handleDeleteTemplate = async (templateId) => {
    if (!window.confirm('คุณแน่ใจหรือไม่ที่จะลบ Template นี้?')) {
      return
    }
    try {
      const response = await apiRequest(`/api/agents/templates/${templateId}`, { method: 'DELETE' })
      const result = await response.json()
      if (result.success) {
        fetchTemplates()
      } else {
        setError(result.message || 'ไม่สามารถลบ Template ได้')
      }
    } catch (err) {
      setError('เกิดข้อผิดพลาดในการลบ Template: ' + err.message)
    }
  }

  const handleEditTemplate = (template) => {
    setCurrentTemplate(template)
    setForm({
      name: template.name || '',
      description: template.description || '',
      role: template.role || '',
      goal: template.goal || '',
      initial_prompt: template.initial_prompt || '',
      constraints: template.constraints || [],
      tools: template.tools || [],
      knowledge_base_ids: template.knowledge_base_ids || [],
      output_format_instruction: template.output_format_instruction || '',
      custom_fields: template.custom_fields || {}
    })
    setIsDialogOpen(true)
  }

  const handleNewTemplate = () => {
    setCurrentTemplate(null)
    setForm({
      name: '',
      description: '',
      role: '',
      goal: '',
      initial_prompt: '',
      constraints: [],
      tools: [],
      knowledge_base_ids: [],
      output_format_instruction: '',
      custom_fields: {}
    })
    setFormError('')
    setIsDialogOpen(true)
  }

  return (
    <div className="flex flex-col h-full p-4 overflow-y-auto">
      <h1 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Agent Templates</h1>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        สร้างและจัดการ Agent Templates เพื่อกำหนดพฤติกรรมของ AI Agent ของคุณ
      </p>

      <div className="mb-6">
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={handleNewTemplate}>
              <Plus className="mr-2 h-4 w-4" /> สร้าง Template ใหม่
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>{currentTemplate ? 'แก้ไข Template' : 'สร้าง Template ใหม่'}</DialogTitle>
              <DialogDescription>
                {currentTemplate ? 'แก้ไขรายละเอียดของ Agent Template' : 'สร้าง Agent Template ใหม่เพื่อกำหนดพฤติกรรมของ AI Agent'}
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              {formError && (
                <Alert variant="destructive">
                  <XCircle className="h-4 w-4" />
                  <AlertDescription>{formError}</AlertDescription>
                </Alert>
              )}
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="name" className="text-right">ชื่อ</Label>
                <Input id="name" name="name" value={form.name} onChange={handleInputChange} className="col-span-3" />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="description" className="text-right">คำอธิบาย</Label>
                <Textarea id="description" name="description" value={form.description} onChange={handleInputChange} className="col-span-3" />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="role" className="text-right">บทบาท</Label>
                <Input id="role" name="role" value={form.role} onChange={handleInputChange} className="col-span-3" />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="goal" className="text-right">เป้าหมาย</Label>
                <Input id="goal" name="goal" value={form.goal} onChange={handleInputChange} className="col-span-3" />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="initial_prompt" className="text-right">Initial Prompt</Label>
                <Textarea id="initial_prompt" name="initial_prompt" value={form.initial_prompt} onChange={handleInputChange} className="col-span-3" />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="constraints" className="text-right">ข้อจำกัด (คั่นด้วยคอมมา)</Label>
                <Input id="constraints" name="constraints" value={form.constraints.join(', ')} onChange={(e) => handleArrayInputChange('constraints', e.target.value)} className="col-span-3" />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="tools" className="text-right">Tools (คั่นด้วยคอมมา)</Label>
                <Input id="tools" name="tools" value={form.tools.join(', ')} onChange={(e) => handleArrayInputChange('tools', e.target.value)} className="col-span-3" />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="knowledge_base_ids" className="text-right">Knowledge Base IDs (คั่นด้วยคอมมา)</Label>
                <Input id="knowledge_base_ids" name="knowledge_base_ids" value={form.knowledge_base_ids.join(', ')} onChange={(e) => handleArrayInputChange('knowledge_base_ids', e.target.value)} className="col-span-3" />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="output_format_instruction" className="text-right">Output Format Instruction</Label>
                <Textarea id="output_format_instruction" name="output_format_instruction" value={form.output_format_instruction} onChange={handleInputChange} className="col-span-3" />
              </div>
              {/* Custom Fields - simplified for now */}
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="custom_field_example" className="text-right">Custom Field (Example)</Label>
                <Input id="custom_field_example" value={form.custom_fields.example || ''} onChange={(e) => handleCustomFieldsChange('example', e.target.value)} className="col-span-3" />
              </div>
            </div>
            <DialogFooter>
              <Button type="submit" onClick={handleSaveTemplate}>บันทึก Template</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card className="flex-1">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="w-5 h-5" />
            รายการ Agent Templates
          </CardTitle>
          <CardDescription>
            Template ที่คุณสร้างขึ้นเพื่อใช้งานกับ AI Agent
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading && <p className="text-center text-gray-500">กำลังโหลด Templates...</p>}
          {error && (
            <Alert variant="destructive">
              <XCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          {!loading && templates.length === 0 && !error && (
            <p className="text-center text-gray-500">ยังไม่มี Agent Templates</p>
          )}
          <div className="space-y-3">
            {templates.map(template => (
              <div key={template.id} className="flex items-center justify-between p-3 border rounded-lg bg-gray-50 dark:bg-gray-800">
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 dark:text-white">{template.name}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 truncate">{template.description || 'ไม่มีคำอธิบาย'}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">บทบาท: {template.role || 'ไม่ได้ระบุ'}</p>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => handleEditTemplate(template)}>
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button variant="destructive" size="sm" onClick={() => handleDeleteTemplate(template.id)}>
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

