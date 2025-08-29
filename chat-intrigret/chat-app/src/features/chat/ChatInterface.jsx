import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Send, Bot, User, Loader2 } from 'lucide-react'

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
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: messageContent,
          message_metadata: {
            timestamp: new Date().toISOString()
          }
        }),
      })

      const data = await response.json()
      if (data.success) {
        // Update messages with both user message and AI response
        if (data.data.user_message && data.data.ai_response) {
          setMessages(prev => [...prev, data.data.user_message, data.data.ai_response])
        } else if (data.data.user_message) {
          setMessages(prev => [...prev, data.data.user_message])
          
          // Show error if AI response failed
          if (data.data.ai_error) {
            console.error('AI Response Error:', data.data.ai_error)
            // Add error message
            const errorMessage = {
              id: Date.now(),
              chat_session_id: selectedChatId,
              content: 'ขออภัย เกิดข้อผิดพลาดในการสร้างคำตอบ กรุณาลองใหม่อีกครั้ง',
              role: 'assistant',
              timestamp: new Date().toISOString(),
              message_metadata: { error: true }
            }
            setMessages(prev => [...prev, errorMessage])
          }
        } else {
          // Handle single message response (backward compatibility)
          setMessages(prev => [...prev, data.data])
        }
      }
    } catch (error) {
      console.error('Error sending message:', error)
      // Add error message to chat
      const errorMessage = {
        id: Date.now(),
        chat_session_id: selectedChatId,
        content: 'เกิดข้อผิดพลาดในการส่งข้อความ กรุณาลองใหม่อีกครั้ง',
        role: 'assistant',
        timestamp: new Date().toISOString(),
        message_metadata: { error: true }
      }
      setMessages(prev => [...prev, errorMessage])
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

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('th-TH', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (!selectedChatId) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <Bot className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            ยินดีต้อนรับสู่ Chat Integration
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            เลือกแชตจากแถบด้านซ้าย หรือสร้างแชตใหม่เพื่อเริ่มต้น
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">แชต</h2>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4">
        {loading ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <Loader2 className="mx-auto h-6 w-6 animate-spin mb-2" />
            กำลังโหลดข้อความ...
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <Bot className="mx-auto h-8 w-8 text-gray-400 mb-2" />
            เริ่มการสนทนาใหม่
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex max-w-[70%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  <Avatar className="w-8 h-8">
                    <AvatarFallback className={message.message_metadata?.error ? 'bg-red-100 text-red-600' : ''}>
                      {message.role === 'user' ? (
                        <User className="w-4 h-4" />
                      ) : (
                        <Bot className="w-4 h-4" />
                      )}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className={`mx-2 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                    <div
                      className={`inline-block p-3 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-blue-500 text-white'
                          : message.message_metadata?.error
                          ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                          : 'bg-gray-100 text-gray-900 dark:bg-gray-700 dark:text-gray-100'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {formatTime(message.timestamp)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {sending && (
              <div className="flex justify-start">
                <div className="flex max-w-[70%]">
                  <Avatar className="w-8 h-8">
                    <AvatarFallback>
                      <Bot className="w-4 h-4" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="mx-2">
                    <div className="inline-block p-3 rounded-lg bg-gray-100 dark:bg-gray-700">
                      <div className="flex items-center space-x-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-gray-600 dark:text-gray-300">กำลังพิมพ์...</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </ScrollArea>

      {/* Input */}
      <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4">
        <div className="flex space-x-2">
          <Input
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="พิมพ์ข้อความ..."
            disabled={sending}
            className="flex-1"
          />
          <Button 
            onClick={sendMessage}
            disabled={!currentMessage.trim() || sending}
            size="icon"
          >
            {sending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}

