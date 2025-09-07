#!/usr/bin/env python3
"""
Unified File System MCP Chat App
แอปแชตแบบรวมศูนย์ที่เชื่อมต่อทุกอย่างอัตโนมัติ
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import threading
import time
import subprocess
import requests
import os
import sys
from datetime import datetime
from pathlib import Path
from core.file_system_analyzer import FileSystemMCPTool

class UnifiedChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 File System MCP - Unified Chat")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Force window to front and make it copyable
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        
        # Initialize components
        self.tool = FileSystemMCPTool()
        self.current_session_id = None
        self.scanning = False
        self.ollama_connected = False
        self.ollama_client = None
        
        # Setup UI
        self.setup_ui()
        self.setup_styles()
        
        # Auto-start services
        self.auto_start_services()
        
    def setup_styles(self):
        """ตั้งค่าสไตล์ของ UI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for dark theme
        style.configure('Dark.TFrame', background='#1e1e1e')
        style.configure('Dark.TLabel', background='#1e1e1e', foreground='#ffffff')
        style.configure('Dark.TButton', 
                       background='#007acc', 
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'))
        
    def setup_ui(self):
        """สร้าง UI หลัก"""
        # Main container
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header with status
        self.setup_header(main_frame)
        
        # Split view: Chat and Control Panel
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left side: Chat area
        self.setup_chat_area(paned_window)
        
        # Right side: Control panel
        self.setup_control_panel(paned_window)
        
        # Input area at bottom
        self.setup_input_area(main_frame)
        
    def setup_header(self, parent):
        """สร้างส่วนหัวพร้อมสถานะ"""
        header_frame = ttk.Frame(parent, style='Dark.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(header_frame, 
                              text="🚀 File System MCP - Unified Chat", 
                              font=('Segoe UI', 18, 'bold'),
                              fg='#ffffff',
                              bg='#1e1e1e')
        title_label.pack(side=tk.LEFT)
        
        # Status indicators
        status_frame = tk.Frame(header_frame, bg='#1e1e1e')
        status_frame.pack(side=tk.RIGHT)
        
        # File System Status
        self.fs_status = tk.Label(status_frame,
                                 text="📁 File System: กำลังเชื่อมต่อ...",
                                 font=('Segoe UI', 9),
                                 fg='#ffaa00',
                                 bg='#1e1e1e')
        self.fs_status.pack(side=tk.LEFT, padx=(0, 10))
        
        # Ollama Status
        self.ollama_status = tk.Label(status_frame,
                                     text="🤖 Ollama: กำลังเชื่อมต่อ...",
                                     font=('Segoe UI', 9),
                                     fg='#ffaa00',
                                     bg='#1e1e1e')
        self.ollama_status.pack(side=tk.LEFT, padx=(0, 10))
        
        # Session Status
        self.session_status = tk.Label(status_frame,
                                      text="💾 Session: ไม่มี",
                                      font=('Segoe UI', 9),
                                      fg='#cccccc',
                                      bg='#1e1e1e')
        self.session_status.pack(side=tk.LEFT)
        
    def setup_chat_area(self, parent):
        """สร้างพื้นที่แชต"""
        chat_frame = ttk.Frame(parent, style='Dark.TFrame')
        parent.add(chat_frame, weight=3)
        
        # Chat display with copy functionality
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=('Consolas', 11),
            bg='#2d2d2d',
            fg='#ffffff',
            insertbackground='#ffffff',
            selectbackground='#007acc',
            state=tk.NORMAL,  # Allow copying
            cursor='ibeam'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Add right-click menu for copy/paste
        self.setup_context_menu()
        
    def setup_context_menu(self):
        """สร้างเมนูคลิกขวาสำหรับ copy/paste"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="📋 Copy", command=self.copy_selected)
        self.context_menu.add_command(label="📋 Copy All", command=self.copy_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Clear Chat", command=self.clear_chat)
        
        self.chat_display.bind("<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        """แสดงเมนูคลิกขวา"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
            
    def copy_selected(self):
        """คัดลอกข้อความที่เลือก"""
        try:
            selected_text = self.chat_display.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.add_system_message("✅ คัดลอกข้อความแล้ว")
        except tk.TclError:
            self.add_system_message("⚠️ ไม่มีข้อความที่เลือก")
            
    def copy_all(self):
        """คัดลอกข้อความทั้งหมด"""
        all_text = self.chat_display.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(all_text)
        self.add_system_message("✅ คัดลอกข้อความทั้งหมดแล้ว")
        
    def clear_chat(self):
        """ล้างแชต"""
        self.chat_display.delete(1.0, tk.END)
        self.add_system_message("🗑️ ล้างแชตแล้ว")
        
    def setup_control_panel(self, parent):
        """สร้างแผงควบคุม"""
        control_frame = ttk.Frame(parent, style='Dark.TFrame')
        parent.add(control_frame, weight=1)
        
        # Control panel title
        title_label = tk.Label(control_frame,
                              text="🎛️ Control Panel",
                              font=('Segoe UI', 14, 'bold'),
                              fg='#ffffff',
                              bg='#1e1e1e')
        title_label.pack(pady=(0, 15))
        
        # Quick actions
        self.setup_quick_actions(control_frame)
        
        # File operations
        self.setup_file_operations(control_frame)
        
        # AI operations
        self.setup_ai_operations(control_frame)
        
        # System info
        self.setup_system_info(control_frame)
        
    def setup_quick_actions(self, parent):
        """สร้างปุ่มการทำงานด่วน"""
        quick_frame = tk.LabelFrame(parent, text="⚡ Quick Actions", 
                                   font=('Segoe UI', 10, 'bold'),
                                   fg='#ffffff', bg='#1e1e1e')
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Scan button
        self.scan_btn = tk.Button(quick_frame,
                                 text="📁 Scan Folder",
                                 command=self.scan_folder,
                                 bg='#007acc',
                                 fg='white',
                                 font=('Segoe UI', 10, 'bold'),
                                 relief=tk.FLAT,
                                 padx=15,
                                 pady=8)
        self.scan_btn.pack(fill=tk.X, padx=10, pady=5)
        
        # Quick queries
        queries = [
            ("📊 Summary", "give me summary"),
            ("🔍 Large Files", "show me large files"),
            ("🔄 Duplicates", "find duplicate files"),
            ("📁 File Types", "show file types")
        ]
        
        for text, query in queries:
            btn = tk.Button(quick_frame,
                           text=text,
                           command=lambda q=query: self.quick_query(q),
                           bg='#2d2d2d',
                           fg='#ffffff',
                           font=('Segoe UI', 9),
                           relief=tk.FLAT,
                           padx=10,
                           pady=5)
            btn.pack(fill=tk.X, padx=10, pady=2)
            
    def setup_file_operations(self, parent):
        """สร้างส่วนการจัดการไฟล์"""
        file_frame = tk.LabelFrame(parent, text="📁 File Operations", 
                                  font=('Segoe UI', 10, 'bold'),
                                  fg='#ffffff', bg='#1e1e1e')
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File search
        search_frame = tk.Frame(file_frame, bg='#1e1e1e')
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(search_frame, text="Search:", font=('Segoe UI', 9), 
                fg='#ffffff', bg='#1e1e1e').pack(side=tk.LEFT)
        
        self.search_entry = tk.Entry(search_frame, font=('Segoe UI', 9),
                                    bg='#2d2d2d', fg='#ffffff',
                                    insertbackground='#ffffff')
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.search_entry.bind('<Return>', lambda e: self.search_files())
        
        search_btn = tk.Button(search_frame, text="🔍", command=self.search_files,
                              bg='#007acc', fg='white', font=('Segoe UI', 9))
        search_btn.pack(side=tk.RIGHT)
        
    def setup_ai_operations(self, parent):
        """สร้างส่วน AI operations"""
        ai_frame = tk.LabelFrame(parent, text="🤖 AI Assistant", 
                                font=('Segoe UI', 10, 'bold'),
                                fg='#ffffff', bg='#1e1e1e')
        ai_frame.pack(fill=tk.X, pady=(0, 10))
        
        # AI status
        self.ai_status_label = tk.Label(ai_frame,
                                       text="Status: กำลังเชื่อมต่อ...",
                                       font=('Segoe UI', 9),
                                       fg='#ffaa00',
                                       bg='#1e1e1e')
        self.ai_status_label.pack(pady=5)
        
        # AI actions
        ai_actions = [
            ("🧠 Analyze Structure", self.analyze_structure),
            ("📋 Generate Report", self.generate_report),
            ("💡 Get Suggestions", self.get_suggestions),
            ("🔍 Smart Search", self.smart_search)
        ]
        
        for text, command in ai_actions:
            btn = tk.Button(ai_frame, text=text, command=command,
                           bg='#2d2d2d', fg='#ffffff',
                           font=('Segoe UI', 9), relief=tk.FLAT,
                           padx=10, pady=5)
            btn.pack(fill=tk.X, padx=10, pady=2)
            
    def setup_system_info(self, parent):
        """สร้างส่วนข้อมูลระบบ"""
        info_frame = tk.LabelFrame(parent, text="ℹ️ System Info", 
                                  font=('Segoe UI', 10, 'bold'),
                                  fg='#ffffff', bg='#1e1e1e')
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=6, font=('Consolas', 8),
                                bg='#2d2d2d', fg='#ffffff',
                                insertbackground='#ffffff', state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def setup_input_area(self, parent):
        """สร้างพื้นที่ป้อนข้อมูล"""
        input_frame = ttk.Frame(parent, style='Dark.TFrame')
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Input field with placeholder
        self.input_field = tk.Entry(input_frame,
                                   font=('Segoe UI', 12),
                                   bg='#2d2d2d',
                                   fg='#ffffff',
                                   insertbackground='#ffffff',
                                   relief=tk.FLAT)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_field.bind('<Return>', self.send_message)
        
        # Placeholder text
        self.input_field.insert(0, "💬 พิมพ์คำถามหรือคำสั่ง...")
        self.input_field.bind('<FocusIn>', self.on_entry_click)
        self.input_field.bind('<FocusOut>', self.on_focus_out)
        self.input_field.config(fg='#888888')
        
        # Send button
        send_btn = tk.Button(input_frame,
                            text="🚀 Send",
                            command=self.send_message,
                            bg='#007acc',
                            fg='white',
                            font=('Segoe UI', 11, 'bold'),
                            relief=tk.FLAT,
                            padx=20,
                            pady=8)
        send_btn.pack(side=tk.RIGHT)
        
    def on_entry_click(self, event):
        """เมื่อคลิกที่ input field"""
        if self.input_field.get() == "💬 พิมพ์คำถามหรือคำสั่ง...":
            self.input_field.delete(0, tk.END)
            self.input_field.config(fg='#ffffff')
            
    def on_focus_out(self, event):
        """เมื่อออกจาก input field"""
        if not self.input_field.get():
            self.input_field.insert(0, "💬 พิมพ์คำถามหรือคำสั่ง...")
            self.input_field.config(fg='#888888')
            
    def auto_start_services(self):
        """เริ่มต้นบริการต่างๆ อัตโนมัติ"""
        self.add_system_message("🚀 กำลังเริ่มต้นระบบ...")
        
        # Start File System service
        self.start_file_system_service()
        
        # Start Ollama service
        self.start_ollama_service()
        
    def start_file_system_service(self):
        """เริ่มต้น File System service"""
        def start_fs():
            try:
                # Test File System connection
                test_result = self.tool._run(json.dumps({
                    "action": "query_function",
                    "function": "get_directory_summary",
                    "session_id": "test",
                    "args": []
                }))
                
                self.root.after(0, lambda: self.update_fs_status("✅ Connected", "#00ff00"))
                self.root.after(0, lambda: self.add_system_message("✅ File System service พร้อมใช้งาน"))
                
            except Exception as e:
                self.root.after(0, lambda: self.update_fs_status("❌ Error", "#ff4444"))
                self.root.after(0, lambda: self.add_system_message(f"❌ File System error: {str(e)}"))
                
        threading.Thread(target=start_fs, daemon=True).start()
        
    def start_ollama_service(self):
        """เริ่มต้น Ollama service"""
        def start_ollama():
            try:
                # Test Ollama connection
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    self.ollama_connected = True
                    self.root.after(0, lambda: self.update_ollama_status("✅ Connected", "#00ff00"))
                    self.root.after(0, lambda: self.add_system_message(f"✅ Ollama service พร้อมใช้งาน (พบ {len(models)} models)"))
                else:
                    raise Exception("Ollama server not responding")
                    
            except Exception as e:
                self.root.after(0, lambda: self.update_ollama_status("❌ Not Connected", "#ff4444"))
                self.root.after(0, lambda: self.add_system_message("⚠️ Ollama ไม่พร้อมใช้งาน - ใช้ File System เท่านั้น"))
                
        threading.Thread(target=start_ollama, daemon=True).start()
        
    def update_fs_status(self, text, color):
        """อัปเดตสถานะ File System"""
        self.fs_status.config(text=f"📁 File System: {text}", fg=color)
        
    def update_ollama_status(self, text, color):
        """อัปเดตสถานะ Ollama"""
        self.ollama_status.config(text=f"🤖 Ollama: {text}", fg=color)
        
    def add_message(self, sender, message, message_type="normal"):
        """เพิ่มข้อความในแชต"""
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
        elif message_type == "error":
            formatted_message = f"[{timestamp}] ❌ ข้อผิดพลาด: {message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("error", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("error", foreground="#ff4444")
        elif message_type == "ai":
            formatted_message = f"[{timestamp}] 🤖 AI: {message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("ai", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("ai", foreground="#ff66cc")
        
        self.chat_display.see(tk.END)
        
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
        self.scan_btn.config(state=tk.DISABLED, text="⏳ Scanning...")
        
        # Run scan in separate thread
        thread = threading.Thread(target=self._perform_scan, args=(folder_path,))
        thread.daemon = True
        thread.start()
        
    def _perform_scan(self, folder_path):
        """ทำการสแกนในเธรดแยก"""
        try:
            self.root.after(0, lambda: self.add_system_message(f"🔍 เริ่มสแกนโฟลเดอร์: {folder_path}"))
            
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
                self.root.after(0, lambda: self.add_system_message(f"✅ สแกนเสร็จสิ้น! Session ID: {self.current_session_id}"))
                self.root.after(0, lambda: self.session_status.config(text=f"💾 Session: {self.current_session_id[:8]}..."))
                self.root.after(0, lambda: self.update_system_info())
            else:
                self.root.after(0, lambda: self.add_system_message(f"❌ การสแกนล้มเหลว: {result}"))
                
        except Exception as e:
            self.root.after(0, lambda: self.add_system_message(f"❌ เกิดข้อผิดพลาด: {str(e)}"))
        finally:
            self.scanning = False
            self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL, text="📁 Scan Folder"))
            
    def send_message(self, event=None):
        """ส่งข้อความ"""
        message = self.input_field.get().strip()
        if not message or message == "💬 พิมพ์คำถามหรือคำสั่ง...":
            return
            
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, "💬 พิมพ์คำถามหรือคำสั่ง...")
        self.input_field.config(fg='#888888')
        
        self.add_message("user", message, "user")
        
        # Process message in separate thread
        thread = threading.Thread(target=self._process_message, args=(message,))
        thread.daemon = True
        thread.start()
        
    def _process_message(self, message):
        """ประมวลผลข้อความ"""
        try:
            if not self.current_session_id:
                self.root.after(0, lambda: self.add_system_message("⚠️ กรุณาสแกนโฟลเดอร์ก่อนใช้งาน"))
                return
                
            # Check for special commands
            if message.lower().startswith("/help"):
                self._show_help()
                return
            elif message.lower().startswith("/scan"):
                self.root.after(0, lambda: self.add_system_message("ใช้ปุ่ม 'Scan Folder' เพื่อสแกนโฟลเดอร์ใหม่"))
                return
                
            # Try AI first if available
            if self.ollama_connected and self._should_use_ai(message):
                self._process_with_ai(message)
            else:
                # Use File System query
                self._process_with_filesystem(message)
                
        except Exception as e:
            self.root.after(0, lambda: self.add_message("error", f"เกิดข้อผิดพลาด: {str(e)}", "error"))
            
    def _should_use_ai(self, message):
        """ตรวจสอบว่าควรใช้ AI หรือไม่"""
        ai_keywords = ['analyze', 'explain', 'suggest', 'recommend', 'why', 'how', 'what', 'วิเคราะห์', 'อธิบาย', 'แนะนำ', 'ทำไม', 'อย่างไร', 'อะไร']
        return any(keyword in message.lower() for keyword in ai_keywords)
        
    def _process_with_ai(self, message):
        """ประมวลผลด้วย AI"""
        try:
            # Get file system data first
            fs_data = self._get_filesystem_data()
            
            # Send to Ollama
            ai_response = self._ask_ollama(message, fs_data)
            
            self.root.after(0, lambda: self.add_message("ai", ai_response, "ai"))
            
        except Exception as e:
            # Fallback to File System
            self.root.after(0, lambda: self.add_system_message("⚠️ AI ไม่พร้อม ใช้ File System แทน"))
            self._process_with_filesystem(message)
            
    def _process_with_filesystem(self, message):
        """ประมวลผลด้วย File System"""
        try:
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
                    self.root.after(0, lambda: self.add_message("result", formatted_result, "result"))
                else:
                    self.root.after(0, lambda: self.add_message("error", result_data.get('error', 'ไม่สามารถประมวลผลได้'), "error"))
            except json.JSONDecodeError:
                self.root.after(0, lambda: self.add_message("result", result, "result"))
                
        except Exception as e:
            self.root.after(0, lambda: self.add_message("error", f"เกิดข้อผิดพลาด: {str(e)}", "error"))
            
    def _get_filesystem_data(self):
        """ดึงข้อมูล File System สำหรับ AI"""
        try:
            summary_params = {
                "action": "query_function",
                "function": "get_directory_summary",
                "session_id": self.current_session_id,
                "args": []
            }
            
            result = self.tool._run(json.dumps(summary_params))
            return result
            
        except Exception:
            return "No file system data available"
            
    def _ask_ollama(self, message, fs_data):
        """ถาม Ollama"""
        try:
            # สร้าง prompt ที่ชัดเจนและมี context
            prompt = f"""You are a helpful File System Analysis Assistant. Your job is to analyze file system data and provide clear, useful answers.

FILE SYSTEM DATA:
{fs_data}

USER QUESTION: {message}

TASK: Analyze the file system data above and answer the user's question. Be specific, helpful, and respond in Thai language.

IMPORTANT: Use the actual file system data provided above. Do not say you cannot help with file management - this IS your job.

Please provide a clear, detailed answer:"""
            
            response = requests.post("http://localhost:11434/api/generate", 
                                   json={
                                       "model": "deepseek-coder:6.7b-instruct",
                                       "prompt": prompt,
                                       "stream": False,
                                       "options": {
                                           "temperature": 0.3,
                                           "top_p": 0.8,
                                           "num_predict": 800
                                       }
                                   }, 
                                   timeout=30)
            
            if response.status_code == 200:
                ai_response = response.json().get('response', 'ไม่สามารถประมวลผลได้')
                
                # ตรวจสอบว่า AI ตอบแบบ generic หรือไม่
                generic_phrases = [
                    "i'm sorry", "i cannot", "outside of my", "programming assistant",
                    "computer science", "cannot assist", "not related", "file management",
                    "ซีมิส์", "ตัวมีนตัง", "ประยาว", "พิสูจน์"
                ]
                
                if any(phrase in ai_response.lower() for phrase in generic_phrases):
                    return self._generate_fallback_response(message, fs_data)
                
                return ai_response
            else:
                raise Exception("Ollama request failed")
                
        except Exception as e:
            return self._generate_fallback_response(message, fs_data)
            
    def _generate_fallback_response(self, message, fs_data):
        """สร้าง fallback response เมื่อ AI ไม่เข้าใจ"""
        try:
            # Parse file system data
            if isinstance(fs_data, str):
                # Try to parse JSON from string
                import re
                json_match = re.search(r'\{.*\}', fs_data, re.DOTALL)
                if json_match:
                    fs_data = json.loads(json_match.group())
                else:
                    return f"ไม่สามารถวิเคราะห์ข้อมูลได้: {fs_data}"
            
            # Generate response based on question type
            message_lower = message.lower()
            
            if "summary" in message_lower or "สรุป" in message_lower:
                return self._generate_summary_response(fs_data)
            elif "large" in message_lower or "ใหญ่" in message_lower:
                return self._generate_large_files_response(fs_data)
            elif "duplicate" in message_lower or "ซ้ำ" in message_lower:
                return self._generate_duplicate_response(fs_data)
            elif "analyze" in message_lower or "วิเคราะห์" in message_lower:
                return self._generate_analysis_response(fs_data)
            else:
                return self._generate_general_response(fs_data, message)
                
        except Exception as e:
            return f"เกิดข้อผิดพลาดในการวิเคราะห์: {str(e)}"
            
    def _generate_summary_response(self, fs_data):
        """สร้าง response สำหรับ summary"""
        try:
            # Query for comprehensive summary
            summary_params = {
                "action": "query_function",
                "function": "get_directory_summary",
                "session_id": self.current_session_id,
                "args": []
            }
            
            result = self.tool._run(json.dumps(summary_params))
            summary_data = json.loads(result)
            
            if summary_data.get('success') and summary_data.get('summary'):
                summary = summary_data['summary']
                
                # Get file types breakdown
                file_types = summary.get('file_types', {})
                total_files = summary.get('total_files', 0)
                total_size_mb = summary.get('total_size_mb', 0)
                average_size = summary.get('average_size', 0)
                
                response = f"""📊 สรุปข้อมูลไฟล์ระบบ:

📁 ข้อมูลทั่วไป:
• จำนวนไฟล์ทั้งหมด: {total_files:,} ไฟล์
• ขนาดรวม: {total_size_mb:.2f} MB ({summary.get('total_size', 0):,} bytes)
• ขนาดเฉลี่ย: {average_size:,.0f} bytes

📋 การกระจายประเภทไฟล์:"""
                
                # Show top file types
                if file_types:
                    sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
                    for ext, count in sorted_types[:8]:
                        percentage = (count / total_files * 100) if total_files > 0 else 0
                        response += f"\n• {ext}: {count:,} ไฟล์ ({percentage:.1f}%)"
                
                # Show largest files
                largest_files = summary.get('largest_files', [])
                if largest_files:
                    response += f"\n\n🔝 ไฟล์ขนาดใหญ่ที่สุด:"
                    for i, file_info in enumerate(largest_files[:3], 1):
                        size_mb = file_info.get('file_size', 0) / (1024 * 1024)
                        response += f"\n{i}. {file_info.get('file_name', 'Unknown')} ({size_mb:.2f} MB)"
                
                # Analysis and recommendations
                response += f"\n\n💡 การวิเคราะห์:"
                if total_files < 50:
                    response += f"\n• ระบบมีไฟล์จำนวนน้อย ({total_files} ไฟล์) - เหมาะสำหรับโปรเจคขนาดเล็ก"
                elif total_files < 500:
                    response += f"\n• ระบบมีไฟล์จำนวนปานกลาง ({total_files} ไฟล์) - ควรจัดระเบียบเป็นระยะ"
                else:
                    response += f"\n• ระบบมีไฟล์จำนวนมาก ({total_files} ไฟล์) - ควรจัดระเบียบอย่างเร่งด่วน"
                
                if total_size_mb < 100:
                    response += f"\n• ใช้พื้นที่น้อย ({total_size_mb:.2f} MB) - ประหยัดพื้นที่จัดเก็บ"
                elif total_size_mb < 1000:
                    response += f"\n• ใช้พื้นที่ปานกลาง ({total_size_mb:.2f} MB) - ควรตรวจสอบไฟล์ใหญ่"
                else:
                    response += f"\n• ใช้พื้นที่มาก ({total_size_mb:.2f} MB) - ควรหาวิธีลดขนาด"
                
                if len(file_types) < 10:
                    response += f"\n• มีประเภทไฟล์น้อย ({len(file_types)} ประเภท) - โครงสร้างเรียบง่าย"
                else:
                    response += f"\n• มีประเภทไฟล์หลากหลาย ({len(file_types)} ประเภท) - ควรจัดกลุ่ม"
                
                return response
            else:
                return "ไม่สามารถดึงข้อมูลสรุปได้"
        except Exception as e:
            return f"เกิดข้อผิดพลาดในการสร้างสรุป: {str(e)}"
            
    def _generate_large_files_response(self, fs_data):
        """สร้าง response สำหรับ large files"""
        try:
            # Query for largest files specifically
            large_files_params = {
                "action": "query_sql",
                "sql": "SELECT file_name, file_path, file_size FROM files WHERE session_id = ? ORDER BY file_size DESC LIMIT 5",
                "params": [self.current_session_id]
            }
            
            result = self.tool._run(json.dumps(large_files_params))
            large_files_data = json.loads(result)
            
            if large_files_data.get('success') and large_files_data.get('data'):
                files = large_files_data['data']
                if files:
                    response = "🔍 ไฟล์ขนาดใหญ่ที่สุดในระบบ:\n\n"
                    for i, file_info in enumerate(files, 1):
                        size_mb = file_info.get('file_size', 0) / (1024 * 1024)
                        response += f"{i}. 📄 {file_info.get('file_name', 'Unknown')}\n"
                        response += f"   📁 Path: {file_info.get('file_path', 'Unknown')}\n"
                        response += f"   💾 Size: {size_mb:.2f} MB ({file_info.get('file_size', 0):,} bytes)\n\n"
                    
                    response += "💡 ข้อสังเกต:\n"
                    response += f"• ไฟล์ที่ใหญ่ที่สุด: {files[0].get('file_name', 'Unknown')} ({files[0].get('file_size', 0) / (1024*1024):.2f} MB)\n"
                    response += f"• ไฟล์ที่เล็กที่สุดในรายการ: {files[-1].get('file_name', 'Unknown')} ({files[-1].get('file_size', 0) / (1024*1024):.2f} MB)\n"
                    
                    return response
                else:
                    return "ไม่พบไฟล์ในระบบ"
            else:
                return "ไม่สามารถดึงข้อมูลไฟล์ขนาดใหญ่ได้"
        except Exception as e:
            return f"เกิดข้อผิดพลาดในการวิเคราะห์ไฟล์ขนาดใหญ่: {str(e)}"
            
    def _generate_duplicate_response(self, fs_data):
        """สร้าง response สำหรับ duplicates"""
        try:
            # Query for duplicates
            duplicate_params = {
                "action": "query_function",
                "function": "get_duplicate_files",
                "session_id": self.current_session_id,
                "args": []
            }
            
            result = self.tool._run(json.dumps(duplicate_params))
            duplicate_data = json.loads(result)
            
            if duplicate_data.get('success') and duplicate_data.get('duplicates'):
                duplicates = duplicate_data['duplicates']
                response = "🔄 ไฟล์ซ้ำที่พบ:\n\n"
                
                for i, dup in enumerate(duplicates[:3], 1):
                    response += f"{i}. 🔗 Hash: {dup.get('hash_md5', 'Unknown')[:8]}...\n"
                    response += f"   📊 จำนวนไฟล์: {dup.get('count', 0)} ไฟล์\n"
                    response += f"   💾 ขนาดรวม: {dup.get('total_size', 0) / (1024*1024):.2f} MB\n"
                    response += f"   ⚠️ พื้นที่เสีย: {dup.get('wasted_space', 0) / (1024*1024):.2f} MB\n\n"
                    
                    for file_info in dup.get('files', [])[:2]:
                        response += f"      📄 {file_info.get('file_name', 'Unknown')}\n"
                    response += "\n"
                    
                return response
            else:
                return "✅ ไม่พบไฟล์ซ้ำในระบบ"
        except Exception as e:
            return f"เกิดข้อผิดพลาดในการค้นหาไฟล์ซ้ำ: {str(e)}"
            
    def _generate_analysis_response(self, fs_data):
        """สร้าง response สำหรับ analysis"""
        try:
            if isinstance(fs_data, dict) and 'summary' in fs_data:
                summary = fs_data['summary']
                total_files = summary.get('total_files', 0)
                total_size_mb = summary.get('total_size_mb', 0)
                file_types = summary.get('file_types', {})
                
                response = "🧠 การวิเคราะห์โครงสร้างไฟล์:\n\n"
                
                # File type analysis
                response += "📋 การกระจายประเภทไฟล์:\n"
                for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                    percentage = (count / total_files * 100) if total_files > 0 else 0
                    response += f"   • {ext}: {count} ไฟล์ ({percentage:.1f}%)\n"
                
                response += f"\n📊 สถิติทั่วไป:\n"
                response += f"   • ไฟล์ทั้งหมด: {total_files:,} ไฟล์\n"
                response += f"   • ขนาดรวม: {total_size_mb:.2f} MB\n"
                response += f"   • ขนาดเฉลี่ย: {summary.get('average_size', 0):,.0f} bytes\n"
                
                # Recommendations
                response += f"\n💡 คำแนะนำ:\n"
                if total_files > 100:
                    response += "   • ระบบมีไฟล์จำนวนมาก ควรจัดระเบียบ\n"
                if total_size_mb > 1000:
                    response += "   • ใช้พื้นที่มาก ควรตรวจสอบไฟล์ที่ไม่จำเป็น\n"
                if len(file_types) > 20:
                    response += "   • มีประเภทไฟล์หลากหลาย ควรจัดกลุ่ม\n"
                    
                return response
            else:
                return "ไม่สามารถวิเคราะห์โครงสร้างได้"
        except Exception as e:
            return f"เกิดข้อผิดพลาดในการวิเคราะห์: {str(e)}"
            
    def _generate_general_response(self, fs_data, message):
        """สร้าง response ทั่วไป"""
        try:
            if isinstance(fs_data, dict) and 'summary' in fs_data:
                summary = fs_data['summary']
                return f"""🤖 การตอบสนองสำหรับ: "{message}"

📊 ข้อมูลปัจจุบัน:
• ไฟล์ทั้งหมด: {summary.get('total_files', 'N/A')} ไฟล์
• ขนาดรวม: {summary.get('total_size_mb', 'N/A')} MB
• ประเภทไฟล์: {len(summary.get('file_types', {}))} ประเภท

💡 ใช้คำสั่งต่อไปนี้เพื่อข้อมูลเพิ่มเติม:
• "give me summary" - สรุปข้อมูล
• "show me large files" - ไฟล์ขนาดใหญ่
• "find duplicate files" - ไฟล์ซ้ำ
• "analyze structure" - วิเคราะห์โครงสร้าง"""
            else:
                return f"ไม่สามารถประมวลผลคำถาม '{message}' ได้ กรุณาลองคำสั่งอื่น"
        except Exception as e:
            return f"เกิดข้อผิดพลาด: {str(e)}"
            
    def _format_file_types(self, file_types):
        """จัดรูปแบบประเภทไฟล์"""
        if not file_types:
            return "ไม่พบข้อมูล"
            
        formatted = []
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]:
            formatted.append(f"   • {ext}: {count} ไฟล์")
        return "\n".join(formatted)
        
    def _format_largest_files(self, largest_files):
        """จัดรูปแบบไฟล์ขนาดใหญ่"""
        if not largest_files:
            return "ไม่พบข้อมูล"
            
        formatted = []
        for i, file_info in enumerate(largest_files[:3], 1):
            size_mb = file_info.get('file_size', 0) / (1024 * 1024)
            formatted.append(f"   {i}. {file_info.get('file_name', 'Unknown')} ({size_mb:.2f} MB)")
        return "\n".join(formatted)
        
    def quick_query(self, query):
        """คำถามด่วน"""
        if not self.current_session_id:
            self.add_system_message("⚠️ กรุณาสแกนโฟลเดอร์ก่อนใช้งาน")
            return
            
        self.add_message("user", query, "user")
        
        # Process in thread
        thread = threading.Thread(target=self._process_message, args=(query,))
        thread.daemon = True
        thread.start()
        
    def search_files(self):
        """ค้นหาไฟล์"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            return
            
        if not self.current_session_id:
            self.add_system_message("⚠️ กรุณาสแกนโฟลเดอร์ก่อนใช้งาน")
            return
            
        self.add_message("user", f"search: {search_term}", "user")
        
        # Process in thread
        thread = threading.Thread(target=self._process_message, args=(f"find files containing {search_term}",))
        thread.daemon = True
        thread.start()
        
    def analyze_structure(self):
        """วิเคราะห์โครงสร้าง"""
        if not self.current_session_id:
            self.add_system_message("⚠️ กรุณาสแกนโฟลเดอร์ก่อนใช้งาน")
            return
            
        self.add_message("user", "analyze the file structure and explain what this project is about", "user")
        
        thread = threading.Thread(target=self._process_message, args=("analyze the file structure and explain what this project is about",))
        thread.daemon = True
        thread.start()
        
    def generate_report(self):
        """สร้างรายงาน"""
        if not self.current_session_id:
            self.add_system_message("⚠️ กรุณาสแกนโฟลเดอร์ก่อนใช้งาน")
            return
            
        self.add_message("user", "generate a comprehensive report about this file system", "user")
        
        thread = threading.Thread(target=self._process_message, args=("generate a comprehensive report about this file system",))
        thread.daemon = True
        thread.start()
        
    def get_suggestions(self):
        """ได้คำแนะนำ"""
        if not self.current_session_id:
            self.add_system_message("⚠️ กรุณาสแกนโฟลเดอร์ก่อนใช้งาน")
            return
            
        self.add_message("user", "what suggestions do you have for improving this file organization", "user")
        
        thread = threading.Thread(target=self._process_message, args=("what suggestions do you have for improving this file organization",))
        thread.daemon = True
        thread.start()
        
    def smart_search(self):
        """ค้นหาอัจฉริยะ"""
        if not self.current_session_id:
            self.add_system_message("⚠️ กรุณาสแกนโฟลเดอร์ก่อนใช้งาน")
            return
            
        self.add_message("user", "perform a smart search to find important files and patterns", "user")
        
        thread = threading.Thread(target=self._process_message, args=("perform a smart search to find important files and patterns",))
        thread.daemon = True
        thread.start()
        
    def update_system_info(self):
        """อัปเดตข้อมูลระบบ"""
        try:
            if self.current_session_id:
                # Get basic stats
                stats_params = {
                    "action": "query_function",
                    "function": "get_directory_summary",
                    "session_id": self.current_session_id,
                    "args": []
                }
                
                result = self.tool._run(json.dumps(stats_params))
                result_data = json.loads(result)
                
                info_text = f"""
