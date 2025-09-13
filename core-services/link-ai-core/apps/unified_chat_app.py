#!/usr/bin/env python3
"""
Unified File System MCP Chat App.
A centralized chat application that automatically connects everything.
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
    """
    A unified chat application for the File System MCP.

    Attributes:
        root: The root Tkinter window.
        tool (FileSystemMCPTool): The file system analysis tool.
        current_session_id (str): The current scan session ID.
        scanning (bool): A flag indicating if a scan is in progress.
        ollama_connected (bool): A flag indicating if Ollama is connected.
        ollama_client: The Ollama client.
    """
    def __init__(self, root):
        """
        Initializes the UnifiedChatApp.

        Args:
            root: The root Tkinter window.
        """
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
        """Sets up the UI styles."""
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
        """Creates the main UI."""
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
        """
        Creates the header with status indicators.

        Args:
            parent: The parent widget.
        """
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
                                 text="📁 File System: Connecting...",
                                 font=('Segoe UI', 9),
                                 fg='#ffaa00',
                                 bg='#1e1e1e')
        self.fs_status.pack(side=tk.LEFT, padx=(0, 10))
        
        # Ollama Status
        self.ollama_status = tk.Label(status_frame,
                                     text="🤖 Ollama: Connecting...",
                                     font=('Segoe UI', 9),
                                     fg='#ffaa00',
                                     bg='#1e1e1e')
        self.ollama_status.pack(side=tk.LEFT, padx=(0, 10))
        
        # Session Status
        self.session_status = tk.Label(status_frame,
                                      text="💾 Session: None",
                                      font=('Segoe UI', 9),
                                      fg='#cccccc',
                                      bg='#1e1e1e')
        self.session_status.pack(side=tk.LEFT)
        
    def setup_chat_area(self, parent):
        """
        Creates the chat area.

        Args:
            parent: The parent widget.
        """
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
        """Creates the right-click context menu for copy/paste."""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="📋 Copy", command=self.copy_selected)
        self.context_menu.add_command(label="📋 Copy All", command=self.copy_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Clear Chat", command=self.clear_chat)
        
        self.chat_display.bind("<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        """
        Shows the right-click context menu.

        Args:
            event: The event that triggered the menu.
        """
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
            
    def copy_selected(self):
        """Copies the selected text."""
        try:
            selected_text = self.chat_display.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.add_system_message("✅ Text copied")
        except tk.TclError:
            self.add_system_message("⚠️ No text selected")
            
    def copy_all(self):
        """Copies all text."""
        all_text = self.chat_display.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(all_text)
        self.add_system_message("✅ All text copied")
        
    def clear_chat(self):
        """Clears the chat."""
        self.chat_display.delete(1.0, tk.END)
        self.add_system_message("🗑️ Chat cleared")
        
    def setup_control_panel(self, parent):
        """
        Creates the control panel.

        Args:
            parent: The parent widget.
        """
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
        """
        Creates the quick action buttons.

        Args:
            parent: The parent widget.
        """
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
        """
        Creates the file operations section.

        Args:
            parent: The parent widget.
        """
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
        """
        Creates the AI operations section.

        Args:
            parent: The parent widget.
        """
        ai_frame = tk.LabelFrame(parent, text="🤖 AI Assistant", 
                                font=('Segoe UI', 10, 'bold'),
                                fg='#ffffff', bg='#1e1e1e')
        ai_frame.pack(fill=tk.X, pady=(0, 10))
        
        # AI status
        self.ai_status_label = tk.Label(ai_frame,
                                       text="Status: Connecting...",
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
        """
        Creates the system info section.

        Args:
            parent: The parent widget.
        """
        info_frame = tk.LabelFrame(parent, text="ℹ️ System Info", 
                                  font=('Segoe UI', 10, 'bold'),
                                  fg='#ffffff', bg='#1e1e1e')
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=6, font=('Consolas', 8),
                                bg='#2d2d2d', fg='#ffffff',
                                insertbackground='#ffffff', state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def setup_input_area(self, parent):
        """
        Creates the input area.

        Args:
            parent: The parent widget.
        """
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
        self.input_field.insert(0, "💬 Type a question or command...")
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
        """
        Handles the event when the input field is clicked.

        Args:
            event: The event that triggered the handler.
        """
        if self.input_field.get() == "💬 Type a question or command...":
            self.input_field.delete(0, tk.END)
            self.input_field.config(fg='#ffffff')
            
    def on_focus_out(self, event):
        """
        Handles the event when the input field loses focus.

        Args:
            event: The event that triggered the handler.
        """
        if not self.input_field.get():
            self.input_field.insert(0, "💬 Type a question or command...")
            self.input_field.config(fg='#888888')
            
    def auto_start_services(self):
        """Automatically starts the required services."""
        self.add_system_message("🚀 Starting system...")
        
        # Start File System service
        self.start_file_system_service()
        
        # Start Ollama service
        self.start_ollama_service()
        
    def start_file_system_service(self):
        """Starts the File System service."""
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
                self.root.after(0, lambda: self.add_system_message("✅ File System service is ready."))
                
            except Exception as e:
                self.root.after(0, lambda: self.update_fs_status("❌ Error", "#ff4444"))
                self.root.after(0, lambda: self.add_system_message(f"❌ File System error: {str(e)}"))
                
        threading.Thread(target=start_fs, daemon=True).start()
        
    def start_ollama_service(self):
        """Starts the Ollama service."""
        def start_ollama():
            try:
                # Test Ollama connection
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    self.ollama_connected = True
                    self.root.after(0, lambda: self.update_ollama_status("✅ Connected", "#00ff00"))
                    self.root.after(0, lambda: self.add_system_message(f"✅ Ollama service is ready ({len(models)} models found)."))
                else:
                    raise Exception("Ollama server not responding")
                    
            except Exception as e:
                self.root.after(0, lambda: self.update_ollama_status("❌ Not Connected", "#ff4444"))
                self.root.after(0, lambda: self.add_system_message("⚠️ Ollama is not available - using File System only."))
                
        threading.Thread(target=start_ollama, daemon=True).start()
        
    def update_fs_status(self, text, color):
        """
        Updates the File System status.

        Args:
            text (str): The status text.
            color (str): The color of the status text.
        """
        self.fs_status.config(text=f"📁 File System: {text}", fg=color)
        
    def update_ollama_status(self, text, color):
        """
        Updates the Ollama status.

        Args:
            text (str): The status text.
            color (str): The color of the status text.
        """
        self.ollama_status.config(text=f"🤖 Ollama: {text}", fg=color)
        
    def add_message(self, sender: str, message: str, message_type: str = "normal"):
        """
        Adds a message to the chat.

        Args:
            sender (str): The sender of the message.
            message (str): The message content.
            message_type (str, optional): The type of the message. Defaults to "normal".
        """
        # Timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Format message based on type
        if message_type == "system":
            formatted_message = f"[{timestamp}] 🤖 {message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("system", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("system", foreground="#00ff00")
        elif message_type == "user":
            formatted_message = f"[{timestamp}] 👤 You: {message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("user", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("user", foreground="#007acc")
        elif message_type == "result":
            formatted_message = f"[{timestamp}] 📊 Result:\n{message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("result", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("result", foreground="#ffaa00")
        elif message_type == "error":
            formatted_message = f"[{timestamp}] ❌ Error: {message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("error", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("error", foreground="#ff4444")
        elif message_type == "ai":
            formatted_message = f"[{timestamp}] 🤖 AI: {message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("ai", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("ai", foreground="#ff66cc")
        
        self.chat_display.see(tk.END)
        
    def add_system_message(self, message: str):
        """
        Adds a system message to the chat.

        Args:
            message (str): The system message.
        """
        self.add_message("system", message, "system")
        
    def scan_folder(self):
        """Scans a folder."""
        if self.scanning:
            messagebox.showwarning("Scanning", "Please wait for the current scan to finish.")
            return
            
        folder_path = filedialog.askdirectory(title="Select a folder to scan")
        if not folder_path:
            return
            
        self.scanning = True
        self.scan_btn.config(state=tk.DISABLED, text="⏳ Scanning...")
        
        # Run scan in separate thread
        thread = threading.Thread(target=self._perform_scan, args=(folder_path,))
        thread.daemon = True
        thread.start()
        
    def _perform_scan(self, folder_path: str):
        """
        Performs the scan in a separate thread.

        Args:
            folder_path (str): The path to the folder to scan.
        """
        try:
            self.root.after(0, lambda: self.add_system_message(f"🔍 Starting to scan folder: {folder_path}"))
            
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
                self.root.after(0, lambda: self.add_system_message(f"✅ Scan complete! Session ID: {self.current_session_id}"))
                self.root.after(0, lambda: self.session_status.config(text=f"💾 Session: {self.current_session_id[:8]}..."))
                self.root.after(0, lambda: self.update_system_info())
            else:
                self.root.after(0, lambda: self.add_system_message(f"❌ Scan failed: {result}"))
                
        except Exception as e:
            self.root.after(0, lambda: self.add_system_message(f"❌ An error occurred: {str(e)}"))
        finally:
            self.scanning = False
            self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL, text="📁 Scan Folder"))
            
    def send_message(self, event=None):
        """Sends a message."""
        message = self.input_field.get().strip()
        if not message or message == "💬 Type a question or command...":
            return
            
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, "💬 Type a question or command...")
        self.input_field.config(fg='#888888')
        
        self.add_message("user", message, "user")
        
        # Process message in separate thread
        thread = threading.Thread(target=self._process_message, args=(message,))
        thread.daemon = True
        thread.start()
        
    def _process_message(self, message: str):
        """
        Processes a message.

        Args:
            message (str): The message to process.
        """
        try:
            if not self.current_session_id:
                self.root.after(0, lambda: self.add_system_message("⚠️ Please scan a folder before use."))
                return
                
            # Check for special commands
            if message.lower().startswith("/help"):
                self._show_help()
                return
            elif message.lower().startswith("/scan"):
                self.root.after(0, lambda: self.add_system_message("Use the 'Scan Folder' button to scan a new folder."))
                return
                
            # Try AI first if available
            if self.ollama_connected and self._should_use_ai(message):
                self._process_with_ai(message)
            else:
                # Use File System query
                self._process_with_filesystem(message)
                
        except Exception as e:
            self.root.after(0, lambda: self.add_message("error", f"An error occurred: {str(e)}", "error"))
            
    def _should_use_ai(self, message: str):
        """
        Checks if AI should be used.

        Args:
            message (str): The message to check.

        Returns:
            bool: True if AI should be used, False otherwise.
        """
        ai_keywords = ['analyze', 'explain', 'suggest', 'recommend', 'why', 'how', 'what', 'วิเคราะห์', 'อธิบาย', 'แนะนำ', 'ทำไม', 'อย่างไร', 'อะไร']
        return any(keyword in message.lower() for keyword in ai_keywords)
        
    def _process_with_ai(self, message: str):
        """
        Processes a message with AI.

        Args:
            message (str): The message to process.
        """
        try:
            # Get file system data first
            fs_data = self._get_filesystem_data()
            
            # Send to Ollama
            ai_response = self._ask_ollama(message, fs_data)
            
            self.root.after(0, lambda: self.add_message("ai", ai_response, "ai"))
            
        except Exception as e:
            # Fallback to File System
            self.root.after(0, lambda: self.add_system_message("⚠️ AI not available. Using File System instead."))
            self._process_with_filesystem(message)
            
    def _process_with_filesystem(self, message: str):
        """
        Processes a message with the File System.

        Args:
            message (str): The message to process.
        """
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
                    self.root.after(0, lambda: self.add_message("error", result_data.get('error', 'Could not process'), "error"))
            except json.JSONDecodeError:
                self.root.after(0, lambda: self.add_message("result", result, "result"))
                
        except Exception as e:
            self.root.after(0, lambda: self.add_message("error", f"An error occurred: {str(e)}", "error"))
            
    def _get_filesystem_data(self):
        """
        Gets file system data for AI.

        Returns:
            str: The file system data.
        """
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
        """
        Asks Ollama a question.

        Args:
            message (str): The question to ask.
            fs_data: The file system data.

        Returns:
            str: The response from Ollama.
        """
        try:
            # Create a clear prompt with context
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
                ai_response = response.json().get('response', 'Could not process')
                
                # Check if the AI gave a generic response
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
        """
        Generates a fallback response when the AI doesn't understand.

        Args:
            message (str): The user's message.
            fs_data: The file system data.

        Returns:
            str: The fallback response.
        """
        try:
            # Parse file system data
            if isinstance(fs_data, str):
                # Try to parse JSON from string
                import re
                json_match = re.search(r'\{.*\}', fs_data, re.DOTALL)
                if json_match:
                    fs_data = json.loads(json_match.group())
                else:
                    return f"Could not analyze data: {fs_data}"
            
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
            return f"An error occurred while analyzing: {str(e)}"
            
    def _generate_summary_response(self, fs_data):
        """
        Generates a response for a summary request.

        Args:
            fs_data: The file system data.

        Returns:
            str: The summary response.
        """
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
                
                response = f"""📊 File System Summary:

