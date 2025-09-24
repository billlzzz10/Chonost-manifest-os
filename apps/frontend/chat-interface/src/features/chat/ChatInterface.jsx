import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { ScrollArea } from '@/shared/ui/scroll-area'
import { Send, Bot } from 'lucide-react'
import MessageItem from './MessageItem'

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
  }, [selectedChatId, fetchMessages])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  const fetchMessages = useCallback(async () => {
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
  }, [selectedChatId])

  const sendMessage = useCallback(async () => {
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
  }, [currentMessage, selectedChatId, sending])

  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }, [sendMessage])

  const formatTime = useCallback((timestamp) => 
    new Date(timestamp).toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' }), [])

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
              <MessageItem 
                key={message.id} 
                message={message} 
                formatTime={formatTime} 
              />
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

