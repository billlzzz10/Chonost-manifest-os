#!/usr/bin/env python3
"""
File System MCP Desktop Chat App
แอปเดสทอปแบบแชตสำหรับวิเคราะห์ไฟล์ระบบ
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

class FileSystemChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File System MCP Chat")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Force window to front
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        
        # Initialize File System Tool
        self.tool = FileSystemMCPTool()
        self.current_session_id = None
        self.scanning = False
        
        # Setup UI
        self.setup_ui()
        self.setup_styles()
        
        # Welcome message
        self.add_system_message("🚀 ยินดีต้อนรับสู่ File System MCP Chat!")
        self.add_system_message("💡 คุณสามารถ:\n• สแกนโฟลเดอร์\n• ค้นหาไฟล์ด้วยภาษาธรรมชาติ\n• วิเคราะห์ข้อมูลไฟล์\n• ดูสถิติต่างๆ")
        
    def setup_styles(self):
        """ตั้งค่าสไตล์ของ UI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Chat.TFrame', background='#2b2b2b')
        style.configure('Input.TFrame', background='#3c3c3c')
        style.configure('Button.TButton', 
                       background='#007acc', 
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'))
        
    def setup_ui(self):
        """สร้าง UI หลัก"""
        # Main container
        main_frame = ttk.Frame(self.root, style='Chat.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="File System MCP Chat", 
                              font=('Segoe UI', 16, 'bold'),
                              fg='#ffffff',
                              bg='#2b2b2b')
        title_label.pack(pady=(0, 10))
        
        # Chat area
        self.setup_chat_area(main_frame)
        
        # Control panel
        self.setup_control_panel(main_frame)
        
        # Input area
        self.setup_input_area(main_frame)
        
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
        
        # Session info
        self.session_label = tk.Label(control_frame,
                                     text="Session: ไม่มี",
                                     font=('Segoe UI', 9),
                                     fg='#cccccc',
                                     bg='#3c3c3c')
        self.session_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Status
        self.status_label = tk.Label(control_frame,
                                    text="พร้อมใช้งาน",
                                    font=('Segoe UI', 9),
                                    fg='#00ff00',
                                    bg='#3c3c3c')
        self.status_label.pack(side=tk.RIGHT)
        
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
        elif message_type == "error":
            formatted_message = f"[{timestamp}] ❌ ข้อผิดพลาด: {message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("error", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("error", foreground="#ff4444")
        
        self.chat_display.config(state=tk.DISABLED)
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
        self.status_label.config(text="กำลังสแกน...", fg='#ffaa00')
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
            else:
                self.add_system_message(f"❌ การสแกนล้มเหลว: {result}")
                
        except Exception as e:
            self.add_system_message(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        finally:
            self.scanning = False
            self.status_label.config(text="พร้อมใช้งาน", fg='#00ff00')
            self.scan_btn.config(state=tk.NORMAL)
            
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

💾 SQL Queries:
• "SELECT * FROM files WHERE file_size > 1000000" - ค้นหาด้วย SQL

🔧 Special Commands:
• /help - แสดงความช่วยเหลือ
• /scan - ข้อมูลการสแกน

💡 Tips:
• ใช้ภาษาธรรมชาติในการค้นหา
• ระบบจะประมวลผลแบบ real-time
• ผลลัพธ์จะแสดงในรูปแบบตาราง
        """
        self.add_system_message(help_text)

def main():
    """ฟังก์ชันหลัก"""
    try:
        root = tk.Tk()
        app = FileSystemChatApp(root)
        
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
        
        print("🚀 แอปแชตพร้อมใช้งาน! หน้าต่าง GUI ควรปรากฏแล้ว")
        print("💡 หากไม่เห็นหน้าต่าง ให้ตรวจสอบ:")
        print("   • หน้าจออื่น (Alt+Tab)")
        print("   • Taskbar")
        print("   • หน้าต่างที่ถูกย่อขนาด")
        
        root.mainloop()
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเปิดแอป: {str(e)}")
        input("กด Enter เพื่อปิด...")

if __name__ == "__main__":
    main()