📁 General Information:
• Total files: {total_files:,}
• Total size: {total_size_mb:.2f} MB ({summary.get('total_size', 0):,} bytes)
• Average size: {average_size:,.0f} bytes

📋 File Type Distribution:"""
                
                # Show top file types
                if file_types:
                    sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
                    for ext, count in sorted_types[:8]:
                        percentage = (count / total_files * 100) if total_files > 0 else 0
                        response += f"\n• {ext}: {count:,} files ({percentage:.1f}%)"
                
                # Show largest files
                largest_files = summary.get('largest_files', [])
                if largest_files:
                    response += f"\n\n🔝 Largest Files:"
                    for i, file_info in enumerate(largest_files[:3], 1):
                        size_mb = file_info.get('file_size', 0) / (1024 * 1024)
                        response += f"\n{i}. {file_info.get('file_name', 'Unknown')} ({size_mb:.2f} MB)"
                
                # Analysis and recommendations
                response += f"\n\n💡 Analysis:"
                if total_files < 50:
                    response += f"\n• The system has a small number of files ({total_files}) - suitable for small projects."
                elif total_files < 500:
                    response += f"\n• The system has a moderate number of files ({total_files}) - should be organized periodically."
                else:
                    response += f"\n• The system has a large number of files ({total_files}) - should be organized urgently."
                
                if total_size_mb < 100:
                    response += f"\n• Low disk space usage ({total_size_mb:.2f} MB) - storage efficient."
                elif total_size_mb < 1000:
                    response += f"\n• Moderate disk space usage ({total_size_mb:.2f} MB) - should check large files."
                else:
                    response += f"\n• High disk space usage ({total_size_mb:.2f} MB) - should find ways to reduce size."
                
                if len(file_types) < 10:
                    response += f"\n• Few file types ({len(file_types)}) - simple structure."
                else:
                    response += f"\n• Diverse file types ({len(file_types)}) - should be grouped."
                
                return response
            else:
                return "Could not retrieve summary data."
        except Exception as e:
            return f"An error occurred while generating the summary: {str(e)}"
            
    def _generate_large_files_response(self, fs_data):
        """
        Generates a response for a large files request.

        Args:
            fs_data: The file system data.

        Returns:
            str: The large files response.
        """
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
                    response = "🔍 Largest files in the system:\n\n"
                    for i, file_info in enumerate(files, 1):
                        size_mb = file_info.get('file_size', 0) / (1024 * 1024)
                        response += f"{i}. 📄 {file_info.get('file_name', 'Unknown')}\n"
                        response += f"   📁 Path: {file_info.get('file_path', 'Unknown')}\n"
                        response += f"   💾 Size: {size_mb:.2f} MB ({file_info.get('file_size', 0):,} bytes)\n\n"
                    
                    response += "💡 Observations:\n"
                    response += f"• Largest file: {files[0].get('file_name', 'Unknown')} ({files[0].get('file_size', 0) / (1024*1024):.2f} MB)\n"
                    response += f"• Smallest file in the list: {files[-1].get('file_name', 'Unknown')} ({files[-1].get('file_size', 0) / (1024*1024):.2f} MB)\n"
                    
                    return response
                else:
                    return "No files found in the system."
            else:
                return "Could not retrieve large file data."
        except Exception as e:
            return f"An error occurred while analyzing large files: {str(e)}"
            
    def _generate_duplicate_response(self, fs_data):
        """
        Generates a response for a duplicates request.

        Args:
            fs_data: The file system data.

        Returns:
            str: The duplicates response.
        """
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
                response = "🔄 Duplicate files found:\n\n"
                
                for i, dup in enumerate(duplicates[:3], 1):
                    response += f"{i}. 🔗 Hash: {dup.get('hash_md5', 'Unknown')[:8]}...\n"
                    response += f"   📊 File count: {dup.get('count', 0)}\n"
                    response += f"   💾 Total size: {dup.get('total_size', 0) / (1024*1024):.2f} MB\n"
                    response += f"   ⚠️ Wasted space: {dup.get('wasted_space', 0) / (1024*1024):.2f} MB\n\n"
                    
                    for file_info in dup.get('files', [])[:2]:
                        response += f"      📄 {file_info.get('file_name', 'Unknown')}\n"
                    response += "\n"
                    
                return response
            else:
                return "✅ No duplicate files found in the system."
        except Exception as e:
            return f"An error occurred while searching for duplicate files: {str(e)}"
            
    def _generate_analysis_response(self, fs_data):
        """
        Generates a response for an analysis request.

        Args:
            fs_data: The file system data.

        Returns:
            str: The analysis response.
        """
        try:
            if isinstance(fs_data, dict) and 'summary' in fs_data:
                summary = fs_data['summary']
                total_files = summary.get('total_files', 0)
                total_size_mb = summary.get('total_size_mb', 0)
                file_types = summary.get('file_types', {})
                
                response = "🧠 File Structure Analysis:\n\n"
                
                # File type analysis
                response += "📋 File Type Distribution:\n"
                for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                    percentage = (count / total_files * 100) if total_files > 0 else 0
                    response += f"   • {ext}: {count} files ({percentage:.1f}%)\n"
                
                response += f"\n📊 General Statistics:\n"
                response += f"   • Total files: {total_files:,}\n"
                response += f"   • Total size: {total_size_mb:.2f} MB\n"
                response += f"   • Average size: {summary.get('average_size', 0):,.0f} bytes\n"
                
                # Recommendations
                response += f"\n💡 Recommendations:\n"
                if total_files > 100:
                    response += "   • The system has a large number of files and should be organized.\n"
                if total_size_mb > 1000:
                    response += "   • High disk space usage. Unnecessary files should be checked.\n"
                if len(file_types) > 20:
                    response += "   • Diverse file types. Should be grouped.\n"
                    
                return response
            else:
                return "Could not analyze the structure."
        except Exception as e:
            return f"An error occurred during analysis: {str(e)}"
            
    def _generate_general_response(self, fs_data, message):
        """
        Generates a general response.

        Args:
            fs_data: The file system data.
            message (str): The user's message.

        Returns:
            str: The general response.
        """
        try:
            if isinstance(fs_data, dict) and 'summary' in fs_data:
                summary = fs_data['summary']
                return f"""🤖 Response for: "{message}"

