#!/usr/bin/env python3
"""
AI-Enhanced File System MCP Desktop Chat App
แอปเดสทอปแบบแชตที่รวม AI จาก Ollama
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import threading
import time
from datetime import datetime
from pathlib import Path
import os
from file_system_analyzer import FileSystemMCPTool
from ollama_client import FileSystemAIAnalyzer

class AIEnhancedChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-Enhanced File System MCP Chat")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Initialize components
        self.tool = FileSystemMCPTool()
        self.ai_analyzer = FileSystemAIAnalyzer()
        self.current_session_id = None
        self.scanning = False
        self.chat_history = []
        self.file_data = {}
        
        # Setup UI
        self.setup_ui()
        self.setup_styles()
        
        # Welcome message
        self.add_system_message("🚀 ยินดีต้อนรับสู่ AI-Enhanced File System MCP Chat!")
        self.add_system_message("💡 ฟีเจอร์ใหม่:\n• 🤖 AI วิเคราะห์ไฟล์ระบบ\n• 📊 การวิเคราะห์อัจฉริยะ\n• 💡 คำแนะนำจาก AI\n• 🎯 การค้นหาขั้นสูง")
        
        # Check AI connection
        if self.ai_analyzer.is_connected():
            self.add_system_message("✅ เชื่อมต่อ AI สำเร็จ! พร้อมใช้งาน")
        else:
            self.add_system_message("⚠️ ไม่สามารถเชื่อมต่อ AI ได้ ใช้งานในโหมดปกติ")
        
    def setup_styles(self):
        """ตั้งค่าสไตล์ของ UI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Main.TFrame', background='#1e1e1e')
        style.configure('Chat.TFrame', background='#2d2d2d')
        style.configure('Input.TFrame', background='#3c3c3c')
        
    def setup_ui(self):
        """สร้าง UI หลัก"""
        # Main container
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Title bar
        self.setup_title_bar(main_frame)
        
        # Content area
        content_frame = ttk.Frame(main_frame, style='Main.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Chat tab
        self.setup_chat_tab()
        
        # AI Analysis tab
        self.setup_ai_analysis_tab()
        
    def setup_title_bar(self, parent):
        """สร้างแถบหัวข้อ"""
        title_frame = ttk.Frame(parent, style='Main.TFrame')
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(title_frame, 
                              text="AI-Enhanced File System MCP Chat", 
                              font=('Segoe UI', 18, 'bold'),
                              fg='#ffffff',
                              bg='#1e1e1e')
        title_label.pack(side=tk.LEFT)
        
        # Status indicators
        status_frame = ttk.Frame(title_frame, style='Main.TFrame')
        status_frame.pack(side=tk.RIGHT)
        
        # AI Status
        ai_status = "🟢 AI พร้อม" if self.ai_analyzer.is_connected() else "🔴 AI ไม่พร้อม"
        self.ai_status_label = tk.Label(status_frame,
                                       text=ai_status,
                                       font=('Segoe UI', 10),
                                       fg='#00ff00' if self.ai_analyzer.is_connected() else '#ff4444',
                                       bg='#1e1e1e')
        self.ai_status_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Session status
        self.session_label = tk.Label(status_frame,
                                     text="Session: ไม่มี",
                                     font=('Segoe UI', 10),
                                     fg='#cccccc',
                                     bg='#1e1e1e')
        self.session_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Connection status
        self.status_label = tk.Label(status_frame,
                                    text="🟢 พร้อมใช้งาน",
                                    font=('Segoe UI', 10),
                                    fg='#00ff00',
                                    bg='#1e1e1e')
        self.status_label.pack(side=tk.LEFT)
        
    def setup_chat_tab(self):
        """สร้างแท็บแชต"""
        chat_frame = ttk.Frame(self.notebook, style='Chat.TFrame')
        self.notebook.add(chat_frame, text="💬 แชต")
        
        # Chat area
        self.setup_chat_area(chat_frame)
        
        # Control panel
        self.setup_control_panel(chat_frame)
        
        # Input area
        self.setup_input_area(chat_frame)
        
    def setup_ai_analysis_tab(self):
        """สร้างแท็บการวิเคราะห์ AI"""
        ai_frame = ttk.Frame(self.notebook, style='Chat.TFrame')
        self.notebook.add(ai_frame, text="🤖 AI วิเคราะห์")
        
        # AI controls
        controls_frame = ttk.Frame(ai_frame, style='Chat.TFrame')
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # AI analysis buttons
        ai_buttons = [
            ("📊 วิเคราะห์โครงสร้าง", self.ai_analyze_structure),
            ("📋 สร้างรายงาน", self.ai_generate_report),
            ("💡 คำแนะนำ", self.ai_get_suggestions),
            ("🔍 วิเคราะห์ขั้นสูง", self.ai_advanced_analysis)
        ]
        
        for text, command in ai_buttons:
            btn = tk.Button(controls_frame,
                           text=text,
                           command=command,
                           bg='#007acc',
                           fg='white',
                           font=('Segoe UI', 10),
                           relief=tk.FLAT,
                           padx=15,
                           pady=5)
            btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # AI display
        self.ai_display = scrolledtext.ScrolledText(
            ai_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#ffffff',
            insertbackground='#ffffff',
            selectbackground='#007acc',
            state=tk.DISABLED
        )
        self.ai_display.pack(fill=tk.BOTH, expand=True)
        
    def setup_chat_area(self, parent):
        """สร้างพื้นที่แชต"""
        chat_frame = ttk.Frame(parent, style='Chat.TFrame')
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#ffffff',
            insertbackground='#ffffff',
            selectbackground='#007acc',
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
    def setup_control_panel(self, parent):
        """สร้างแผงควบคุม"""
        control_frame = ttk.Frame(parent, style='Input.TFrame')
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Scan button
        self.scan_btn = tk.Button(control_frame,
                                 text="📁 สแกนโฟลเดอร์",
                                 command=self.scan_folder,
                                 bg='#007acc',
                                 fg='white',
                                 font=('Segoe UI', 10, 'bold'),
                                 relief=tk.FLAT,
                                 padx=20,
                                 pady=5)
        self.scan_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # AI Analysis button
        ai_btn = tk.Button(control_frame,
                          text="🤖 AI วิเคราะห์",
                          command=self.quick_ai_analysis,
                          bg='#28a745',
                          fg='white',
                          font=('Segoe UI', 10),
                          relief=tk.FLAT,
                          padx=15,
                          pady=5)
        ai_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear chat button
        clear_btn = tk.Button(control_frame,
                             text="🗑️ ล้างแชต",
                             command=self.clear_chat,
                             bg='#dc3545',
                             fg='white',
                             font=('Segoe UI', 10),
                             relief=tk.FLAT,
                             padx=15,
                             pady=5)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export button
        export_btn = tk.Button(control_frame,
                              text="📤 ส่งออก",
                              command=self.export_results,
                              bg='#ffc107',
                              fg='black',
                              font=('Segoe UI', 10),
                              relief=tk.FLAT,
                              padx=15,
                              pady=5)
        export_btn.pack(side=tk.LEFT)
        
    def setup_input_area(self, parent):
        """สร้างพื้นที่ป้อนข้อมูล"""
        input_frame = ttk.Frame(parent, style='Input.TFrame')
        input_frame.pack(fill=tk.X)
        
        # Input field
        self.input_field = tk.Entry(input_frame,
                                   font=('Segoe UI', 11),
                                   bg='#3c3c3c',
                                   fg='#ffffff',
                                   insertbackground='#ffffff',
                                   relief=tk.FLAT)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_field.bind('<Return>', self.send_message)
        
        # Send button
        send_btn = tk.Button(input_frame,
                            text="ส่ง",
                            command=self.send_message,
                            bg='#007acc',
                            fg='white',
                            font=('Segoe UI', 10, 'bold'),
                            relief=tk.FLAT,
                            padx=20)
        send_btn.pack(side=tk.RIGHT)
        
    def add_message(self, sender, message, message_type="normal"):
        """เพิ่มข้อความในแชต"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Format message based on type
        if message_type == "system":
            formatted_message = f"[{timestamp}] 🤖 {message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("system", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("system", foreground="#00ff00")
        elif message_type == "user":
            formatted_message = f"[{timestamp}] 👤 คุณ: {message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("user", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("user", foreground="#007acc")
        elif message_type == "result":
            formatted_message = f"[{timestamp}] 📊 ผลลัพธ์:\n{message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("result", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("result", foreground="#ffaa00")
        elif message_type == "ai":
            formatted_message = f"[{timestamp}] 🤖 AI:\n{message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("ai", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("ai", foreground="#28a745")
        elif message_type == "error":
            formatted_message = f"[{timestamp}] ❌ ข้อผิดพลาด: {message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("error", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("error", foreground="#ff4444")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
        # Save to history
        self.chat_history.append({
            'timestamp': timestamp,
            'sender': sender,
            'message': message,
            'type': message_type
        })
        
    def add_system_message(self, message):
        """เพิ่มข้อความระบบ"""
        self.add_message("system", message, "system")
        
    def scan_folder(self):
        """สแกนโฟลเดอร์"""
        if self.scanning:
            messagebox.showwarning("กำลังสแกน", "กรุณารอให้การสแกนเสร็จสิ้น")
            return
            
        folder_path = filedialog.askdirectory(title="เลือกโฟลเดอร์ที่ต้องการสแกน")
        if not folder_path:
            return
            
        self.scanning = True
        self.status_label.config(text="🟡 กำลังสแกน...", fg='#ffaa00')
        self.scan_btn.config(state=tk.DISABLED)
        
        # Run scan in separate thread
        thread = threading.Thread(target=self._perform_scan, args=(folder_path,))
        thread.daemon = True
        thread.start()
        
    def _perform_scan(self, folder_path):
        """ทำการสแกนในเธรดแยก"""
        try:
            self.add_system_message(f"🔍 เริ่มสแกนโฟลเดอร์: {folder_path}")
            
            scan_params = {
                "action": "scan",
                "path": folder_path,
                "config": {
                    "max_depth": 10,
                    "include_hidden": False,
                    "calculate_hashes": True,
                    "hash_size_limit_mb": 50
                }
            }
            
            result = self.tool._run(json.dumps(scan_params))
            
            if "Session ID:" in result:
                self.current_session_id = result.split("Session ID: ")[1].strip()
                self.add_system_message(f"✅ สแกนเสร็จสิ้น! Session ID: {self.current_session_id}")
                self.session_label.config(text=f"Session: {self.current_session_id[:8]}...")
                
                # Collect file data for AI analysis
                self._collect_file_data()
                
            else:
                self.add_system_message(f"❌ การสแกนล้มเหลว: {result}")
                
        except Exception as e:
            self.add_system_message(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        finally:
            self.scanning = False
            self.status_label.config(text="🟢 พร้อมใช้งาน", fg='#00ff00')
            self.scan_btn.config(state=tk.NORMAL)
            
    def _collect_file_data(self):
        """เก็บข้อมูลไฟล์สำหรับ AI วิเคราะห์"""
        try:
            if not self.current_session_id:
                return
                
            # Get summary data
            summary_result = self.tool._run(json.dumps({
                "action": "query_function",
                "function": "get_directory_summary",
                "session_id": self.current_session_id
            }))
            
            # Get file types
            file_types_result = self.tool._run(json.dumps({
                "action": "query_sql",
                "sql": "SELECT file_extension, COUNT(*) as count FROM files WHERE session_id = ? GROUP BY file_extension ORDER BY count DESC LIMIT 10",
                "params": [self.current_session_id]
            }))
            
            # Get largest files
            largest_files_result = self.tool._run(json.dumps({
                "action": "query_function",
                "function": "get_largest_files",
                "session_id": self.current_session_id,
                "args": [10]
            }))
            
            # Combine data
            self.file_data = {
                "session_id": self.current_session_id,
                "summary": summary_result,
                "file_types": file_types_result,
                "largest_files": largest_files_result
            }
            
            self.add_system_message("📊 ข้อมูลไฟล์พร้อมสำหรับ AI วิเคราะห์")
            
        except Exception as e:
            self.add_system_message(f"⚠️ ไม่สามารถเก็บข้อมูลไฟล์: {str(e)}")
            
    def send_message(self, event=None):
        """ส่งข้อความ"""
        message = self.input_field.get().strip()
        if not message:
            return
            
        self.input_field.delete(0, tk.END)
        self.add_message("user", message, "user")
        
        # Process message in separate thread
        thread = threading.Thread(target=self._process_message, args=(message,))
        thread.daemon = True
        thread.start()
        
    def _process_message(self, message):
        """ประมวลผลข้อความ"""
        try:
            if not self.current_session_id:
                self.add_system_message("⚠️ กรุณาสแกนโฟลเดอร์ก่อนใช้งาน")
                return
                
            # Check for special commands
            if message.lower().startswith("/help"):
                self._show_help()
                return
            elif message.lower().startswith("/scan"):
                self.add_system_message("ใช้ปุ่ม 'สแกนโฟลเดอร์' เพื่อสแกนโฟลเดอร์ใหม่")
                return
            elif message.lower().startswith("/ai"):
                self._process_ai_query(message[3:].strip())
                return
            elif message.lower().startswith("/clear"):
                self.clear_chat()
                return
                
            # Check if it's an AI query
            if self.ai_analyzer.is_connected() and any(keyword in message.lower() for keyword in 
                ['วิเคราะห์', 'อธิบาย', 'แนะนำ', 'รายงาน', 'โครงสร้าง', 'ปัญหา', 'ปรับปรุง']):
                self._process_ai_query(message)
                return
                
            # Process natural language query
            query_params = {
                "action": "query_natural",
                "request": message,
                "session_id": self.current_session_id
            }
            
            result = self.tool._run(json.dumps(query_params))
            
            # Parse and format result
            try:
                result_data = json.loads(result)
                if result_data.get('success'):
                    formatted_result = self._format_result(result_data.get('data', result_data))
                    self.add_message("result", formatted_result, "result")
                else:
                    self.add_message("error", result_data.get('error', 'ไม่สามารถประมวลผลได้'), "error")
            except json.JSONDecodeError:
                self.add_message("result", result, "result")
                
        except Exception as e:
            self.add_message("error", f"เกิดข้อผิดพลาด: {str(e)}", "error")
            
    def _process_ai_query(self, query):
        """ประมวลผลคำถาม AI"""
        if not self.ai_analyzer.is_connected():
            self.add_message("error", "ไม่สามารถเชื่อมต่อ AI ได้", "error")
            return
            
        if not self.file_data:
            self.add_message("error", "ไม่มีข้อมูลไฟล์สำหรับ AI วิเคราะห์", "error")
            return
            
        self.add_system_message("🤖 กำลังประมวลผลด้วย AI...")
        
        # Run AI analysis in separate thread
        thread = threading.Thread(target=self._run_ai_analysis, args=(query,))
        thread.daemon = True
        thread.start()
        
    def _run_ai_analysis(self, query):
        """รันการวิเคราะห์ AI"""
        try:
            result = self.ai_analyzer.analyze_with_ai(self.file_data, query)
            if result:
                self.add_message("ai", result, "ai")
            else:
                self.add_message("error", "ไม่สามารถวิเคราะห์ด้วย AI ได้", "error")
        except Exception as e:
            self.add_message("error", f"เกิดข้อผิดพลาดในการวิเคราะห์ AI: {str(e)}", "error")
            
    def _format_result(self, data):
        """จัดรูปแบบผลลัพธ์"""
        if isinstance(data, list):
            if not data:
                return "ไม่พบข้อมูล"
            
            # Check if it's a list of dictionaries (table data)
            if isinstance(data[0], dict):
                return self._format_table(data)
            else:
                return "\n".join(str(item) for item in data)
        elif isinstance(data, dict):
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return str(data)
            
    def _format_table(self, data):
        """จัดรูปแบบตาราง"""
        if not data:
            return "ไม่พบข้อมูล"
            
        # Get headers
        headers = list(data[0].keys())
        
        # Calculate column widths
        col_widths = {}
        for header in headers:
            col_widths[header] = len(str(header))
            
        for row in data:
            for header in headers:
                col_widths[header] = max(col_widths[header], len(str(row.get(header, ''))))
                
        # Create table
        table = []
        
        # Header
        header_row = " | ".join(f"{header:<{col_widths[header]}}" for header in headers)
        table.append(header_row)
        table.append("-" * len(header_row))
        
        # Data rows
        for row in data:
            row_str = " | ".join(f"{str(row.get(header, '')):<{col_widths[header]}}" for header in headers)
            table.append(row_str)
            
        return "\n".join(table)
        
    def _show_help(self):
        """แสดงความช่วยเหลือ"""
        help_text = """
📋 คำสั่งที่ใช้งานได้:

🔍 Natural Language Queries:
• "show me large files" - แสดงไฟล์ขนาดใหญ่
• "find duplicate files" - ค้นหาไฟล์ซ้ำ
• "give me summary" - สรุปข้อมูล
• "show files with extension .py" - แสดงไฟล์ตามนามสกุล

🤖 AI Commands:
• /ai วิเคราะห์โครงสร้าง - วิเคราะห์โครงสร้างไฟล์ด้วย AI
• /ai สร้างรายงาน - สร้างรายงานการวิเคราะห์
• /ai คำแนะนำ - ได้คำแนะนำจาก AI
• ใช้คำว่า "วิเคราะห์", "อธิบาย", "แนะนำ" เพื่อเรียก AI

🔧 Special Commands:
• /help - แสดงความช่วยเหลือ
• /scan - ข้อมูลการสแกน
• /clear - ล้างแชต

💡 Tips:
• ใช้ภาษาธรรมชาติในการค้นหา
• AI จะช่วยวิเคราะห์และให้คำแนะนำ
• ระบบจะประมวลผลแบบ real-time
        """
        self.add_system_message(help_text)
        
    def clear_chat(self):
        """ล้างแชต"""
        if messagebox.askyesno("ยืนยัน", "คุณต้องการล้างการสนทนาทั้งหมดหรือไม่?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.chat_history.clear()
            self.add_system_message("🗑️ การสนทนาถูกล้างแล้ว")
            
    def export_results(self):
        """ส่งออกผลลัพธ์"""
        if not self.current_session_id:
            messagebox.showwarning("ไม่มีข้อมูล", "กรุณาสแกนโฟลเดอร์ก่อนส่งออกผลลัพธ์")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="ส่งออกผลลัพธ์"
        )
        if filename:
            try:
                # Get chat content
                chat_content = self.chat_display.get(1.0, tk.END)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("AI-Enhanced File System MCP Chat Export\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Session ID: {self.current_session_id}\n")
                    f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(chat_content)
                    
                messagebox.showinfo("สำเร็จ", f"ส่งออกผลลัพธ์ไปยัง {filename}")
            except Exception as e:
                messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถส่งออกได้: {str(e)}")
                
    def quick_ai_analysis(self):
        """การวิเคราะห์ AI ด่วน"""
        if not self.ai_analyzer.is_connected():
            messagebox.showwarning("AI ไม่พร้อม", "ไม่สามารถเชื่อมต่อ AI ได้")
            return
            
        if not self.file_data:
            messagebox.showwarning("ไม่มีข้อมูล", "กรุณาสแกนโฟลเดอร์ก่อนใช้งาน AI")
            return
            
        # Run quick analysis
        thread = threading.Thread(target=self._quick_ai_analysis)
        thread.daemon = True
        thread.start()
        
    def _quick_ai_analysis(self):
        """การวิเคราะห์ AI ด่วน"""
        try:
            self.add_system_message("🤖 กำลังวิเคราะห์ด้วย AI...")
            
            # Get AI suggestions
            suggestions = self.ai_analyzer.get_suggestions(self.file_data)
            if suggestions:
                self.add_message("ai", f"💡 คำแนะนำจาก AI:\n{suggestions}", "ai")
            
            # Get structure explanation
            structure = self.ai_analyzer.explain_structure(self.file_data)
            if structure:
                self.add_message("ai", f"📁 การวิเคราะห์โครงสร้าง:\n{structure}", "ai")
                
        except Exception as e:
            self.add_message("error", f"เกิดข้อผิดพลาดในการวิเคราะห์ AI: {str(e)}", "error")
            
    # AI Analysis tab methods
    def ai_analyze_structure(self):
        """วิเคราะห์โครงสร้างด้วย AI"""
        if not self._check_ai_ready():
            return
            
        thread = threading.Thread(target=self._ai_analyze_structure)
        thread.daemon = True
        thread.start()
        
    def _ai_analyze_structure(self):
        """วิเคราะห์โครงสร้างด้วย AI"""
        try:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, "🤖 กำลังวิเคราะห์โครงสร้าง...\n")
            self.ai_display.config(state=tk.DISABLED)
            
            result = self.ai_analyzer.explain_structure(self.file_data)
            if result:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, f"📁 การวิเคราะห์โครงสร้าง:\n\n{result}")
                self.ai_display.config(state=tk.DISABLED)
            else:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, "❌ ไม่สามารถวิเคราะห์ได้")
                self.ai_display.config(state=tk.DISABLED)
                
        except Exception as e:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, f"❌ เกิดข้อผิดพลาด: {str(e)}")
            self.ai_display.config(state=tk.DISABLED)
            
    def ai_generate_report(self):
        """สร้างรายงานด้วย AI"""
        if not self._check_ai_ready():
            return
            
        thread = threading.Thread(target=self._ai_generate_report)
        thread.daemon = True
        thread.start()
        
    def _ai_generate_report(self):
        """สร้างรายงานด้วย AI"""
        try:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, "🤖 กำลังสร้างรายงาน...\n")
            self.ai_display.config(state=tk.DISABLED)
            
            result = self.ai_analyzer.generate_report(self.file_data)
            if result:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, f"📋 รายงานการวิเคราะห์:\n\n{result}")
                self.ai_display.config(state=tk.DISABLED)
            else:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, "❌ ไม่สามารถสร้างรายงานได้")
                self.ai_display.config(state=tk.DISABLED)
                
        except Exception as e:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, f"❌ เกิดข้อผิดพลาด: {str(e)}")
            self.ai_display.config(state=tk.DISABLED)
            
    def ai_get_suggestions(self):
        """ได้คำแนะนำจาก AI"""
        if not self._check_ai_ready():
            return
            
        thread = threading.Thread(target=self._ai_get_suggestions)
        thread.daemon = True
        thread.start()
        
    def _ai_get_suggestions(self):
        """ได้คำแนะนำจาก AI"""
        try:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, "🤖 กำลังสร้างคำแนะนำ...\n")
            self.ai_display.config(state=tk.DISABLED)
            
            result = self.ai_analyzer.get_suggestions(self.file_data)
            if result:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, f"💡 คำแนะนำจาก AI:\n\n{result}")
                self.ai_display.config(state=tk.DISABLED)
            else:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, "❌ ไม่สามารถสร้างคำแนะนำได้")
                self.ai_display.config(state=tk.DISABLED)
                
        except Exception as e:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, f"❌ เกิดข้อผิดพลาด: {str(e)}")
            self.ai_display.config(state=tk.DISABLED)
            
    def ai_advanced_analysis(self):
        """การวิเคราะห์ขั้นสูงด้วย AI"""
        if not self._check_ai_ready():
            return
            
        # Create custom query dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("การวิเคราะห์ขั้นสูง")
        dialog.geometry("500x300")
        dialog.configure(bg='#2d2d2d')
        
        tk.Label(dialog, text="การวิเคราะห์ขั้นสูง", 
                font=('Segoe UI', 14, 'bold'), fg='#ffffff', bg='#2d2d2d').pack(pady=10)
        
        tk.Label(dialog, text="คำถามหรือคำสั่ง:", 
                font=('Segoe UI', 10), fg='#ffffff', bg='#2d2d2d').pack(anchor=tk.W, padx=20, pady=5)
        
        query_entry = tk.Entry(dialog, font=('Segoe UI', 10), bg='#3c3c3c', fg='#ffffff')
        query_entry.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        def run_analysis():
            query = query_entry.get().strip()
            if not query:
                return
                
            dialog.destroy()
            
            thread = threading.Thread(target=self._run_advanced_analysis, args=(query,))
            thread.daemon = True
            thread.start()
        
        tk.Button(dialog, text="วิเคราะห์", command=run_analysis,
                 bg='#007acc', fg='white', font=('Segoe UI', 10, 'bold'),
                 relief=tk.FLAT, padx=20, pady=5).pack()
        
    def _run_advanced_analysis(self, query):
        """รันการวิเคราะห์ขั้นสูง"""
        try:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, f"🤖 กำลังวิเคราะห์: {query}\n")
            self.ai_display.config(state=tk.DISABLED)
            
            result = self.ai_analyzer.analyze_with_ai(self.file_data, query)
            if result:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, f"🔍 ผลการวิเคราะห์:\n\n{result}")
                self.ai_display.config(state=tk.DISABLED)
            else:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, "❌ ไม่สามารถวิเคราะห์ได้")
                self.ai_display.config(state=tk.DISABLED)
                
        except Exception as e:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, f"❌ เกิดข้อผิดพลาด: {str(e)}")
            self.ai_display.config(state=tk.DISABLED)
            
    def _check_ai_ready(self):
        """ตรวจสอบว่า AI พร้อมใช้งาน"""
        if not self.ai_analyzer.is_connected():
            messagebox.showwarning("AI ไม่พร้อม", "ไม่สามารถเชื่อมต่อ AI ได้")
            return False
            
        if not self.file_data:
            messagebox.showwarning("ไม่มีข้อมูล", "กรุณาสแกนโฟลเดอร์ก่อนใช้งาน AI")
            return False
            
        return True

def main():
    """ฟังก์ชันหลัก"""
    root = tk.Tk()
    app = AIEnhancedChatApp(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
