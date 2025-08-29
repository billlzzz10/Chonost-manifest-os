import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { 
  Plus, 
  CheckCircle, 
  XCircle, 
  Settings,
  Trash2,
  TestTube
} from 'lucide-react'

export function Connections() {
  const [connections, setConnections] = useState([])
  const [supportedServices, setSupportedServices] = useState({})
  const [loading, setLoading] = useState(false)
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [selectedService, setSelectedService] = useState('')
  const [connectionForm, setConnectionForm] = useState({
    api_key: '',
    access_token: '',
    connection_config: {}
  })

  useEffect(() => {
    fetchConnections()
    fetchSupportedServices()
  }, [])

  const fetchConnections = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/connections?user_id=1')
      const data = await response.json()
      if (data.success) {
        setConnections(data.data)
      }
    } catch (error) {
      console.error('Error fetching connections:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchSupportedServices = async () => {
    try {
      const response = await fetch('/api/connections/services')
      const data = await response.json()
      if (data.success) {
        setSupportedServices(data.data)
      }
    } catch (error) {
      console.error('Error fetching supported services:', error)
    }
  }

  const createConnection = async () => {
    if (!selectedService) return

    try {
      const response = await fetch('/api/connections', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 1,
          service_name: selectedService,
          ...connectionForm
        }),
      })

      const data = await response.json()
      if (data.success) {
        setConnections(prev => [data.data, ...prev])
        setShowAddDialog(false)
        setSelectedService('')
        setConnectionForm({
          api_key: '',
          access_token: '',
          connection_config: {}
        })
      } else {
        alert(data.error || 'เกิดข้อผิดพลาดในการสร้างการเชื่อมต่อ')
      }
    } catch (error) {
      console.error('Error creating connection:', error)
      alert('เกิดข้อผิดพลาดในการสร้างการเชื่อมต่อ')
    }
  }

  const testConnection = async (connectionId) => {
    try {
      const response = await fetch(`/api/connections/${connectionId}/test`, {
        method: 'POST',
      })
      const data = await response.json()
      if (data.success) {
        alert(`การทดสอบสำเร็จ: ${data.data.message}`)
        fetchConnections() // Refresh to update last_used_at
      } else {
        alert('การทดสอบล้มเหลว')
      }
    } catch (error) {
      console.error('Error testing connection:', error)
      alert('เกิดข้อผิดพลาดในการทดสอบการเชื่อมต่อ')
    }
  }

  const deleteConnection = async (connectionId) => {
    if (!confirm('คุณแน่ใจหรือไม่ที่จะลบการเชื่อมต่อนี้?')) return

    try {
      const response = await fetch(`/api/connections/${connectionId}`, {
        method: 'DELETE',
      })
      const data = await response.json()
      if (data.success) {
        setConnections(prev => prev.filter(conn => conn.id !== connectionId))
      }
    } catch (error) {
      console.error('Error deleting connection:', error)
    }
  }

  const getServiceIcon = (serviceName) => {
    // Return appropriate icon based on service name
    // For now, just return a generic icon
    return '🔗'
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'ไม่เคยใช้งาน'
    return new Date(dateString).toLocaleDateString('th-TH')
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">การเชื่อมต่อ</h2>
            <p className="text-gray-600 mt-1">จัดการการเชื่อมต่อกับบริการต่างๆ</p>
          </div>
          
          <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                เพิ่มการเชื่อมต่อ
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>เพิ่มการเชื่อมต่อใหม่</DialogTitle>
                <DialogDescription>
                  เลือกบริการที่ต้องการเชื่อมต่อและกรอกข้อมูลที่จำเป็น
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="service">เลือกบริการ</Label>
                  <select
                    id="service"
                    value={selectedService}
                    onChange={(e) => setSelectedService(e.target.value)}
                    className="w-full mt-1 p-2 border border-gray-300 rounded-md"
                  >
                    <option value="">เลือกบริการ</option>
                    {Object.entries(supportedServices).map(([key, service]) => (
                      <option key={key} value={key}>
                        {service.display_name}
                      </option>
                    ))}
                  </select>
                </div>

                {selectedService && supportedServices[selectedService]?.auth_type === 'api_key' && (
                  <div>
                    <Label htmlFor="api_key">API Key</Label>
                    <Input
                      id="api_key"
                      type="password"
                      value={connectionForm.api_key}
                      onChange={(e) => setConnectionForm(prev => ({
                        ...prev,
                        api_key: e.target.value
                      }))}
                      placeholder="กรอก API Key"
                    />
                  </div>
                )}

                {selectedService && supportedServices[selectedService]?.auth_type === 'oauth' && (
                  <div className="text-sm text-gray-600">
                    การเชื่อมต่อแบบ OAuth จะเปิดหน้าต่างใหม่เพื่อให้คุณอนุญาตการเข้าถึง
                  </div>
                )}

                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setShowAddDialog(false)}>
                    ยกเลิก
                  </Button>
                  <Button 
                    onClick={createConnection}
                    disabled={!selectedService || (supportedServices[selectedService]?.auth_type === 'api_key' && !connectionForm.api_key)}
                  >
                    เชื่อมต่อ
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Connections List */}
      <ScrollArea className="flex-1 p-6">
        {loading ? (
          <div className="text-center py-8 text-gray-500">กำลังโหลด...</div>
        ) : connections.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">🔗</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              ยังไม่มีการเชื่อมต่อ
            </h3>
            <p className="text-gray-500 mb-4">
              เริ่มต้นโดยการเพิ่มการเชื่อมต่อกับบริการที่คุณใช้งาน
            </p>
            <Button onClick={() => setShowAddDialog(true)}>
              <Plus className="mr-2 h-4 w-4" />
              เพิ่มการเชื่อมต่อแรก
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {connections.map((connection) => (
              <Card key={connection.id} className="relative">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">
                        {getServiceIcon(connection.service_name)}
                      </div>
                      <div>
                        <CardTitle className="text-lg">
                          {connection.service_display_name}
                        </CardTitle>
                        <CardDescription>
                          {supportedServices[connection.service_name]?.description}
                        </CardDescription>
                      </div>
                    </div>
                    
                    <Badge variant={connection.has_valid_token ? "default" : "destructive"}>
                      {connection.has_valid_token ? (
                        <CheckCircle className="w-3 h-3 mr-1" />
                      ) : (
                        <XCircle className="w-3 h-3 mr-1" />
                      )}
                      {connection.has_valid_token ? 'เชื่อมต่อแล้ว' : 'ขาดการเชื่อมต่อ'}
                    </Badge>
                  </div>
                </CardHeader>
                
                <CardContent>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div>สร้างเมื่อ: {formatDate(connection.created_at)}</div>
                    <div>ใช้งานล่าสุด: {formatDate(connection.last_used_at)}</div>
                  </div>
                  
                  <div className="flex space-x-2 mt-4">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => testConnection(connection.id)}
                    >
                      <TestTube className="w-4 h-4 mr-1" />
                      ทดสอบ
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                    >
                      <Settings className="w-4 h-4 mr-1" />
                      ตั้งค่า
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => deleteConnection(connection.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
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