📊 Current Data:
• Total files: {summary.get('total_files', 'N/A')}
• Total size: {summary.get('total_size_mb', 'N/A')} MB
• File types: {len(summary.get('file_types', {}))}

💡 Use the following commands for more information:
• "give me summary"
• "show me large files"
• "find duplicate files"
• "analyze structure"
"""
            else:
                return f"Could not process the question '{message}'. Please try another command."
        except Exception as e:
            return f"An error occurred: {str(e)}"
            
    def _format_file_types(self, file_types):
        """
        Formats the file types.

        Args:
            file_types: The file types to format.

        Returns:
            str: The formatted file types.
        """
        if not file_types:
            return "No data found"
            
        formatted = []
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]:
            formatted.append(f"   • {ext}: {count} files")
        return "\n".join(formatted)
        
    def _format_largest_files(self, largest_files):
        """
        Formats the largest files.

        Args:
            largest_files: The largest files to format.

        Returns:
            str: The formatted largest files.
        """
        if not largest_files:
            return "No data found"
            
        formatted = []
        for i, file_info in enumerate(largest_files[:3], 1):
            size_mb = file_info.get('file_size', 0) / (1024 * 1024)
            formatted.append(f"   {i}. {file_info.get('file_name', 'Unknown')} ({size_mb:.2f} MB)")
        return "\n".join(formatted)
        
    def quick_query(self, query):
        """
        Performs a quick query.

        Args:
            query (str): The query to perform.
        """
        if not self.current_session_id:
            self.add_system_message("⚠️ Please scan a folder before use.")
            return
            
        self.add_message("user", query, "user")
        
        # Process in thread
        thread = threading.Thread(target=self._process_message, args=(query,))
        thread.daemon = True
        thread.start()
        
    def search_files(self):
        """Searches for files."""
        search_term = self.search_entry.get().strip()
        if not search_term:
            return
            
        if not self.current_session_id:
            self.add_system_message("⚠️ Please scan a folder before use.")
            return
            
        self.add_message("user", f"search: {search_term}", "user")
        
        # Process in thread
        thread = threading.Thread(target=self._process_message, args=(f"find files containing {search_term}",))
        thread.daemon = True
        thread.start()
        
    def analyze_structure(self):
        """Analyzes the structure."""
        if not self.current_session_id:
            self.add_system_message("⚠️ Please scan a folder before use.")
            return
            
        self.add_message("user", "analyze the file structure and explain what this project is about", "user")
        
        thread = threading.Thread(target=self._process_message, args=("analyze the file structure and explain what this project is about",))
        thread.daemon = True
        thread.start()
        
    def generate_report(self):
        """Generates a report."""
        if not self.current_session_id:
            self.add_system_message("⚠️ Please scan a folder before use.")
            return
            
        self.add_message("user", "generate a comprehensive report about this file system", "user")
        
        thread = threading.Thread(target=self._process_message, args=("generate a comprehensive report about this file system",))
        thread.daemon = True
        thread.start()
        
    def get_suggestions(self):
        """Gets suggestions."""
        if not self.current_session_id:
            self.add_system_message("⚠️ Please scan a folder before use.")
            return
            
        self.add_message("user", "what suggestions do you have for improving this file organization", "user")
        
        thread = threading.Thread(target=self._process_message, args=("what suggestions do you have for improving this file organization",))
        thread.daemon = True
        thread.start()
        
    def smart_search(self):
        """Performs a smart search."""
        if not self.current_session_id:
            self.add_system_message("⚠️ Please scan a folder before use.")
            return
            
        self.add_message("user", "perform a smart search to find important files and patterns", "user")
        
        thread = threading.Thread(target=self._process_message, args=("perform a smart search to find important files and patterns",))
        thread.daemon = True
        thread.start()
        
    def update_system_info(self):
        """Updates the system information."""
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
        """
        Formats the result.

        Args:
            data: The data to format.

        Returns:
            str: The formatted result.
        """
        if isinstance(data, list):
            if not data:
                return "No data found"
            
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
        """
        Formats data as a table.

        Args:
            data: The data to format.

        Returns:
            str: The formatted table.
        """
        if not data:
            return "No data found"
            
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
        """Shows the help message."""
        help_text = """
📋 Available Commands:

🔍 Natural Language Queries:
• "show me large files"
• "find duplicate files"
• "give me summary"
• "show files with extension .py"

🤖 AI Assistant (if Ollama is connected):
• "analyze this project"
• "explain the structure"
• "suggest improvements"

💾 SQL Queries:
• "SELECT * FROM files WHERE file_size > 1000000"

🔧 Special Commands:
• /help - Show this help message
• /scan - Scan information

💡 Tips:
• Use natural language for searching.
• The AI will help analyze and provide recommendations.
• Right-click to copy text.
        """
        self.add_system_message(help_text)

def main():
    """Main function."""
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
        
        print("🚀 Unified Chat App is ready!")
        print("✅ The system will automatically connect to the File System and Ollama.")
        print("�� The GUI window should be visible.")
        
        root.mainloop()
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