Session: {self.current_session_id[:8]}...
Files: {result_data.get('total_files', 'N/A')}
Size: {result_data.get('total_size_mb', 'N/A')} MB
Types: {len(result_data.get('file_types', []))} types

Ollama: {'✅ Connected' if self.ollama_connected else '❌ Not Connected'}
Models: Available for AI analysis
                """
                
                self.info_text.config(state=tk.NORMAL)
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(1.0, info_text)
                self.info_text.config(state=tk.DISABLED)
                
        except Exception as e:
            pass
            
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

🤖 AI Assistant (ถ้าเชื่อมต่อ Ollama):
• "analyze this project" - วิเคราะห์โปรเจค
• "explain the structure" - อธิบายโครงสร้าง
• "suggest improvements" - แนะนำการปรับปรุง

💾 SQL Queries:
• "SELECT * FROM files WHERE file_size > 1000000" - ค้นหาด้วย SQL

🔧 Special Commands:
• /help - แสดงความช่วยเหลือ
• /scan - ข้อมูลการสแกน

💡 Tips:
• ใช้ภาษาธรรมชาติในการค้นหา
• AI จะช่วยวิเคราะห์และให้คำแนะนำ
• คลิกขวาเพื่อคัดลอกข้อความ
        """
        self.add_system_message(help_text)

def main():
    """ฟังก์ชันหลัก"""
    try:
        root = tk.Tk()
        app = UnifiedChatApp(root)
        
        # Center window
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Force focus and show window
        root.focus_force()
        root.deiconify()
        
        print("🚀 Unified Chat App พร้อมใช้งาน!")
        print("✅ ระบบจะเชื่อมต่อ File System และ Ollama อัตโนมัติ")
        print("�� หน้าต่าง GUI ควรปรากฏแล้ว")
        
        root.mainloop()
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        input("กด Enter เพื่อปิด...")

if __name__ == "__main__":
    main()
