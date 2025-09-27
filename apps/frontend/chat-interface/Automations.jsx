import { useState, useEffect } from 'react'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Badge } from '@/shared/ui/badge'
import { ScrollArea } from '@/shared/ui/scroll-area'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Textarea } from '@/shared/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/shared/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/shared/ui/dropdown-menu'
import { 
  Plus, 
  Play, 
  Pause, 
  Settings,
  Trash2,
  MoreHorizontal,
  Clock,
  Zap,
  CheckCircle,
  XCircle
} from 'lucide-react'

export function Automations() {
  const [workflows, setWorkflows] = useState([])
  const [loading, setLoading] = useState(false)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [workflowForm, setWorkflowForm] = useState({
    name: '',
    description: '',
    trigger_type: 'manual'
  })

  useEffect(() => {
    fetchWorkflows()
  }, [])

  const fetchWorkflows = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/workflows?user_id=1')
      const data = await response.json()
      if (data.success) {
        setWorkflows(data.data)
      }
    } catch (error) {
      console.error('Error fetching workflows:', error)
    } finally {
      setLoading(false)
    }
  }

  const createWorkflow = async () => {
    if (!workflowForm.name.trim()) return

    try {
      const response = await fetch('/api/workflows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 1,
          ...workflowForm
        }),
      })

      const data = await response.json()
      if (data.success) {
        setWorkflows(prev => [data.data, ...prev])
        setShowCreateDialog(false)
        setWorkflowForm({
          name: '',
          description: '',
          trigger_type: 'manual'
        })
      }
    } catch (error) {
      console.error('Error creating workflow:', error)
    }
  }

  const executeWorkflow = async (workflowId) => {
    try {
      const response = await fetch(`/api/workflows/${workflowId}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          trigger_data: {
            manual_trigger: true,
            timestamp: new Date().toISOString()
          }
        }),
      })

      const data = await response.json()
      if (data.success) {
        alert('Workflow executed successfully!')
        fetchWorkflows() // Refresh to update run count
      }
    } catch (error) {
      console.error('Error executing workflow:', error)
    }
  }

  const toggleWorkflow = async (workflowId, isActive) => {
    try {
      const response = await fetch(`/api/workflows/${workflowId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          is_active: !isActive
        }),
      })

      const data = await response.json()
      if (data.success) {
        setWorkflows(prev => prev.map(workflow => 
          workflow.id === workflowId 
            ? { ...workflow, is_active: !isActive }
            : workflow
        ))
      }
    } catch (error) {
      console.error('Error toggling workflow:', error)
    }
  }

  const deleteWorkflow = async (workflowId) => {
    if (!confirm('คุณแน่ใจหรือไม่ที่จะลบ workflow นี้?')) return

    try {
      const response = await fetch(`/api/workflows/${workflowId}`, {
        method: 'DELETE',
      })
      const data = await response.json()
      if (data.success) {
        setWorkflows(prev => prev.filter(workflow => workflow.id !== workflowId))
      }
    } catch (error) {
      console.error('Error deleting workflow:', error)
    }
  }

  const getTriggerIcon = (triggerType) => {
    switch (triggerType) {
      case 'schedule':
        return <Clock className="w-4 h-4" />
      case 'webhook':
        return <Zap className="w-4 h-4" />
      default:
        return <Play className="w-4 h-4" />
    }
  }

  const getTriggerLabel = (triggerType) => {
    switch (triggerType) {
      case 'schedule':
        return 'ตามกำหนดเวลา'
      case 'webhook':
        return 'Webhook'
      case 'event':
        return 'เหตุการณ์'
      default:
        return 'ด้วยตนเอง'
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'ไม่เคยรัน'
    return new Date(dateString).toLocaleDateString('th-TH', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">อัตโนมัติ</h2>
            <p className="text-gray-600 mt-1">สร้างและจัดการ workflow อัตโนมัติ</p>
          </div>
          
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                สร้าง Workflow
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>สร้าง Workflow ใหม่</DialogTitle>
                <DialogDescription>
                  สร้าง workflow อัตโนมัติเพื่อเชื่อมต่อและทำงานกับบริการต่างๆ
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">ชื่อ Workflow</Label>
                  <Input
                    id="name"
                    value={workflowForm.name}
                    onChange={(e) => setWorkflowForm(prev => ({
                      ...prev,
                      name: e.target.value
                    }))}
                    placeholder="กรอกชื่อ workflow"
                  />
                </div>

                <div>
                  <Label htmlFor="description">คำอธิบาย</Label>
                  <Textarea
                    id="description"
                    value={workflowForm.description}
                    onChange={(e) => setWorkflowForm(prev => ({
                      ...prev,
                      description: e.target.value
                    }))}
                    placeholder="อธิบายการทำงานของ workflow"
                    rows={3}
                  />
                </div>

                <div>
                  <Label htmlFor="trigger_type">ประเภทการเรียกใช้</Label>
                  <select
                    id="trigger_type"
                    value={workflowForm.trigger_type}
                    onChange={(e) => setWorkflowForm(prev => ({
                      ...prev,
                      trigger_type: e.target.value
                    }))}
                    className="w-full mt-1 p-2 border border-gray-300 rounded-md"
                  >
                    <option value="manual">ด้วยตนเอง</option>
                    <option value="schedule">ตามกำหนดเวลา</option>
                    <option value="webhook">Webhook</option>
                    <option value="event">เหตุการณ์</option>
                  </select>
                </div>

                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                    ยกเลิก
                  </Button>
                  <Button 
                    onClick={createWorkflow}
                    disabled={!workflowForm.name.trim()}
                  >
                    สร้าง
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Workflows List */}
      <ScrollArea className="flex-1 p-6">
        {loading ? (
          <div className="text-center py-8 text-gray-500">กำลังโหลด...</div>
        ) : workflows.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">⚡</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              ยังไม่มี Workflow
            </h3>
            <p className="text-gray-500 mb-4">
              สร้าง workflow อัตโนมัติเพื่อเชื่อมต่อและทำงานกับบริการต่างๆ
            </p>
            <Button onClick={() => setShowCreateDialog(true)}>
              <Plus className="mr-2 h-4 w-4" />
              สร้าง Workflow แรก
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {workflows.map((workflow) => (
              <Card key={workflow.id} className="relative">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <CardTitle className="text-lg">{workflow.name}</CardTitle>
                        <Badge variant={workflow.is_active ? "default" : "secondary"}>
                          {workflow.is_active ? (
                            <CheckCircle className="w-3 h-3 mr-1" />
                          ) : (
                            <XCircle className="w-3 h-3 mr-1" />
                          )}
                          {workflow.is_active ? 'เปิดใช้งาน' : 'ปิดใช้งาน'}
                        </Badge>
                      </div>
                      <CardDescription className="mt-1">
                        {workflow.description || 'ไม่มีคำอธิบาย'}
                      </CardDescription>
                    </div>
                    
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => toggleWorkflow(workflow.id, workflow.is_active)}>
                          {workflow.is_active ? (
                            <>
                              <Pause className="mr-2 h-4 w-4" />
                              ปิดใช้งาน
                            </>
                          ) : (
                            <>
                              <Play className="mr-2 h-4 w-4" />
                              เปิดใช้งาน
                            </>
                          )}
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Settings className="mr-2 h-4 w-4" />
                          แก้ไข
                        </DropdownMenuItem>
                        <DropdownMenuItem 
                          className="text-red-600"
                          onClick={() => deleteWorkflow(workflow.id)}
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          ลบ
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardHeader>
                
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      {getTriggerIcon(workflow.trigger_type)}
                      <span>ประเภท: {getTriggerLabel(workflow.trigger_type)}</span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">จำนวนขั้นตอน:</span>
                        <div className="font-medium">{workflow.step_count || 0} ขั้นตอน</div>
                      </div>
                      <div>
                        <span className="text-gray-500">รันแล้ว:</span>
                        <div className="font-medium">{workflow.run_count || 0} ครั้ง</div>
                      </div>
                    </div>
                    
                    <div className="text-sm text-gray-600">
                      <span className="text-gray-500">รันล่าสุด:</span>
                      <div>{formatDate(workflow.last_run_at)}</div>
                    </div>
                  </div>
                  
                  <div className="flex space-x-2 mt-4">
                    <Button
                      size="sm"
                      onClick={() => executeWorkflow(workflow.id)}
                      disabled={!workflow.is_active}
                    >
                      <Play className="w-4 h-4 mr-1" />
                      รัน
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                    >
                      <Settings className="w-4 h-4 mr-1" />
                      แก้ไข
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  )
}

