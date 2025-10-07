import React, { useState } from 'react';
import { Upload, MessageCircle, BarChart3, Settings, FileText, Brain, Database, TrendingUp, Search, ChevronRight, File, Users, Clock, Zap, Monitor, Download, Play, CheckCircle, XCircle, AlertCircle, Loader2, ExternalLink, Copy, Terminal, Send, Bot, User, Sparkles, Star, ThumbsUp, ThumbsDown, RotateCcw, Eye, Trash2, X, Check, Filter, Calendar, Wifi, HardDrive, Cpu } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Area, AreaChart } from 'recharts';

const CompleteRAGSystem = () => {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Navigation items
  const navigation = [
    { id: 'dashboard', name: 'หน้าหลัก', icon: BarChart3, description: 'ภาพรวมระบบ' },
    { id: 'upload', name: 'อัปโหลดเอกสาร', icon: Upload, description: 'จัดการไฟล์' },
    { id: 'chat', name: 'ถามคำถาม', icon: MessageCircle, description: 'แชทกับ AI' },
    { id: 'analytics', name: 'วิเคราะห์ข้อมูล', icon: BarChart3, description: 'สถิติและรายงาน' },
    { id: 'setup', name: 'ตั้งค่าระบบ', icon: Settings, description: 'ติดตั้งและกำหนดค่า' }
  ];

  // Dashboard Component
  const Dashboard = () => {
    const [stats] = useState({
      totalDocuments: 1247,
      totalChunks: 18493,
      totalQueries: 856,
      avgConfidence: 0.87
    });

    const [quickStats] = useState([
      { label: 'เอกสารทั้งหมด', value: '1,247', icon: FileText, color: 'bg-blue-500', change: '+12%' },
      { label: 'Chunks ข้อมูล', value: '18.4K', icon: Database, color: 'bg-green-500', change: '+8%' },
      { label: 'คำถามวันนี้', value: '156', icon: MessageCircle, color: 'bg-purple-500', change: '+24%' },
      { label: 'ความแม่นยำ', value: '87%', icon: Brain, color: 'bg-orange-500', change: '+3%' }
    ]);

    const [popularQuestions] = useState([
      'สรุปข้อมูลการขายในเดือนนี้',
      'มีข้อมูลเกี่ยวกับ Machine Learning อะไรบ้าง',
      'แนวโน้มตลาดในอนาคตเป็นอย่างไร',
      'ข้อมูลลูกค้าในไฟล์ Excel มีอะไรบ้าง'
    ]);

    const StatCard = ({ label, value, icon: Icon, color, change }) => (
      <div className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow duration-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 mb-1">{label}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            {change && (
              <p className="text-sm text-green-600 mt-1">
                <TrendingUp className="inline w-4 h-4 mr-1" />
                {change}
              </p>
            )}
          </div>
          <div className={`${color} p-3 rounded-lg`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
        </div>
      </div>
    );

    return (
      <div className="p-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-2">สวัสดี! ยินดีต้อนรับสู่ RAG System</h2>
                <p className="text-blue-100 mb-6">ระบบตอบคำถามอัจฉริยะจากเอกสารของคุณ พร้อมใช้งานแล้ว!</p>
                <div className="flex space-x-4">
                  <button 
                    onClick={() => setCurrentPage('upload')}
                    className="bg-white text-blue-600 px-6 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors flex items-center space-x-2"
                  >
                    <Upload className="w-5 h-5" />
                    <span>อัปโหลดเอกสาร</span>
                  </button>
                  <button 
                    onClick={() => setCurrentPage('chat')}
                    className="bg-blue-700 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-800 transition-colors flex items-center space-x-2"
                  >
                    <MessageCircle className="w-5 h-5" />
                    <span>ถามคำถาม</span>
                  </button>
                </div>
              </div>
              <div className="hidden lg:block">
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
                  <BarChart3 className="w-16 h-16 text-white/80" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {quickStats.map((stat, index) => (
            <StatCard key={index} {...stat} />
          ))}
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">การดำเนินการด่วน</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div 
              onClick={() => setCurrentPage('upload')}
              className="flex flex-col items-center p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all cursor-pointer group"
            >
              <Upload className="w-8 h-8 text-blue-600 mb-3" />
              <h4 className="font-medium text-gray-900 mb-1">อัปโหลดเอกสาร</h4>
              <p className="text-sm text-gray-500 text-center">เพิ่มไฟล์ใหม่เข้าระบบ</p>
            </div>
            
            <div 
              onClick={() => setCurrentPage('chat')}
              className="flex flex-col items-center p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-400 hover:bg-green-50 transition-all cursor-pointer group"
            >
              <MessageCircle className="w-8 h-8 text-green-600 mb-3" />
              <h4 className="font-medium text-gray-900 mb-1">ถามคำถาม</h4>
              <p className="text-sm text-gray-500 text-center">สนทนากับ AI</p>
            </div>
            
            <div 
              onClick={() => setCurrentPage('analytics')}
              className="flex flex-col items-center p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-400 hover:bg-purple-50 transition-all cursor-pointer group"
            >
              <BarChart3 className="w-8 h-8 text-purple-600 mb-3" />
              <h4 className="font-medium text-gray-900 mb-1">ดูการวิเคราะห์</h4>
              <p className="text-sm text-gray-500 text-center">สถิติการใช้งาน</p>
            </div>
            
            <div 
              onClick={() => setCurrentPage('setup')}
              className="flex flex-col items-center p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-orange-400 hover:bg-orange-50 transition-all cursor-pointer group"
            >
              <Settings className="w-8 h-8 text-orange-600 mb-3" />
              <h4 className="font-medium text-gray-900 mb-1">ตั้งค่าระบบ</h4>
              <p className="text-sm text-gray-500 text-center">กำหนดค่าการทำงาน</p>
            </div>
          </div>
        </div>

        {/* Popular Questions */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">คำถามยอดนิยม</h3>
          <div className="space-y-3">
            {popularQuestions.map((question, index) => (
              <div 
                key={index}
                onClick={() => setCurrentPage('chat')}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-blue-50 cursor-pointer transition-colors group"
              >
                <p className="text-sm text-gray-700 group-hover:text-blue-700">{question}</p>
                <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-blue-500" />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  // Simple Upload Component
  const UploadPage = () => {
    const [dragActive, setDragActive] = useState(false);
    
    return (
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">อัปโหลดเอกสาร</h1>
          <p className="text-gray-600">ลากไฟล์มาวางหรือเลือกเพื่ออัปโหลดเอกสารสู่ระบบ RAG</p>
        </div>

        <div className="max-w-4xl mx-auto">
          <div
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-all duration-200 ${
              dragActive
                ? 'border-blue-400 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <div className="space-y-4">
              <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                <Upload className="w-8 h-8 text-blue-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  ลากไฟล์มาวางที่นี่
                </h3>
                <p className="text-gray-600 mb-4">
                  หรือ{' '}
                  <button className="text-blue-600 hover:text-blue-700 font-medium">
                    เลือกไฟล์จากเครื่อง
                  </button>
                </p>
                <div className="text-sm text-gray-500">
                  รองรับไฟล์: PDF, Word, Excel, CSV, JSON, Text, Markdown
                  <br />
                  ขนาดไฟล์สูงสุด: 50MB ต่อไฟล์
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <FileText className="w-8 h-8 text-blue-500 mb-3" />
              <h3 className="font-medium text-gray-900 mb-2">เอกสารข้อความ</h3>
              <p className="text-sm text-gray-600">PDF, Word, Text, Markdown</p>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <Database className="w-8 h-8 text-green-500 mb-3" />
              <h3 className="font-medium text-gray-900 mb-2">ข้อมูลตาราง</h3>
              <p className="text-sm text-gray-600">Excel, CSV, JSON</p>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <Brain className="w-8 h-8 text-purple-500 mb-3" />
              <h3 className="font-medium text-gray-900 mb-2">AI Processing</h3>
              <p className="text-sm text-gray-600">แยกข้อมูลเป็น chunks อัตโนมัติ</p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Simple Chat Component
  const ChatPage = () => {
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([
      {
        id: 1,
        type: 'ai',
        content: 'สวัสดีครับ! ผมเป็น AI ผู้ช่วยที่จะช่วยตอบคำถามจากเอกสารของคุณ มีอะไรให้ผมช่วยไหมครับ?',
        timestamp: new Date()
      }
    ]);

    const handleSend = () => {
      if (!message.trim()) return;
      
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'user',
        content: message,
        timestamp: new Date()
      }]);
      setMessage('');
      
      // Simulate AI response
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          type: 'ai',
          content: 'ขอบคุณสำหรับคำถามครับ! ผมกำลังค้นหาข้อมูลในเอกสารให้คุณ ในระบบจริงจะมีการเชื่อมต่อกับ LM Studio และ Vector Database เพื่อให้คำตอบที่แม่นยำ',
          timestamp: new Date(),
          sources: [
            { fileName: 'document1.pdf', similarity: 0.92 },
            { fileName: 'data.csv', similarity: 0.87 }
          ]
        }]);
      }, 1500);
    };

    return (
      <div className="flex h-screen bg-gray-50">
        <div className="flex-1 flex flex-col">
          <div className="bg-white border-b p-6">
            <h1 className="text-2xl font-bold text-gray-900">AI Assistant</h1>
            <p className="text-gray-600">ถามคำถามเกี่ยวกับเอกสารของคุณ</p>
          </div>

          <div className="flex-1 overflow-y-auto p-6">
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`flex max-w-xl ${msg.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${msg.type === 'user' ? 'ml-3 bg-blue-600' : 'mr-3 bg-purple-600'}`}>
                      {msg.type === 'user' ? 
                        <User className="w-5 h-5 text-white" /> : 
                        <Bot className="w-5 h-5 text-white" />
                      }
                    </div>
                    <div className={`p-4 rounded-2xl ${
                      msg.type === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-white border shadow-sm'
                    }`}>
                      <p className="text-sm">{msg.content}</p>
                      {msg.sources && (
                        <div className="mt-3 pt-3 border-t">
                          <p className="text-xs text-gray-600 mb-2">แหล่งข้อมูล:</p>
                          {msg.sources.map((source, i) => (
                            <div key={i} className="text-xs bg-gray-50 p-2 rounded mb-1">
                              📄 {source.fileName} ({(source.similarity * 100).toFixed(0)}%)
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white border-t p-6">
            <div className="max-w-3xl mx-auto flex space-x-4">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="พิมพ์คำถามของคุณที่นี่..."
                className="flex-1 p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
              <button
                onClick={handleSend}
                className="bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 transition-colors"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Simple Analytics Component
  const AnalyticsPage = () => {
    const data = [
      { name: 'จ', queries: 45, uploads: 12 },
      { name: 'อ', queries: 52, uploads: 8 },
      { name: 'พ', queries: 38, uploads: 15 },
      { name: 'พฤ', queries: 61, uploads: 18 },
      { name: 'ศ', queries: 49, uploads: 11 },
      { name: 'ส', queries: 73, uploads: 22 },
      { name: 'อา', queries: 67, uploads: 19 }
    ];

    return (
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">การวิเคราะห์ข้อมูล</h1>
          <p className="text-gray-600">ภาพรวมการใช้งานระบบ RAG และประสิทธิภาพ</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">คำถามทั้งหมด</p>
                <p className="text-3xl font-bold text-gray-900">2,847</p>
                <p className="text-sm text-green-600 mt-1">+12.5%</p>
              </div>
              <MessageCircle className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">เอกสารทั้งหมด</p>
                <p className="text-3xl font-bold text-gray-900">1,247</p>
                <p className="text-sm text-green-600 mt-1">+8.2%</p>
              </div>
              <FileText className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">เวลาตอบเฉลี่ย</p>
                <p className="text-3xl font-bold text-gray-900">2.3 วิ</p>
                <p className="text-sm text-green-600 mt-1">-5.1%</p>
              </div>
              <Clock className="w-8 h-8 text-orange-600" />
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">ความแม่นยำ</p>
                <p className="text-3xl font-bold text-gray-900">89.2%</p>
                <p className="text-sm text-green-600 mt-1">+3.4%</p>
              </div>
              <Brain className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">แนวโน้มการใช้งาน</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="queries" stroke="#3b82f6" fillOpacity={1} fill="url(#colorQueries)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  };

  // Simple Setup Component
  const SetupPage = () => {
    const [systemStatus, setSystemStatus] = useState({
      lmstudio: 'connected',
      vectordb: 'connected',
      embedding: 'connected'
    });

    return (
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">ตั้งค่าระบบ</h1>
          <p className="text-gray-600">ตรวจสอบสถานะและกำหนดค่าระบบ RAG</p>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">สถานะระบบ</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-6 bg-green-50 rounded-lg">
                <div className="w-12 h-12 bg-green-500 rounded-full mx-auto mb-3 flex items-center justify-center">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <div className="font-medium text-green-900">LM Studio</div>
                <div className="text-sm text-green-700 mt-1">เชื่อมต่อแล้ว</div>
              </div>
              
              <div className="text-center p-6 bg-green-50 rounded-lg">
                <div className="w-12 h-12 bg-green-500 rounded-full mx-auto mb-3 flex items-center justify-center">
                  <Database className="w-6 h-6 text-white" />
                </div>
                <div className="font-medium text-green-900">Vector Database</div>
                <div className="text-sm text-green-700 mt-1">พร้อมใช้งาน</div>
              </div>
              
              <div className="text-center p-6 bg-green-50 rounded-lg">
                <div className="w-12 h-12 bg-green-500 rounded-full mx-auto mb-3 flex items-center justify-center">
                  <Cpu className="w-6 h-6 text-white" />
                </div>
                <div className="font-medium text-green-900">Embedding Model</div>
                <div className="text-sm text-green-700 mt-1">โหลดแล้ว</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">การตั้งค่า</h3>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">ขนาด Chunk</label>
                <input type="number" defaultValue="1000" className="w-full p-3 border border-gray-300 rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Chunk Overlap</label>
                <input type="number" defaultValue="200" className="w-full p-3 border border-gray-300 rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Batch Size</label>
                <input type="number" defaultValue="50" className="w-full p-3 border border-gray-300 rounded-lg" />
              </div>
              <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
                บันทึกการตั้งค่า
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'dashboard': return <Dashboard />;
      case 'upload': return <UploadPage />;
      case 'chat': return <ChatPage />;
      case 'analytics': return <AnalyticsPage />;
      case 'setup': return <SetupPage />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className={`${sidebarCollapsed ? 'w-16' : 'w-64'} bg-white border-r border-gray-200 flex flex-col transition-all duration-300`}>
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            {!sidebarCollapsed && (
              <h1 className="text-xl font-bold text-gray-900">RAG System</h1>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <div className="space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentPage(item.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-3 rounded-lg text-left transition-colors ${
                    isActive
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  {!sidebarCollapsed && (
                    <div>
                      <div className="font-medium">{item.name}</div>
                      <div className="text-xs text-gray-500">{item.description}</div>
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </nav>

        {/* Status */}
        <div className="p-4 border-t border-gray-200">
          <div className={`flex items-center space-x-2 bg-green-100 text-green-800 px-3 py-2 rounded-lg ${sidebarCollapsed ? 'justify-center' : ''}`}>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            {!sidebarCollapsed && (
              <span className="text-sm font-medium">ระบบพร้อมใช้งาน</span>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="p-2 text-gray-500 hover:text-gray-700"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                {navigation.find(item => item.id === currentPage)?.name}
              </div>
              <button className="p-2 text-gray-400 hover:text-gray-500">
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main>
          {renderCurrentPage()}
        </main>
      </div>
    </div>
  );
};

export default CompleteRAGSystem;