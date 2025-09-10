#!/usr/bin/env python3
"""
Advanced File System MCP Desktop Chat App
แอปเดสทอปแบบแชตขั้นสูงสำหรับวิเคราะห์ไฟล์ระบบ
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

class AdvancedFileSystemChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced File System MCP Chat")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Initialize components
        self.tool = FileSystemMCPTool()
        self.current_session_id = None
        self.scanning = False
        self.chat_history = []
        
        # Setup UI
        self.setup_ui()
        self.setup_styles()
        
        # Welcome message
        self.add_system_message("🚀 ยินดีต้อนรับสู่ Advanced File System MCP Chat!")
        self.add_system_message("💡 ฟีเจอร์ใหม่:\n• 📊 แสดงผลแบบกราฟ\n• 💾 บันทึกการสนทนา\n• 🔍 ค้นหาขั้นสูง\n• 🎨 UI ที่สวยงาม")
        
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
        
        # Analysis tab
        self.setup_analysis_tab()
        
    def setup_title_bar(self, parent):
        """สร้างแถบหัวข้อ"""
        title_frame = ttk.Frame(parent, style='Main.TFrame')
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(title_frame, 
                              text="Advanced File System MCP Chat", 
                              font=('Segoe UI', 18, 'bold'),
                              fg='#ffffff',
                              bg='#1e1e1e')
        title_label.pack(side=tk.LEFT)
        
        # Status indicators
        status_frame = ttk.Frame(title_frame, style='Main.TFrame')
        status_frame.pack(side=tk.RIGHT)
        
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
        
    def setup_analysis_tab(self):
        """สร้างแท็บการวิเคราะห์"""
        analysis_frame = ttk.Frame(self.notebook, style='Chat.TFrame')
        self.notebook.add(analysis_frame, text="📊 การวิเคราะห์")
        
        # Analysis controls
        controls_frame = ttk.Frame(analysis_frame, style='Chat.TFrame')
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Quick analysis buttons
        quick_buttons = [
            ("📈 สถิติไฟล์", self.quick_file_stats),
            ("🔍 ไฟล์ซ้ำ", self.quick_duplicates),
            ("📁 โครงสร้าง", self.quick_structure),
            ("💾 ขนาดไฟล์", self.quick_size_analysis)
        ]
        
        for text, command in quick_buttons:
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
        
        # Analysis display
        self.analysis_display = scrolledtext.ScrolledText(
            analysis_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#ffffff',
            insertbackground='#ffffff',
            selectbackground='#007acc',
            state=tk.DISABLED
        )
        self.analysis_display.pack(fill=tk.BOTH, expand=True)
        
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
                              bg='#28a745',
                              fg='white',
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
            else:
                self.add_system_message(f"❌ การสแกนล้มเหลว: {result}")
                
        except Exception as e:
            self.add_system_message(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        finally:
            self.scanning = False
            self.status_label.config(text="🟢 พร้อมใช้งาน", fg='#00ff00')
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
            elif message.lower().startswith("/clear"):
                self.clear_chat()
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

🔧 Special Commands:
• /help - แสดงความช่วยเหลือ
• /scan - ข้อมูลการสแกน
• /clear - ล้างแชต

💡 Tips:
• ใช้ภาษาธรรมชาติในการค้นหา
• ระบบจะประมวลผลแบบ real-time
• ผลลัพธ์จะแสดงในรูปแบบตาราง
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
                    f.write("File System MCP Chat Export\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Session ID: {self.current_session_id}\n")
                    f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(chat_content)
                    
                messagebox.showinfo("สำเร็จ", f"ส่งออกผลลัพธ์ไปยัง {filename}")
            except Exception as e:
                messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถส่งออกได้: {str(e)}")
                
    # Quick analysis methods
    def quick_file_stats(self):
        """สถิติไฟล์ด่วน"""
        if not self.current_session_id:
            messagebox.showwarning("ไม่มีข้อมูล", "กรุณาสแกนโฟลเดอร์ก่อนใช้งาน")
            return
            
        try:
            result = self.tool._run(json.dumps({
                "action": "query_function",
                "function": "get_directory_summary",
                "session_id": self.current_session_id
            }))
            
            self.analysis_display.config(state=tk.NORMAL)
            self.analysis_display.delete(1.0, tk.END)
            self.analysis_display.insert(1.0, f"📈 สถิติไฟล์\n{result}")
            self.analysis_display.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", str(e))
            
    def quick_duplicates(self):
        """ไฟล์ซ้ำด่วน"""
        if not self.current_session_id:
            messagebox.showwarning("ไม่มีข้อมูล", "กรุณาสแกนโฟลเดอร์ก่อนใช้งาน")
            return
            
        try:
            result = self.tool._run(json.dumps({
                "action": "query_function",
                "function": "get_duplicate_files",
                "session_id": self.current_session_id
            }))
            
            self.analysis_display.config(state=tk.NORMAL)
            self.analysis_display.delete(1.0, tk.END)
            self.analysis_display.insert(1.0, f"🔍 ไฟล์ซ้ำ\n{result}")
            self.analysis_display.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", str(e))
            
    def quick_structure(self):
        """โครงสร้างด่วน"""
        if not self.current_session_id:
            messagebox.showwarning("ไม่มีข้อมูล", "กรุณาสแกนโฟลเดอร์ก่อนใช้งาน")
            return
            
        try:
            result = self.tool._run(json.dumps({
                "action": "query_sql",
                "sql": "SELECT parent_directory, COUNT(*) as file_count FROM files WHERE session_id = ? GROUP BY parent_directory ORDER BY file_count DESC LIMIT 10",
                "params": [self.current_session_id]
            }))
            
            self.analysis_display.config(state=tk.NORMAL)
            self.analysis_display.delete(1.0, tk.END)
            self.analysis_display.insert(1.0, f"📁 โครงสร้างโฟลเดอร์\n{result}")
            self.analysis_display.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", str(e))
            
    def quick_size_analysis(self):
        """วิเคราะห์ขนาดด่วน"""
        if not self.current_session_id:
            messagebox.showwarning("ไม่มีข้อมูล", "กรุณาสแกนโฟลเดอร์ก่อนใช้งาน")
            return
            
        try:
            result = self.tool._run(json.dumps({
                "action": "query_function",
                "function": "get_largest_files",
                "session_id": self.current_session_id,
                "args": [10]
            }))
            
            self.analysis_display.config(state=tk.NORMAL)
            self.analysis_display.delete(1.0, tk.END)
            self.analysis_display.insert(1.0, f"💾 ไฟล์ขนาดใหญ่\n{result}")
            self.analysis_display.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", str(e))

def main():
    """ฟังก์ชันหลัก"""
    root = tk.Tk()
    app = AdvancedFileSystemChatApp(root)
    
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
