import React, { useState, useEffect } from "react";
import {
  Upload,
  MessageCircle,
  BarChart3,
  Settings,
  FileText,
  Brain,
  Database,
  TrendingUp,
  Search,
  ChevronRight,
  File,
  Users,
  Clock,
  Zap,
} from "lucide-react";

const RAGDashboard = () => {
  const [stats, setStats] = useState({
    totalDocuments: 1247,
    totalChunks: 18493,
    totalQueries: 856,
    avgConfidence: 0.87,
  });

  const [recentActivity, setRecentActivity] = useState([
    { type: "upload", file: "quarterly_report.pdf", time: "5 นาทีที่แล้ว" },
    { type: "query", question: "สรุปยอดขายในไตรมาส 3", time: "12 นาทีที่แล้ว" },
    { type: "upload", file: "meeting_notes.docx", time: "1 ชั่วโมงที่แล้ว" },
    {
      type: "query",
      question: "มีข้อมูลเกี่ยวกับ AI อะไรบ้าง",
      time: "2 ชั่วโมงที่แล้ว",
    },
  ]);

  const [quickStats, setQuickStats] = useState([
    {
      label: "เอกสารทั้งหมด",
      value: "1,247",
      icon: FileText,
      color: "bg-blue-500",
      change: "+12%",
    },
    {
      label: "Chunks ข้อมูล",
      value: "18.4K",
      icon: Database,
      color: "bg-green-500",
      change: "+8%",
    },
    {
      label: "คำถามวันนี้",
      value: "156",
      icon: MessageCircle,
      color: "bg-purple-500",
      change: "+24%",
    },
    {
      label: "ความแม่นยำ",
      value: "87%",
      icon: Brain,
      color: "bg-orange-500",
      change: "+3%",
    },
  ]);

  const [popularQuestions, setPopularQuestions] = useState([
    "สรุปข้อมูลการขายในเดือนนี้",
    "มีข้อมูลเกี่ยวกับ Machine Learning อะไรบ้าง",
    "แนวโน้มตลาดในอนาคตเป็นอย่างไร",
    "ข้อมูลลูกค้าในไฟล์ Excel มีอะไรบ้าง",
  ]);

  const [currentPage, setCurrentPage] = useState("dashboard");

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

  const ActivityItem = ({ activity }) => (
    <div className="flex items-center space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
      <div
        className={`p-2 rounded-lg ${
          activity.type === "upload" ? "bg-blue-100" : "bg-green-100"
        }`}
      >
        {activity.type === "upload" ? (
          <Upload
            className={`w-4 h-4 ${
              activity.type === "upload" ? "text-blue-600" : "text-green-600"
            }`}
          />
        ) : (
          <MessageCircle className="w-4 h-4 text-green-600" />
        )}
      </div>
      <div className="flex-1">
        <p className="text-sm font-medium text-gray-900">
          {activity.type === "upload"
            ? `อัปโหลด ${activity.file}`
            : `ถาม: ${activity.question}`}
        </p>
        <p className="text-xs text-gray-500">{activity.time}</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Brain className="w-8 h-8 text-blue-600" />
                <h1 className="text-xl font-bold text-gray-900">RAG System</h1>
              </div>
              <nav className="hidden md:flex space-x-8">
                <button
                  onClick={() => setCurrentPage("dashboard")}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    currentPage === "dashboard"
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  หน้าหลัก
                </button>
                <button
                  onClick={() => setCurrentPage("upload")}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    currentPage === "upload"
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  อัปโหลดเอกสาร
                </button>
                <button
                  onClick={() => setCurrentPage("chat")}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    currentPage === "chat"
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  ถามคำถาม
                </button>
                <button
                  onClick={() => setCurrentPage("analytics")}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    currentPage === "analytics"
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  วิเคราะห์ข้อมูล
                </button>
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 bg-green-100 text-green-800 px-3 py-1 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium">ระบบพร้อมใช้งาน</span>
              </div>
              <button
                className="p-2 text-gray-400 hover:text-gray-500"
                title="ตั้งค่า"
              >
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-2">
                  สวัสดี! ยินดีต้อนรับสู่ RAG System
                </h2>
                <p className="text-blue-100 mb-6">
                  ระบบตอบคำถามอัจฉริยะจากเอกสารของคุณ พร้อมใช้งานแล้ว!
                </p>
                <div className="flex space-x-4">
                  <button
                    onClick={() => setCurrentPage("upload")}
                    className="bg-white text-blue-600 px-6 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors flex items-center space-x-2"
                  >
                    <Upload className="w-5 h-5" />
                    <span>อัปโหลดเอกสาร</span>
                  </button>
                  <button
                    onClick={() => setCurrentPage("chat")}
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

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">
                  การดำเนินการด่วน
                </h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div
                    onClick={() => setCurrentPage("upload")}
                    className="flex items-center space-x-4 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all cursor-pointer group"
                  >
                    <div className="bg-blue-100 group-hover:bg-blue-200 p-3 rounded-lg">
                      <Upload className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">
                        อัปโหลดเอกสารใหม่
                      </h4>
                      <p className="text-sm text-gray-500">
                        ลากไฟล์มาวางหรือเลือกจากเครื่อง
                      </p>
                    </div>
                  </div>

                  <div
                    onClick={() => setCurrentPage("chat")}
                    className="flex items-center space-x-4 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-400 hover:bg-green-50 transition-all cursor-pointer group"
                  >
                    <div className="bg-green-100 group-hover:bg-green-200 p-3 rounded-lg">
                      <MessageCircle className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">
                        ถามคำถามใหม่
                      </h4>
                      <p className="text-sm text-gray-500">
                        สอบถามข้อมูลจากเอกสารด้วย AI
                      </p>
                    </div>
                  </div>

                  <div
                    onClick={() => setCurrentPage("analytics")}
                    className="flex items-center space-x-4 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-400 hover:bg-purple-50 transition-all cursor-pointer group"
                  >
                    <div className="bg-purple-100 group-hover:bg-purple-200 p-3 rounded-lg">
                      <BarChart3 className="w-6 h-6 text-purple-600" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">
                        ดูการวิเคราะห์
                      </h4>
                      <p className="text-sm text-gray-500">
                        สถิติและกราฟการใช้งาน
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-orange-400 hover:bg-orange-50 transition-all cursor-pointer group">
                    <div className="bg-orange-100 group-hover:bg-orange-200 p-3 rounded-lg">
                      <Search className="w-6 h-6 text-orange-600" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">ค้นหาเอกสาร</h4>
                      <p className="text-sm text-gray-500">
                        ค้นหาไฟล์ตามชื่อหรือเนื้อหา
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Activity Feed */}
          <div className="space-y-6">
            {/* Popular Questions */}
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">
                  คำถามยอดนิยม
                </h3>
              </div>
              <div className="p-6">
                <div className="space-y-3">
                  {popularQuestions.map((question, index) => (
                    <div
                      key={index}
                      onClick={() => setCurrentPage("chat")}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-blue-50 cursor-pointer transition-colors group"
                    >
                      <p className="text-sm text-gray-700 group-hover:text-blue-700">
                        {question}
                      </p>
                      <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-blue-500" />
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">
                  กิจกรรมล่าสุด
                </h3>
              </div>
              <div className="p-6">
                <div className="space-y-1">
                  {recentActivity.map((activity, index) => (
                    <ActivityItem key={index} activity={activity} />
                  ))}
                </div>
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                    ดูกิจกรรมทั้งหมด →
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default RAGDashboard;
