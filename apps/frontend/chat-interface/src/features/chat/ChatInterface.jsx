import { useState, useEffect, useRef } from 'react'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { ScrollArea } from '@/shared/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/shared/ui/avatar'
import { Send, Bot, User } from 'lucide-react'

export function ChatInterface({ selectedChatId, setSelectedChatId }) {
  const [messages, setMessages] = useState([])
  const [currentMessage, setCurrentMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    if (selectedChatId) {
      fetchMessages()
    } else {
      setMessages([])
    }
  }, [selectedChatId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchMessages = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/chat/sessions/${selectedChatId}`)
      const data = await response.json()
      if (data.success) {
        setMessages(data.data.messages || [])
      }
    } catch (error) {
      console.error('Error fetching messages:', error)
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!currentMessage.trim() || !selectedChatId || sending) return
    const messageContent = currentMessage.trim()
    setCurrentMessage('')
    setSending(true)
    try {
      const response = await fetch(`/api/chat/sessions/${selectedChatId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: messageContent, message_metadata: { timestamp: new Date().toISOString() } }),
      })
      const data = await response.json()
      if (data.success) {
        setMessages((prev) => [...prev, data.data])
        setTimeout(() => {
          const aiResponse = {
            id: Date.now(),
            chat_session_id: selectedChatId,
            content: `ขอบคุณสำหรับข้อความ: "${messageContent}" ฉันเป็น AI Assistant ที่สามารถช่วยคุณเชื่อมต่อและทำงานกับบริการต่างๆ ได้`,
            role: 'assistant',
            timestamp: new Date().toISOString(),
            message_metadata: {},
          }
          setMessages((prev) => [...prev, aiResponse])
        }, 1000)
      }
    } catch (error) {
      console.error('Error sending message:', error)
    } finally {
      setSending(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatTime = (timestamp) => new Date(timestamp).toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })

  if (!selectedChatId) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Bot className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">ยินดีต้อนรับสู่ Chat Integration</h3>
          <p className="text-gray-500 mb-4">เลือกแชตจากแถบด้านซ้าย หรือสร้างแชตใหม่เพื่อเริ่มต้น</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col">
      <div className="bg-white border-b border-gray-200 p-4">
        <h2 className="text-lg font-semibold text-gray-900">แชต</h2>
      </div>
      <ScrollArea className="flex-1 p-4">
        {loading ? (
          <div className="text-center py-8 text-gray-500">กำลังโหลดข้อความ...</div>
        ) : messages.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Bot className="mx-auto h-8 w-8 text-gray-400 mb-2" />
            เริ่มการสนทนาใหม่
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex max-w-[70%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  <Avatar className="w-8 h-8">
                    <AvatarFallback>
                      {message.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                    </AvatarFallback>
                  </Avatar>
                  <div className={`mx-2 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                    <div className={`inline-block p-3 rounded-lg ${message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-900'}`}>
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">{formatTime(message.timestamp)}</div>
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </ScrollArea>
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex space-x-2">
          <Input value={currentMessage} onChange={(e) => setCurrentMessage(e.target.value)} onKeyPress={handleKeyPress} placeholder="พิมพ์ข้อความ..." disabled={sending} className="flex-1" />
          <Button onClick={sendMessage} disabled={!currentMessage.trim() || sending} size="icon">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface

