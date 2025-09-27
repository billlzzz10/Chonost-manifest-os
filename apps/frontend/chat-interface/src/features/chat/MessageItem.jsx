import React from 'react'
import { Avatar, AvatarFallback } from '@/shared/ui/avatar'
import { Bot, User } from 'lucide-react'

const MessageItem = React.memo(({ message, formatTime }) => {
  return (
    <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
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
  )
})

MessageItem.displayName = 'MessageItem'

export default MessageItem