import React, { useState, useEffect, useRef } from 'react';
import mermaid from 'mermaid';
import { ChonostIcon, AnimatedIcon, FloatingIcon } from './IconSystem';

// ตั้งค่า Mermaid
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  securityLevel: 'loose',
  fontFamily: 'Noto Sans Thai, sans-serif',
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'basis'
  },
  sequence: {
    useMaxWidth: true,
    diagramMarginX: 50,
    diagramMarginY: 10,
    actorMargin: 50,
    width: 150,
    height: 65,
    boxMargin: 10,
    boxTextMargin: 5,
    noteMargin: 10,
    messageMargin: 35,
    mirrorActors: true,
    bottomMarginAdj: 1,
    useMaxWidth: true,
    rightAngles: false,
    showSequenceNumbers: false
  },
  gantt: {
    titleTopMargin: 25,
    barHeight: 20,
    barGap: 4,
    topPadding: 50,
    leftPadding: 75,
    gridLineStartPadding: 35,
    fontSize: 11,
    fontFamily: 'Noto Sans Thai, sans-serif',
    numberSectionStyles: 4,
    axisFormat: '%Y-%m-%d'
  }
});

// AI Diagram Generator
export const AIDiagramGenerator = ({ onGenerate, className = '' }) => {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [diagramType, setDiagramType] = useState('flowchart');

  const diagramTypes = [
    { id: 'flowchart', name: 'Flowchart', icon: 'chart', description: 'แผนผังการทำงาน' },
    { id: 'sequence', name: 'Sequence', icon: 'timeline', description: 'ลำดับการทำงาน' },
    { id: 'class', name: 'Class', icon: 'structure', description: 'โครงสร้างคลาส' },
    { id: 'state', name: 'State', icon: 'state', description: 'สถานะต่างๆ' },
    { id: 'entity', name: 'Entity', icon: 'database', description: 'ความสัมพันธ์ข้อมูล' },
    { id: 'userjourney', name: 'User Journey', icon: 'journey', description: 'การเดินทางของผู้ใช้' },
    { id: 'gantt', name: 'Gantt', icon: 'calendar', description: 'ตารางเวลา' },
    { id: 'pie', name: 'Pie Chart', icon: 'chart', description: 'กราฟวงกลม' }
  ];

  const generateDiagram = async () => {
    if (!prompt.trim()) return;
    
    setIsGenerating(true);
    
    try {
      // จำลองการเรียก AI API
      const response = await simulateAIGeneration(prompt, diagramType);
      onGenerate(response);
    } catch (error) {
      console.error('Error generating diagram:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const simulateAIGeneration = async (prompt, type) => {
    // จำลองการทำงานของ AI
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const templates = {
      flowchart: `graph TD
    A[เริ่มต้น] --> B{ตรวจสอบเงื่อนไข}
    B -->|ใช่| C[ดำเนินการ A]
    B -->|ไม่ใช่| D[ดำเนินการ B]
    C --> E[เสร็จสิ้น]
    D --> E`,
      sequence: `sequenceDiagram
    participant U as ผู้ใช้
    participant S as ระบบ
    participant D as ฐานข้อมูล
    
    U->>S: ส่งคำขอ
    S->>D: ค้นหาข้อมูล
    D-->>S: ส่งข้อมูลกลับ
    S-->>U: แสดงผลลัพธ์`,
      class: `classDiagram
    class Character {
        +String name
        +String description
        +List~String~ traits
        +addTrait(trait)
        +removeTrait(trait)
    }
    
    class Story {
        +String title
        +String plot
        +List~Character~ characters
        +addCharacter(character)
    }
    
    Character ||--o{ Story : appears in`,
      state: `stateDiagram-v2
    [*] --> Draft
    Draft --> Review
    Review --> Published
    Review --> Draft
    Published --> [*]`,
      entity: `erDiagram
    USER {
        string id
        string name
        string email
    }
    PROJECT {
        string id
        string title
        string description
    }
    DOCUMENT {
        string id
        string title
        string content
    }
    USER ||--o{ PROJECT : creates
    PROJECT ||--o{ DOCUMENT : contains`,
      userjourney: `journey
    title การเขียนนิยาย
    section การเริ่มต้น
      ไอเดีย: 5: ผู้เขียน
      วางแผน: 4: ผู้เขียน
    section การเขียน
      เขียนบทแรก: 3: ผู้เขียน
      แก้ไข: 4: ผู้เขียน
    section การเสร็จสิ้น
      ตรวจสอบ: 5: ผู้เขียน
      เผยแพร่: 4: ผู้เขียน`,
      gantt: `gantt
    title แผนการเขียนนิยาย
    dateFormat  YYYY-MM-DD
    section การวางแผน
    วิเคราะห์พล็อต    :done, plan1, 2024-01-01, 7d
    สร้างตัวละคร     :done, plan2, 2024-01-08, 5d
    section การเขียน
    เขียนบทแรก       :active, write1, 2024-01-13, 10d
    เขียนบทต่อ       :write2, 2024-01-23, 15d
    section การแก้ไข
    แก้ไขครั้งแรก     :edit1, 2024-02-07, 7d
    แก้ไขครั้งสุดท้าย  :edit2, 2024-02-14, 5d`,
      pie: `pie title การใช้เวลาในการเขียน
    "การวางแผน" : 20
    "การเขียน" : 50
    "การแก้ไข" : 25
    "การตรวจสอบ" : 5`
    };

    return {
      type: type,
      code: templates[type] || templates.flowchart,
      prompt: prompt,
      generatedAt: new Date().toISOString()
    };
  };

  return (
    <div className={`ai-diagram-generator ${className}`}>
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <AnimatedIcon name="ai" size="1.2rem" className="mr-2" animation={isGenerating ? "spin" : "pulse"} />
          AI Diagram Generator
        </h3>
        
        <div className="space-y-4">
          {/* Diagram Type Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">ประเภทไดอะแกรม</label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {diagramTypes.map(type => (
                <button
                  key={type.id}
                  onClick={() => setDiagramType(type.id)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    diagramType === type.id
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'
                  }`}
                >
                  <ChonostIcon name={type.icon} size="1.5rem" className="mb-1" />
                  <div className="text-xs font-medium">{type.name}</div>
                  <div className="text-xs text-gray-500">{type.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Prompt Input */}
          <div>
            <label className="block text-sm font-medium mb-2">คำอธิบายไดอะแกรม</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="อธิบายไดอะแกรมที่คุณต้องการ เช่น: แสดงขั้นตอนการเขียนนิยาย ตั้งแต่การวางแผนจนถึงการเผยแพร่"
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg resize-none h-24 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Generate Button */}
          <button
            onClick={generateDiagram}
            disabled={!prompt.trim() || isGenerating}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white py-3 px-6 rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isGenerating ? (
              <>
                <AnimatedIcon name="ai" size="1.2rem" className="mr-2" animation="spin" />
                กำลังสร้างไดอะแกรม...
              </>
            ) : (
              <>
                <ChonostIcon name="magic" size="1.2rem" className="mr-2" />
                สร้างไดอะแกรมด้วย AI
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

// Mermaid Diagram Renderer
export const MermaidDiagram = ({ code, title, className = '', onEdit, onDelete }) => {
  const [error, setError] = useState(null);
  const [isRendering, setIsRendering] = useState(true);
  const diagramRef = useRef(null);

  useEffect(() => {
    renderDiagram();
  }, [code]);

  const renderDiagram = async () => {
    if (!code) return;
    
    setIsRendering(true);
    setError(null);
    
    try {
      // Clear previous content
      if (diagramRef.current) {
        diagramRef.current.innerHTML = '';
      }
      
      // Generate unique ID
      const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      
      // Create container
      const container = document.createElement('div');
      container.id = id;
      container.className = 'mermaid';
      container.textContent = code;
      
      if (diagramRef.current) {
        diagramRef.current.appendChild(container);
      }
      
      // Render with Mermaid
      await mermaid.run();
      setIsRendering(false);
    } catch (err) {
      setError(err.message);
      setIsRendering(false);
    }
  };

  return (
    <div className={`mermaid-diagram ${className}`}>
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-lg font-semibold flex items-center">
            <ChonostIcon name="chart" size="1.2rem" className="mr-2" />
            {title || 'ไดอะแกรม'}
          </h4>
          <div className="flex items-center space-x-2">
            {onEdit && (
              <button
                onClick={onEdit}
                className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
              >
                <ChonostIcon name="edit" size="1rem" />
              </button>
            )}
            {onDelete && (
              <button
                onClick={onDelete}
                className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
              >
                <ChonostIcon name="delete" size="1rem" />
              </button>
            )}
          </div>
        </div>

        {/* Diagram Content */}
        <div className="relative">
          {isRendering && (
            <div className="flex items-center justify-center py-12">
              <AnimatedIcon name="ai" size="2rem" animation="spin" />
              <span className="ml-2 text-gray-600">กำลังสร้างไดอะแกรม...</span>
            </div>
          )}
          
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <div className="flex items-center">
                <ChonostIcon name="error" size="1.2rem" className="mr-2 text-red-600" />
                <span className="text-red-800 dark:text-red-200 font-medium">เกิดข้อผิดพลาด</span>
              </div>
              <p className="text-red-700 dark:text-red-300 text-sm mt-1">{error}</p>
            </div>
          )}
          
          <div 
            ref={diagramRef}
            className={`mermaid-container ${isRendering ? 'hidden' : ''}`}
          />
        </div>

        {/* Code Preview */}
        <details className="mt-4">
          <summary className="cursor-pointer text-sm font-medium text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200">
            แสดงโค้ด Mermaid
          </summary>
          <pre className="mt-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg text-xs overflow-x-auto">
            <code>{code}</code>
          </pre>
        </details>
      </div>
    </div>
  );
};

// Mermaid Editor
export const MermaidEditor = ({ initialCode = '', onSave, onCancel, className = '' }) => {
  const [code, setCode] = useState(initialCode);
  const [preview, setPreview] = useState(null);
  const [isPreviewing, setIsPreviewing] = useState(false);

  const generatePreview = async () => {
    if (!code.trim()) return;
    
    setIsPreviewing(true);
    try {
      // Create temporary container for preview
      const tempContainer = document.createElement('div');
      tempContainer.className = 'mermaid';
      tempContainer.textContent = code;
      
      // Render preview
      await mermaid.run();
      setPreview(tempContainer.innerHTML);
    } catch (error) {
      console.error('Preview error:', error);
    } finally {
      setIsPreviewing(false);
    }
  };

  useEffect(() => {
    if (code) {
      const timeout = setTimeout(generatePreview, 1000);
      return () => clearTimeout(timeout);
    }
  }, [code]);

  return (
    <div className={`mermaid-editor ${className}`}>
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <ChonostIcon name="edit" size="1.2rem" className="mr-2" />
          แก้ไขไดอะแกรม
        </h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Code Editor */}
          <div>
            <label className="block text-sm font-medium mb-2">โค้ด Mermaid</label>
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="ใส่โค้ด Mermaid ตรงนี้..."
              className="w-full h-64 p-3 border border-gray-300 dark:border-gray-600 rounded-lg resize-none font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Preview */}
          <div>
            <label className="block text-sm font-medium mb-2">ตัวอย่าง</label>
            <div className="h-64 border border-gray-300 dark:border-gray-600 rounded-lg p-3 overflow-auto">
              {isPreviewing ? (
                <div className="flex items-center justify-center h-full">
                  <AnimatedIcon name="ai" size="1.5rem" animation="spin" />
                  <span className="ml-2 text-gray-600">กำลังสร้างตัวอย่าง...</span>
                </div>
              ) : preview ? (
                <div dangerouslySetInnerHTML={{ __html: preview }} />
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  ตัวอย่างจะแสดงที่นี่
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end space-x-3 mt-6">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            ยกเลิก
          </button>
          <button
            onClick={() => onSave(code)}
            disabled={!code.trim()}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            บันทึก
          </button>
        </div>
      </div>
    </div>
  );
};

// Diagram Gallery
export const DiagramGallery = ({ diagrams = [], onSelect, onDelete, className = '' }) => {
  return (
    <div className={`diagram-gallery ${className}`}>
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <ChonostIcon name="gallery" size="1.2rem" className="mr-2" />
          แกลเลอรี่ไดอะแกรม
        </h3>
        
        {diagrams.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <ChonostIcon name="empty" size="3rem" className="mx-auto mb-4 opacity-50" />
            <p>ยังไม่มีไดอะแกรม</p>
            <p className="text-sm">สร้างไดอะแกรมแรกของคุณด้วย AI</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {diagrams.map((diagram, index) => (
              <div
                key={index}
                className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:border-blue-300 dark:hover:border-blue-600 transition-colors cursor-pointer"
                onClick={() => onSelect(diagram)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-sm">{diagram.title || `ไดอะแกรม ${index + 1}`}</h4>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(index);
                    }}
                    className="text-gray-400 hover:text-red-600 transition-colors"
                  >
                    <ChonostIcon name="delete" size="1rem" />
                  </button>
                </div>
                <div className="text-xs text-gray-500 mb-2">
                  {diagram.type} • {new Date(diagram.generatedAt).toLocaleDateString('th-TH')}
                </div>
                <div className="h-24 bg-gray-50 dark:bg-gray-700 rounded flex items-center justify-center">
                  <ChonostIcon name="chart" size="2rem" className="opacity-50" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Main Mermaid System Component
export const MermaidSystem = ({ className = '' }) => {
  const [diagrams, setDiagrams] = useState([]);
  const [selectedDiagram, setSelectedDiagram] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showGenerator, setShowGenerator] = useState(false);

  const handleGenerate = (newDiagram) => {
    setDiagrams(prev => [...prev, { ...newDiagram, id: Date.now() }]);
    setSelectedDiagram(newDiagram);
    setShowGenerator(false);
  };

  const handleEdit = (diagram) => {
    setSelectedDiagram(diagram);
    setIsEditing(true);
  };

  const handleSave = (updatedCode) => {
    if (selectedDiagram) {
      const updatedDiagram = { ...selectedDiagram, code: updatedCode };
      setDiagrams(prev => prev.map(d => d.id === selectedDiagram.id ? updatedDiagram : d));
      setSelectedDiagram(updatedDiagram);
    }
    setIsEditing(false);
  };

  const handleDelete = (index) => {
    setDiagrams(prev => prev.filter((_, i) => i !== index));
    if (selectedDiagram && diagrams[index].id === selectedDiagram.id) {
      setSelectedDiagram(null);
    }
  };

  return (
    <div className={`mermaid-system ${className}`}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold flex items-center">
            <ChonostIcon name="chart" size="2rem" className="mr-3" />
            ระบบไดอะแกรม Mermaid
          </h2>
          <button
            onClick={() => setShowGenerator(!showGenerator)}
            className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-all flex items-center"
          >
            <ChonostIcon name="plus" size="1.2rem" className="mr-2" />
            สร้างไดอะแกรมใหม่
          </button>
        </div>

        {/* AI Generator */}
        {showGenerator && (
          <AIDiagramGenerator onGenerate={handleGenerate} />
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Gallery */}
          <div className="lg:col-span-1">
            <DiagramGallery
              diagrams={diagrams}
              onSelect={setSelectedDiagram}
              onDelete={handleDelete}
            />
          </div>

          {/* Editor/Viewer */}
          <div className="lg:col-span-2">
            {isEditing ? (
              <MermaidEditor
                initialCode={selectedDiagram?.code || ''}
                onSave={handleSave}
                onCancel={() => setIsEditing(false)}
              />
            ) : selectedDiagram ? (
              <MermaidDiagram
                code={selectedDiagram.code}
                title={selectedDiagram.title}
                onEdit={() => handleEdit(selectedDiagram)}
                onDelete={() => handleDelete(diagrams.findIndex(d => d.id === selectedDiagram.id))}
              />
            ) : (
              <div className="bg-white dark:bg-gray-800 rounded-xl p-12 shadow-sm text-center">
                <ChonostIcon name="chart" size="4rem" className="mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-medium mb-2">เลือกไดอะแกรม</h3>
                <p className="text-gray-500">เลือกไดอะแกรมจากแกลเลอรี่เพื่อดูหรือแก้ไข</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MermaidSystem;
