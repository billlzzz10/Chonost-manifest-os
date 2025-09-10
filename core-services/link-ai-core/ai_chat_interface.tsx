import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, FileText, Clock, Star, Copy, ThumbsUp, ThumbsDown, RotateCcw, Sparkles } from 'lucide-react';

const AIChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: 'สวัสดีครับ! ผมเป็น AI ผู้ช่วยที่จะช่วยตอบคำถามจากเอกสารของคุณ มีอะไรให้ผมช่วยไหมครับ?',
      timestamp: new Date(),
      sources: []
    }
  ]);
  
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const [suggestedQuestions] = useState([
    'สรุปข้อมูลยอดขายในไตรมาสนี้',
    'มีข้อมูลเกี่ยวกับ Machine Learning อะไรบ้าง?',
    'แนวโน้มตลาดในอนาคตเป็นอย่างไร?',
    'ข้อมูลลูกค้าในไฟล์ Excel มีอะไรบ้าง?',
    'สรุปจุดสำคัญในเอกสารการประชุม',
    'วิเคราะห์ข้อมูลการเงินล่าสุด'
  ]);

  const [conversationHistory, setConversationHistory] = useState([
    {
      id: 1,
      title: 'สรุปข้อมูลการขาย',
      date: '15 ม.ค. 2024',
      preview: 'ยอดขายไตรมาส 3 เพิ่มขึ้น 15%...'
    },
    {
      id: 2,
      title: 'วิเคราะห์ตลาด AI',
      date: '14 ม.ค. 2024',
      preview: 'ตลาด AI คาดว่าจะเติบโต 25% ในปีนี้...'
    },
    {
      id: 3,
      title: 'ข้อมูลลูกค้า',
      date: '13 ม.ค. 2024',
      preview: 'ลูกค้าใหม่เพิ่มขึ้น 200 ราย...'
    }
  ]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // จำลองการตอบกลับของ AI
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        type: 'ai',
        content: generateAIResponse(userMessage.content),
        timestamp: new Date(),
        sources: [
          {
            fileName: 'quarterly_report.pdf',
            similarity: 0.92,
            page: 15
          },
          {
            fileName: 'sales_data.csv',
            similarity: 0.87,
            page: null
          }
        ],
        confidence: 0.89
      };

      setMessages(prev => [...prev, aiResponse]);
      setIsLoading(false);
    }, 1500 + Math.random() * 1000);
  };

  const generateAIResponse = (question) => {
    const responses = {
      'ขาย': 'จากข้อมูลในเอกสาร พบว่ายอดขายในไตรมาสที่ 3 มีการเติบโตขึ้น 15% เมื่อเทียบกับไตรมาสก่อนหน้า โดยสินค้าหมวด A มียอดขายสูงสุดที่ 2.5 ล้านบาท ตามด้วยหมวด B ที่ 1.8 ล้านบาท',
      'AI': 'ในเอกสารมีการกล่าวถึง Machine Learning ในหลายบริบท ได้แก่ การใช้งาน Natural Language Processing สำหรับวิเคราะห์ข้อมูล, Computer Vision สำหรับระบบจดจำภาพ, และ Predictive Analytics สำหรับการพยากรณ์ยอดขาย',
      'ตลาด': 'แนวโน้มตลาดจากการวิเคราะห์ในเอกสารแสดงให้เห็นว่า ตลาดเทคโนโลยีคาดว่าจะเติบโตต่อเนื่องในอัตรา 25% ต่อปี โดยเฉพาะในส่วนของ Cloud Computing และ AI Technology',
      'ลูกค้า': 'ข้อมูลลูกค้าในไฟล์ Excel แสดงให้เห็นว่า มีลูกค้าใหม่เพิ่มขึ้น 200 ราย ในเดือนนี้ โดยส่วนใหญ่เป็นลูกค้าจากภาคเหนือ (45%) รองลงมาคือภาคกลาง (30%) และภาคใต้ (25%)'
    };

    // หาคำตอบที่เหมาะสมที่สุด
    for (const [key, response] of Object.entries(responses)) {
      if (question.toLowerCase().includes(key.toLowerCase())) {
        return response;
      }
    }

    return 'ขออภัยครับ จากการค้นหาในเอกสารไม่พบข้อมูลที่เกี่ยวข้องโดยตรงกับคำถามของคุณ กรุณาลองถามในรูปแบบอื่นหรือให้รายละเอียดเพิ่มเติมครับ';
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const copyMessage = (content) => {
    navigator.clipboard.writeText(content);
  };

  const MessageBubble = ({ message, isUser = false }) => (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div className={`flex max-w-3xl ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
            isUser ? 'bg-blue-600' : 'bg-gradient-to-br from-purple-600 to-blue-600'
          }`}>
            {isUser ? (
              <User className="w-6 h-6 text-white" />
            ) : (
              <Bot className="w-6 h-6 text-white" />
            )}
          </div>
        </div>

        {/* Message Content */}
        <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
          <div className={`inline-block p-4 rounded-2xl max-w-full ${
            isUser 
              ? 'bg-blue-600 text-white' 
              : 'bg-white border shadow-sm'
          }`}>
            <div className="text-sm leading-relaxed whitespace-pre-wrap">
              {message.content}
            </div>
            
            {/* AI Message Extras */}
            {!isUser && (
              <div className="mt-3 space-y-3">
                {/* Confidence Score */}
                {message.confidence && (
                  <div className="flex items-center space-x-2 text-xs text-gray-600">
                    <Sparkles className="w-4 h-4" />
                    <span>ความมั่นใจ: {(message.confidence * 100).toFixed(0)}%</span>
                  </div>
                )}

                {/* Sources */}
                {message.sources && message.sources.length > 0 && (
                  <div className="border-t pt-3">
                    <div className="text-xs text-gray-600 mb-2 font-medium">แหล่งข้อมูล:</div>
                    <div className="space-y-1">
                      {message.sources.map((source, index) => (
                        <div key={index} className="flex items-center space-x-2 text-xs bg-gray-50 p-2 rounded-lg">
                          <FileText className="w-4 h-4 text-gray-400" />
                          <span className="font-medium">{source.fileName}</span>
                          <span className="text-gray-500">
                            ({(source.similarity * 100).toFixed(0)}% ความเกี่ยวข้อง)
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex items-center space-x-2 pt-2 border-t">
                  <button 
                    onClick={() => copyMessage(message.content)}
                    className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                    title="คัดลอก"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button className="p-1 text-gray-400 hover:text-green-600 transition-colors" title="ถูกต้อง">
                    <ThumbsUp className="w-4 h-4" />
                  </button>
                  <button className="p-1 text-gray-400 hover:text-red-600 transition-colors" title="ไม่ถูกต้อง">
                    <ThumbsDown className="w-4 h-4" />
                  </button>
                  <button className="p-1 text-gray-400 hover:text-blue-600 transition-colors" title="ถามใหม่">
                    <RotateCcw className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Timestamp */}
          <div className={`mt-1 text-xs text-gray-500 ${isUser ? 'text-right' : 'text-left'}`}>
            <Clock className="inline w-3 h-3 mr-1" />
            {message.timestamp.toLocaleTimeString('th-TH', { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-2">ประวัติการสนทนา</h2>
          <button className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2">
            <Sparkles className="w-4 h-4" />
            <span>เริ่มการสนทนาใหม่</span>
          </button>
        </div>

        {/* Conversation History */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {conversationHistory.map((conversation) => (
            <div key={conversation.id} className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
              <h3 className="font-medium text-gray-900 text-sm">{conversation.title}</h3>
              <p className="text-xs text-gray-600 mt-1 line-clamp-2">{conversation.preview}</p>
              <div className="flex items-center justify-between mt-2">
                <span className="text-xs text-gray-500">{conversation.date}</span>
                <Star className="w-4 h-4 text-gray-300 hover:text-yellow-400 cursor-pointer" />
              </div>
            </div>
          ))}
        </div>

        {/* Suggested Questions */}
        <div className="p-4 border-t border-gray-200">
          <h3 className="font-medium text-gray-900 mb-3 text-sm">คำถามแนะนำ</h3>
          <div className="space-y-2">
            {suggestedQuestions.slice(0, 3).map((question, index) => (
              <button
                key={index}
                onClick={() => setInputValue(question)}
                className="w-full text-left text-sm text-gray-600 hover:text-blue-600 p-2 rounded hover:bg-blue-50 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="bg-white border-b border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AI Assistant</h1>
              <p className="text-gray-600">ถามคำถามเกี่ยวกับเอกสารของคุณ</p>
            </div>
            <div className="flex items-center space-x-2 bg-green-50 text-green-700 px-4 py-2 rounded-full">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">1,247 เอกสารพร้อมใช้</span>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto">
            {messages.map((message) => (
              <MessageBubble 
                key={message.id} 
                message={message} 
                isUser={message.type === 'user'} 
              />
            ))}
            
            {/* Loading Message */}
            {isLoading && (
              <div className="flex justify-start mb-6">
                <div className="flex">
                  <div className="mr-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
                      <Bot className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <div className="bg-white border shadow-sm p-4 rounded-2xl">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                      <span className="text-sm text-gray-600">กำลังค้นหาข้อมูล...</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 p-6">
          <div className="max-w-4xl mx-auto">
            <div className="flex space-x-4">
              <div className="flex-1 relative">
                <textarea
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="พิมพ์คำถามของคุณที่นี่..."
                  className="w-full p-4 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  rows={1}
                  style={{ minHeight: '56px', maxHeight: '120px' }}
                />
              </div>
              <button
                onClick={handleSend}
                disabled={!inputValue.trim() || isLoading}
                className="bg-blue-600 text-white p-4 rounded-xl hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            
            {/* Quick Actions */}
            <div className="mt-4 flex flex-wrap gap-2">
              {suggestedQuestions.slice(0, 4).map((question, index) => (
                <button
                  key={index}
                  onClick={() => setInputValue(question)}
                  className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded-full transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIChatInterface;