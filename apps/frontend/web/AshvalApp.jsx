import React, { useState, useEffect } from 'react';
import './AshvalApp.css';

const AshvalApp = () => {
    const [currentView, setCurrentView] = useState('dashboard');
    const [isDark, setIsDark] = useState(false);
    const [showQuickAdd, setShowQuickAdd] = useState(false);
    const [currentMood, setCurrentMood] = useState(null);
    const [tasks, setTasks] = useState([]);
    const [aiLoading, setAiLoading] = useState(false);
    const [aiRecommendations, setAiRecommendations] = useState(null);

    const moods = [
        { id: 1, name: 'มีความสุข', emoji: '😊', description: 'รู้สึกดีและมีพลัง' },
        { id: 2, name: 'เครียด', emoji: '😰', description: 'รู้สึกกดดันและวิตกกังวล' },
        { id: 3, name: 'โฟกัส', emoji: '🎯', description: 'พร้อมทำงานและมีสมาธิ' },
        { id: 4, name: 'เบื่อ', emoji: '😑', description: 'รู้สึกไม่มีแรงบันดาลใจ' }
    ];

    useEffect(() => {
        const sampleTasks = [
            {
                id: 1,
                title: 'เรียนภาษาอังกฤษ',
                description: 'อ่านหนังสือและฝึกฟัง 30 นาที',
                status: 'doing',
                priority: 'high',
                completed: false,
                createdAt: new Date('2024-01-15')
            },
            {
                id: 2,
                title: 'ออกกำลังกาย',
                description: 'วิ่งเบาๆ 20 นาที',
                status: 'todo',
                priority: 'medium',
                completed: false,
                createdAt: new Date('2024-01-14')
            }
        ];
        setTasks(sampleTasks);
    }, []);

    const getViewTitle = () => {
        const titles = {
            dashboard: 'แดชบอร์ด',
            tasks: 'งานทั้งหมด',
            mood: 'อารมณ์วันนี้',
            ai: 'AI ผู้ช่วย'
        };
        return titles[currentView] || 'Ashval';
    };

    const toggleDarkMode = () => {
        setIsDark(!isDark);
        if (!isDark) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    };

    const getTotalTasks = () => tasks.length;
    const getCompletedTasks = () => tasks.filter(task => task.status === 'done').length;
    const getInProgressTasks = () => tasks.filter(task => task.status === 'doing').length;

    const toggleTaskComplete = (task) => {
        const updatedTasks = tasks.map(t => 
            t.id === task.id 
                ? { ...t, completed: !t.completed, status: !t.completed ? 'done' : 'todo' }
                : t
        );
        setTasks(updatedTasks);
    };

    const selectMood = (mood) => {
        setCurrentMood(mood);
    };

    const getAIRecommendations = async () => {
        if (!currentMood) return;
        setAiLoading(true);
        setAiRecommendations(null);
        
        setTimeout(() => {
            setAiRecommendations(
                <>
                    <h3>คำแนะนำสำหรับอารมณ์ {currentMood.name}</h3>
                    <p>เมื่อคุณรู้สึก{currentMood.description} เราแนะนำให้:</p>
                    <ul>
                        <li>ทำกิจกรรมที่ผ่อนคลาย</li>
                        <li>ฟังเพลงที่ชอบ</li>
                        <li>ออกไปเดินเล่น</li>
                    </ul>
                </>
            );
            setAiLoading(false);
        }, 2000);
    };

    return (
        <div className={`ashval-app ${isDark ? 'dark' : ''}`}>
            <div className="flex h-screen overflow-hidden">
                {/* Sidebar */}
                <div className="w-64 bg-white dark:bg-gray-800 shadow-lg flex flex-col">
                    {/* Header */}
                    <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                        <h1 className="text-2xl font-bold text-primary flex items-center">
                            <i className="fas fa-brain mr-2"></i>
                            Ashval
                        </h1>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">ผู้ช่วยจัดการงานอัจฉริยะ</p>
                    </div>
                    
                    {/* Navigation */}
                    <nav className="flex-1 p-4">
                        <ul className="space-y-2">
                            {[
                                { id: 'dashboard', icon: 'fas fa-home', label: 'แดชบอร์ด' },
                                { id: 'tasks', icon: 'fas fa-tasks', label: 'งานทั้งหมด' },
                                { id: 'mood', icon: 'fas fa-smile', label: 'อารมณ์วันนี้' },
                                { id: 'ai', icon: 'fas fa-robot', label: 'AI แนะนำงาน' }
                            ].map(item => (
                                <li key={item.id}>
                                    <button 
                                        onClick={() => setCurrentView(item.id)}
                                        className={`w-full text-left px-4 py-3 rounded-lg transition-colors flex items-center text-base ${
                                            currentView === item.id 
                                                ? 'bg-primary text-white' 
                                                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                                        }`}
                                    >
                                        <i className={`${item.icon} mr-3`}></i>
                                        {item.label}
                                    </button>
                                </li>
                            ))}
                        </ul>
                    </nav>
                    
                    {/* Dark Mode Toggle */}
                    <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                        <button 
                            onClick={toggleDarkMode}
                            className="w-full px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center justify-center text-base"
                        >
                            <i className={`${isDark ? 'fas fa-sun' : 'fas fa-moon'} mr-2`}></i>
                            <span>{isDark ? 'โหมดสว่าง' : 'โหมดมืด'}</span>
                        </button>
                    </div>
                </div>

                {/* Main Content */}
                <div className="flex-1 flex flex-col overflow-hidden">
                    {/* Top Bar */}
                    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <h2 className="text-xl font-semibold">{getViewTitle()}</h2>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    {new Date().toLocaleDateString('th-TH', {
                                        weekday: 'long',
                                        year: 'numeric',
                                        month: 'long',
                                        day: 'numeric'
                                    })}
                                </p>
                            </div>
                            <div className="flex items-center space-x-4">
                                {currentMood && (
                                    <div className="flex items-center bg-primary/10 px-3 py-2 rounded-lg">
                                        <span className="text-lg mr-2">{currentMood.emoji}</span>
                                        <span className="text-sm font-medium">{currentMood.name}</span>
                                    </div>
                                )}
                                <button 
                                    onClick={() => setShowQuickAdd(true)}
                                    className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg transition-colors flex items-center text-base"
                                >
                                    <i className="fas fa-plus mr-2"></i>
                                    เพิ่มงาน
                                </button>
                            </div>
                        </div>
                    </header>

                    {/* Content Area */}
                    <main className="flex-1 overflow-auto p-6">
                        {/* Dashboard View */}
                        {currentView === 'dashboard' && (
                            <div className="fade-in">
                                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                                    {/* Stats Cards */}
                                    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
                                        <div className="flex items-center">
                                            <div className="p-3 bg-primary/10 rounded-lg">
                                                <i className="fas fa-tasks text-primary text-xl"></i>
                                            </div>
                                            <div className="ml-4">
                                                <p className="text-sm text-gray-600 dark:text-gray-400">งานทั้งหมด</p>
                                                <p className="text-2xl font-bold">{getTotalTasks()}</p>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
                                        <div className="flex items-center">
                                            <div className="p-3 bg-success/10 rounded-lg">
                                                <i className="fas fa-check text-success text-xl"></i>
                                            </div>
                                            <div className="ml-4">
                                                <p className="text-sm text-gray-600 dark:text-gray-400">เสร็จแล้ว</p>
                                                <p className="text-2xl font-bold">{getCompletedTasks()}</p>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
                                        <div className="flex items-center">
                                            <div className="p-3 bg-warning/10 rounded-lg">
                                                <i className="fas fa-clock text-warning text-xl"></i>
                                            </div>
                                            <div className="ml-4">
                                                <p className="text-sm text-gray-600 dark:text-gray-400">กำลังทำ</p>
                                                <p className="text-2xl font-bold">{getInProgressTasks()}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Recent Tasks */}
                                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
                                    <h3 className="text-lg font-semibold mb-4">งานล่าสุด</h3>
                                    <div className="space-y-3">
                                        {tasks.slice(0, 5).map(task => (
                                            <div 
                                                key={task.id}
                                                className={`task-card bg-gray-50 dark:bg-gray-700 p-4 rounded-lg cursor-pointer priority-${task.priority}`}
                                            >
                                                <div className="flex items-center justify-between">
                                                    <div className="flex-1">
                                                        <h4 className="font-medium">{task.title}</h4>
                                                        <p className="text-sm text-gray-600 dark:text-gray-400">{task.description}</p>
                                                        <div className="flex items-center mt-2 space-x-2">
                                                            <span className="px-2 py-1 bg-primary/10 text-primary rounded-full text-xs">{task.status}</span>
                                                            <span className="text-xs text-gray-500">
                                                                {new Date(task.createdAt).toLocaleDateString('th-TH', {
                                                                    day: 'numeric',
                                                                    month: 'short'
                                                                })}
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <button 
                                                        onClick={() => toggleTaskComplete(task)}
                                                        className={`ml-4 p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors ${
                                                            task.completed ? 'text-success' : 'text-gray-400'
                                                        }`}
                                                    >
                                                        <i className="fas fa-check"></i>
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Mood View */}
                        {currentView === 'mood' && (
                            <div className="fade-in">
                                <div className="max-w-4xl mx-auto">
                                    <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-sm mb-6">
                                        <h3 className="text-2xl font-semibold mb-6 text-center">อารมณ์ของคุณวันนี้เป็นอย่างไร?</h3>
                                        
                                        {/* Mood Selection */}
                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                                            {moods.map(mood => (
                                                <button 
                                                    key={mood.id}
                                                    onClick={() => selectMood(mood)}
                                                    className={`p-6 rounded-xl transition-all text-center ${
                                                        currentMood?.id === mood.id 
                                                            ? 'mood-button active bg-primary text-white' 
                                                            : 'mood-button bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600'
                                                    }`}
                                                >
                                                    <div className="text-4xl mb-2">{mood.emoji}</div>
                                                    <div className="font-medium text-base">{mood.name}</div>
                                                    <div className="text-sm opacity-75 mt-1">{mood.description}</div>
                                                </button>
                                            ))}
                                        </div>

                                        {/* Current Mood Info */}
                                        {currentMood && (
                                            <div className="bg-primary/10 rounded-xl p-6 text-center">
                                                <div className="text-6xl mb-4">{currentMood.emoji}</div>
                                                <h4 className="text-xl font-semibold mb-2">{currentMood.name}</h4>
                                                <p className="text-gray-600 dark:text-gray-400 mb-4">{currentMood.description}</p>
                                                <button 
                                                    onClick={getAIRecommendations}
                                                    disabled={aiLoading}
                                                    className="bg-primary hover:bg-primary/90 disabled:opacity-50 text-white px-6 py-3 rounded-lg transition-colors text-base"
                                                >
                                                    <i className={`${aiLoading ? 'fas fa-spinner fa-spin' : 'fas fa-robot'} mr-2`}></i>
                                                    <span>{aiLoading ? 'กำลังวิเคราะห์...' : 'ขอคำแนะนำจาก AI'}</span>
                                                </button>
                                            </div>
                                        )}
                                    </div>

                                    {/* AI Recommendations */}
                                    {aiRecommendations && (
                                        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
                                            <h4 className="text-lg font-semibold mb-4 flex items-center">
                                                <i className="fas fa-robot text-primary mr-2"></i>
                                                คำแนะนำจาก AI
                                            </h4>
                                            <div className="prose dark:prose-invert max-w-none">
                                                 {aiRecommendations}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Tasks View */}
                        {currentView === 'tasks' && (
                            <div className="fade-in">
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                    {['todo', 'doing', 'done'].map(status => (
                                        <div key={status} className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
                                            <div className="flex items-center justify-between mb-4">
                                                <h3 className="font-semibold text-lg flex items-center">
                                                    <div className={`w-3 h-3 rounded-full mr-3 ${
                                                        status === 'todo' ? 'bg-gray-400' :
                                                        status === 'doing' ? 'bg-warning' : 'bg-success'
                                                    }`}></div>
                                                    {status === 'todo' ? 'รอทำ' : status === 'doing' ? 'กำลังทำ' : 'เสร็จแล้ว'}
                                                </h3>
                                                <span className={`px-2 py-1 rounded-full text-sm ${
                                                    status === 'todo' ? 'bg-gray-100 dark:bg-gray-700' :
                                                    status === 'doing' ? 'bg-warning/10 text-warning' : 'bg-success/10 text-success'
                                                }`}>
                                                    {tasks.filter(task => task.status === status).length}
                                                </span>
                                            </div>
                                            <div className="space-y-3 max-h-96 overflow-y-auto">
                                                {tasks.filter(task => task.status === status).map(task => (
                                                    <div 
                                                        key={task.id}
                                                        className={`task-card bg-gray-50 dark:bg-gray-700 p-4 rounded-lg cursor-pointer priority-${task.priority} ${
                                                            status === 'done' ? 'opacity-75' : ''
                                                        }`}
                                                    >
                                                        <div className="flex items-start justify-between">
                                                            <div className="flex-1">
                                                                <h4 className={`font-medium text-base ${
                                                                    status === 'done' ? 'line-through' : ''
                                                                }`}>{task.title}</h4>
                                                                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{task.description}</p>
                                                                <div className="flex items-center justify-between mt-3">
                                                                    <span className={`px-2 py-1 rounded-full text-xs ${
                                                                        task.priority === 'high' ? 'bg-error/10 text-error' :
                                                                        task.priority === 'medium' ? 'bg-warning/10 text-warning' : 'bg-success/10 text-success'
                                                                    }`}>
                                                                        {task.priority === 'high' ? 'สูง' : task.priority === 'medium' ? 'กลาง' : 'ต่ำ'}
                                                                    </span>
                                                                    {status !== 'done' ? (
                                                                        <button 
                                                                            onClick={() => toggleTaskComplete(task)}
                                                                            className="text-gray-400 hover:text-success transition-colors"
                                                                        >
                                                                            <i className="fas fa-check"></i>
                                                                        </button>
                                                                    ) : (
                                                                        <span className="text-success">
                                                                            <i className="fas fa-check"></i>
                                                                        </span>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* AI View */}
                        {currentView === 'ai' && (
                            <div className="fade-in">
                                <div className="max-w-4xl mx-auto">
                                    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
                                        <h3 className="text-xl font-semibold mb-4 flex items-center">
                                            <i className="fas fa-robot text-primary mr-3"></i>
                                            AI ผู้ช่วยวางแผนงาน
                                        </h3>
                                        <p className="text-gray-600 dark:text-gray-400">
                                            ฟีเจอร์นี้จะช่วยให้คุณวางแผนงานและได้รับคำแนะนำจาก AI
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </main>
                </div>
            </div>

            {/* Floating Action Button (Mobile) */}
            <button 
                onClick={() => setShowQuickAdd(true)}
                className="floating-add md:hidden bg-primary hover:bg-primary/90 text-white w-14 h-14 rounded-full shadow-lg flex items-center justify-center"
            >
                <i className="fas fa-plus text-xl"></i>
            </button>
        </div>
    );
};

export default AshvalApp;
