import { useState, useEffect } from 'react'
import { useNavigate, useLocation, useParams } from 'react-router-dom'
import { Button } from '../../shared/ui/button'
import { ScrollArea } from '../../shared/ui/scroll-area'
import { 
  MessageSquare, 
  Link, 
  Zap, 
  Settings, 
  Plus,
  MoreHorizontal,
  Trash2,
  Edit,
  Files,
  Template,
  Brain
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../../shared/ui/dropdown-menu'

export function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  const { sessionId } = useParams()
  const [chatSessions, setChatSessions] = useState([])
  const [loading, setLoading] = useState(false)

  const menuItems = [
    { id: 'chat', label: 'แชต', icon: MessageSquare, path: '/chat' },
    { id: 'files', label: 'ไฟล์', icon: Files, path: '/files' },
    { id: 'agents', label: 'Agent Builder', icon: Brain, path: '/agents' },
    { id: 'connections', label: 'การเชื่อมต่อ', icon: Link, path: '/connections' },
    { id: 'automations', label: 'อัตโนมัติ', icon: Zap, path: '/automations' },
    { id: 'templates', label: 'เทมเพลต', icon: Template, path: '/templates' },
    { id: 'settings', label: 'ตั้งค่า', icon: Settings, path: '/settings' },
  ]

  const currentView = location.pathname.split('/')[1] || 'chat'

  useEffect(() => {
    if (currentView === 'chat') {
      fetchChatSessions()
    }
  }, [currentView])

  const fetchChatSessions = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/chat/sessions?user_id=1')
      const data = await response.json()
      if (data.success) {
        setChatSessions(data.data)
      }
    } catch (error) {
      console.error('Error fetching chat sessions:', error)
    } finally {
      setLoading(false)
    }
  }

  const createNewChat = async () => {
    try {
      const response = await fetch('/api/chat/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 1,
          title: 'แชตใหม่'
        }),
      })
      const data = await response.json()
      if (data.success) {
        setChatSessions(prev => [data.data, ...prev])
        navigate(`/chat/${data.data.id}`)
      }
    } catch (error) {
      console.error('Error creating new chat:', error)
    }
  }

  const deleteChat = async (chatId) => {
    try {
      const response = await fetch(`/api/chat/sessions/${chatId}`, {
        method: 'DELETE',
      })
      const data = await response.json()
      if (data.success) {
        setChatSessions(prev => prev.filter(chat => chat.id !== chatId))
        if (sessionId === chatId) {
          navigate('/chat')
        }
      }
    } catch (error) {
      console.error('Error deleting chat:', error)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now - date)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 1) return 'วันนี้'
    if (diffDays === 2) return 'เมื่อวาน'
    if (diffDays <= 7) return `${diffDays - 1} วันที่แล้ว`
    return date.toLocaleDateString('th-TH')
  }

  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-900">Chat Integration</h1>
      </div>

      {/* Navigation */}
      <div className="p-4 border-b border-gray-200">
        <nav className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = currentView === item.id
            return (
              <Button
                key={item.id}
                variant={isActive ? "default" : "ghost"}
                className="w-full justify-start"
                onClick={() => navigate(item.path)}
              >
                <Icon className="mr-2 h-4 w-4" />
                {item.label}
              </Button>
            )
          })}
        </nav>
      </div>

      {/* Chat Sessions */}
      {currentView === 'chat' && (
        <div className="flex-1 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <Button 
              onClick={createNewChat}
              className="w-full"
              disabled={loading}
            >
              <Plus className="mr-2 h-4 w-4" />
              แชตใหม่
            </Button>
          </div>

          <ScrollArea className="flex-1">
            <div className="p-2">
              {loading ? (
                <div className="text-center py-4 text-gray-500">กำลังโหลด...</div>
              ) : chatSessions.length === 0 ? (
                <div className="text-center py-4 text-gray-500">ไม่มีแชต</div>
              ) : (
                <div className="space-y-1">
                  {chatSessions.map((chat) => (
                    <div
                      key={chat.id}
                      className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
                        sessionId === chat.id
                          ? 'bg-blue-50 border border-blue-200'
                          : 'hover:bg-gray-50'
                      }`}
                      onClick={() => navigate(`/chat/${chat.id}`)}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-sm text-gray-900 truncate">
                          {chat.title}
                        </div>
                        <div className="text-xs text-gray-500">
                          {formatDate(chat.updated_at)} • {chat.message_count} ข้อความ
                        </div>
                      </div>
                      
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>
                            <Edit className="mr-2 h-4 w-4" />
                            แก้ไขชื่อ
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            className="text-red-600"
                            onClick={() => deleteChat(chat.id)}
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            ลบ
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </ScrollArea>
        </div>
      )}
    </div>
  )
}
