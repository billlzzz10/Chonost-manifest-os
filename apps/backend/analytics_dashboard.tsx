import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Area, AreaChart } from 'recharts';
import { TrendingUp, FileText, MessageCircle, Clock, Users, Database, Search, Filter, Download, Calendar, Eye, Brain } from 'lucide-react';

const AnalyticsDashboard = () => {
  const [timeRange, setTimeRange] = useState('7days');
  const [selectedMetric, setSelectedMetric] = useState('queries');

  // ข้อมูลจำลองสำหรับกราฟ
  const documentTypeData = [
    { name: 'PDF', value: 45, count: 562, color: '#ef4444' },
    { name: 'Word', value: 25, count: 312, color: '#3b82f6' },
    { name: 'Excel', value: 15, count: 187, color: '#10b981' },
    { name: 'CSV', value: 8, count: 99, color: '#f59e0b' },
    { name: 'Text', value: 4, count: 50, color: '#8b5cf6' },
    { name: 'JSON', value: 3, count: 37, color: '#06b6d4' }
  ];

  const queryTrendData = [
    { date: '15 ม.ค.', queries: 45, uploads: 12, success: 42 },
    { date: '16 ม.ค.', queries: 52, uploads: 8, success: 48 },
    { date: '17 ม.ค.', queries: 38, uploads: 15, success: 35 },
    { date: '18 ม.ค.', queries: 61, uploads: 18, success: 58 },
    { date: '19 ม.ค.', queries: 49, uploads: 11, success: 46 },
    { date: '20 ม.ค.', queries: 73, uploads: 22, success: 69 },
    { date: '21 ม.ค.', queries: 67, uploads: 19, success: 63 }
  ];

  const topQueriesData = [
    { query: 'สรุปข้อมูลการขาย', count: 156, avgConfidence: 0.92 },
    { query: 'วิเคราะห์ข้อมูล AI', count: 134, avgConfidence: 0.87 },
    { query: 'ข้อมูลลูกค้า', count: 98, avgConfidence: 0.91 },
    { query: 'แนวโน้มตลาด', count: 87, avgConfidence: 0.84 },
    { query: 'รายงานการเงิน', count: 76, avgConfidence: 0.89 }
  ];

  const performanceData = [
    { hour: '00:00', responseTime: 1.2, queries: 5 },
    { hour: '03:00', responseTime: 1.1, queries: 8 },
    { hour: '06:00', responseTime: 1.5, queries: 15 },
    { hour: '09:00', responseTime: 2.1, queries: 45 },
    { hour: '12:00', responseTime: 2.8, queries: 67 },
    { hour: '15:00', responseTime: 2.3, queries: 52 },
    { hour: '18:00', responseTime: 1.9, queries: 38 },
    { hour: '21:00', responseTime: 1.4, queries: 22 }
  ];

  const keyMetrics = [
    {
      title: 'คำถามทั้งหมด',
      value: '2,847',
      change: '+12.5%',
      changeType: 'positive',
      icon: MessageCircle,
      color: 'bg-blue-500'
    },
    {
      title: 'เอกสารที่ประมวลผล',
      value: '1,247',
      change: '+8.2%',
      changeType: 'positive',
      icon: FileText,
      color: 'bg-green-500'
    },
    {
      title: 'เวลาตอบเฉลี่ย',
      value: '2.3 วิ',
      change: '-5.1%',
      changeType: 'positive',
      icon: Clock,
      color: 'bg-orange-500'
    },
    {
      title: 'ความแม่นยำ',
      value: '89.2%',
      change: '+3.4%',
      changeType: 'positive',
      icon: Brain,
      color: 'bg-purple-500'
    }
  ];

  const recentDocuments = [
    { name: 'quarterly_report.pdf', size: '2.4 MB', chunks: 45, uploadTime: '10 นาทีที่แล้ว', queries: 23 },
    { name: 'meeting_notes.docx', size: '156 KB', chunks: 12, uploadTime: '1 ชั่วโมงที่แล้ว', queries: 8 },
    { name: 'sales_analysis.xlsx', size: '892 KB', chunks: 34, uploadTime: '3 ชั่วโมงที่แล้ว', queries: 15 },
    { name: 'customer_data.csv', size: '445 KB', chunks: 18, uploadTime: '5 ชั่วโมงที่แล้ว', queries: 12 },
    { name: 'market_research.pdf', size: '3.1 MB', chunks: 67, uploadTime: '1 วันที่แล้ว', queries: 31 }
  ];

  const MetricCard = ({ metric }) => {
    const Icon = metric.icon;
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 mb-1">{metric.title}</p>
            <p className="text-3xl font-bold text-gray-900">{metric.value}</p>
            <div className={`flex items-center mt-2 text-sm ${
              metric.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
            }`}>
              <TrendingUp className="w-4 h-4 mr-1" />
              <span>{metric.change}</span>
            </div>
          </div>
          <div className={`${metric.color} p-3 rounded-lg`}>
            <Icon className="w-8 h-8 text-white" />
          </div>
        </div>
      </div>
    );
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-medium">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">การวิเคราะห์ข้อมูล</h1>
              <p className="text-gray-600">ภาพรวมการใช้งานระบบ RAG และประสิทธิภาพ</p>
            </div>
            <div className="flex items-center space-x-4">
              <select 
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="bg-white border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="24hours">24 ชั่วโมงที่แล้ว</option>
                <option value="7days">7 วันที่แล้ว</option>
                <option value="30days">30 วันที่แล้ว</option>
                <option value="90days">3 เดือนที่แล้ว</option>
              </select>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>ส่งออกรายงาน</span>
              </button>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {keyMetrics.map((metric, index) => (
            <MetricCard key={index} metric={metric} />
          ))}
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Query Trends */}
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">แนวโน้มการใช้งาน</h3>
              <div className="flex space-x-2">
                <button 
                  onClick={() => setSelectedMetric('queries')}
                  className={`px-3 py-1 rounded-full text-sm ${
                    selectedMetric === 'queries' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  คำถาม
                </button>
                <button 
                  onClick={() => setSelectedMetric('uploads')}
                  className={`px-3 py-1 rounded-full text-sm ${
                    selectedMetric === 'uploads' ? 'bg-green-100 text-green-700' : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  อัปโหลด
                </button>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={queryTrendData}>
                <defs>
                  <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                  </linearGradient>
                  <linearGradient id="colorUploads" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip content={<CustomTooltip />} />
                <Area 
                  type="monotone" 
                  dataKey={selectedMetric} 
                  stroke={selectedMetric === 'queries' ? '#3b82f6' : '#10b981'} 
                  fillOpacity={1} 
                  fill={selectedMetric === 'queries' ? 'url(#colorQueries)' : 'url(#colorUploads)'} 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Document Types */}
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">ประเภทเอกสาร</h3>
            <div className="flex items-center">
              <div className="flex-1">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={documentTypeData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {documentTypeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="w-40 space-y-3">
                {documentTypeData.map((item, index) => (
                  <div key={index} className="flex items-center">
                    <div 
                      className="w-3 h-3 rounded-full mr-3" 
                      style={{ backgroundColor: item.color }}
                    ></div>
                    <div className="text-sm">
                      <div className="font-medium text-gray-900">{item.name}</div>
                      <div className="text-gray-500">{item.count} ไฟล์</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Performance Chart */}
        <div className="bg-white rounded-xl p-6 shadow-sm mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">ประสิทธิภาพระบบ</h3>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis yAxisId="left" orientation="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip content={<CustomTooltip />} />
              <Bar yAxisId="right" dataKey="queries" fill="#e5e7eb" name="จำนวนคำถาม" />
              <Line 
                yAxisId="left" 
                type="monotone" 
                dataKey="responseTime" 
                stroke="#ef4444" 
                strokeWidth={3}
                name="เวลาตอบ (วิ)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Top Queries */}
          <div className="bg-white rounded-xl shadow-sm">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">คำถามยอดนิยม</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {topQueriesData.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{item.query}</div>
                      <div className="text-sm text-gray-500 mt-1">
                        {item.count} ครั้ง • ความแม่นยำ {(item.avgConfidence * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">{index + 1}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Documents */}
          <div className="bg-white rounded-xl shadow-sm">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">เอกสารล่าสุด</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {recentDocuments.map((doc, index) => (
                  <div key={index} className="flex items-center space-x-4 p-3 hover:bg-gray-50 rounded-lg">
                    <div className="flex-shrink-0">
                      <FileText className="w-8 h-8 text-blue-500" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-900 truncate">{doc.name}</div>
                      <div className="text-sm text-gray-500">
                        {doc.size} • {doc.chunks} chunks • {doc.uploadTime}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900">{doc.queries}</div>
                      <div className="text-xs text-gray-500">คำถาม</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="mt-8 bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">สถานะระบบ</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="w-12 h-12 bg-green-500 rounded-full mx-auto mb-3 flex items-center justify-center">
                <Database className="w-6 h-6 text-white" />
              </div>
              <div className="font-medium text-green-900">Vector Database</div>
              <div className="text-sm text-green-700 mt-1">ปกติ • 18.4K chunks</div>
            </div>
            
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="w-12 h-12 bg-blue-500 rounded-full mx-auto mb-3 flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div className="font-medium text-blue-900">LM Studio</div>
              <div className="text-sm text-blue-700 mt-1">เชื่อมต่อ • Qwen2.5-14B</div>
            </div>
            
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="w-12 h-12 bg-purple-500 rounded-full mx-auto mb-3 flex items-center justify-center">
                <Search className="w-6 h-6 text-white" />
              </div>
              <div className="font-medium text-purple-900">Embedding Model</div>
              <div className="text-sm text-purple-700 mt-1">พร้อมใช้ • MiniLM-L6-v2</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;