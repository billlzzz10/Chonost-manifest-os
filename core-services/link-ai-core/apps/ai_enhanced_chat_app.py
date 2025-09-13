#!/usr/bin/env python3
"""
AI-Enhanced File System MCP Desktop Chat App.

A desktop chat application that integrates AI from Ollama for advanced
file system analysis and interaction.
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
    """
    An AI-enhanced desktop chat application for file system analysis.

    This class creates a Tkinter-based GUI application that allows users to
    scan their file system, ask questions in natural language, and get
    AI-powered analysis and recommendations.

    Attributes:
        root: The root Tkinter window.
        tool (FileSystemMCPTool): The file system analysis tool.
        ai_analyzer (FileSystemAIAnalyzer): The AI analyzer for file system data.
        current_session_id (str): The current scan session ID.
        scanning (bool): A flag indicating if a scan is in progress.
        chat_history (list): A list of chat messages.
        file_data (dict): Data about the scanned files for AI analysis.
    """
    def __init__(self, root):
        """
        Initializes the AIEnhancedChatApp.

        Args:
            root: The root Tkinter window.
        """
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
        self.add_system_message("🚀 Welcome to the AI-Enhanced File System MCP Chat!")
        self.add_system_message("💡 New features:\n• 🤖 AI file system analysis\n• 📊 Smart analysis\n• 💡 AI recommendations\n• 🎯 Advanced search")
        
        # Check AI connection
        if self.ai_analyzer.is_connected():
            self.add_system_message("✅ AI connected successfully! Ready to use.")
        else:
            self.add_system_message("⚠️ Could not connect to AI. Using normal mode.")
        
    def setup_styles(self):
        """Sets up the UI styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Main.TFrame', background='#1e1e1e')
        style.configure('Chat.TFrame', background='#2d2d2d')
        style.configure('Input.TFrame', background='#3c3c3c')
        
    def setup_ui(self):
        """Creates the main UI."""
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
        """
        Creates the title bar.

        Args:
            parent: The parent widget.
        """
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
        ai_status = "🟢 AI Ready" if self.ai_analyzer.is_connected() else "🔴 AI Not Ready"
        self.ai_status_label = tk.Label(status_frame,
                                       text=ai_status,
                                       font=('Segoe UI', 10),
                                       fg='#00ff00' if self.ai_analyzer.is_connected() else '#ff4444',
                                       bg='#1e1e1e')
        self.ai_status_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Session status
        self.session_label = tk.Label(status_frame,
                                     text="Session: None",
                                     font=('Segoe UI', 10),
                                     fg='#cccccc',
                                     bg='#1e1e1e')
        self.session_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Connection status
        self.status_label = tk.Label(status_frame,
                                    text="🟢 Ready",
                                    font=('Segoe UI', 10),
                                    fg='#00ff00',
                                    bg='#1e1e1e')
        self.status_label.pack(side=tk.LEFT)
        
    def setup_chat_tab(self):
        """Creates the chat tab."""
        chat_frame = ttk.Frame(self.notebook, style='Chat.TFrame')
        self.notebook.add(chat_frame, text="💬 Chat")
        
        # Chat area
        self.setup_chat_area(chat_frame)
        
        # Control panel
        self.setup_control_panel(chat_frame)
        
        # Input area
        self.setup_input_area(chat_frame)
        
    def setup_ai_analysis_tab(self):
        """Creates the AI analysis tab."""
        ai_frame = ttk.Frame(self.notebook, style='Chat.TFrame')
        self.notebook.add(ai_frame, text="🤖 AI Analysis")
        
        # AI controls
        controls_frame = ttk.Frame(ai_frame, style='Chat.TFrame')
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # AI analysis buttons
        ai_buttons = [
            ("📊 Analyze Structure", self.ai_analyze_structure),
            ("📋 Generate Report", self.ai_generate_report),
            ("💡 Get Suggestions", self.ai_get_suggestions),
            ("🔍 Advanced Analysis", self.ai_advanced_analysis)
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
        """
        Creates the chat area.

        Args:
            parent: The parent widget.
        """
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
        """
        Creates the control panel.

        Args:
            parent: The parent widget.
        """
        control_frame = ttk.Frame(parent, style='Input.TFrame')
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Scan button
        self.scan_btn = tk.Button(control_frame,
                                 text="📁 Scan Folder",
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
                          text="🤖 AI Analysis",
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
                             text="🗑️ Clear Chat",
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
                              text="📤 Export",
                              command=self.export_results,
                              bg='#ffc107',
                              fg='black',
                              font=('Segoe UI', 10),
                              relief=tk.FLAT,
                              padx=15,
                              pady=5)
        export_btn.pack(side=tk.LEFT)
        
    def setup_input_area(self, parent):
        """
        Creates the input area.

        Args:
            parent: The parent widget.
        """
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
                            text="Send",
                            command=self.send_message,
                            bg='#007acc',
                            fg='white',
                            font=('Segoe UI', 10, 'bold'),
                            relief=tk.FLAT,
                            padx=20)
        send_btn.pack(side=tk.RIGHT)
        
    def add_message(self, sender, message, message_type="normal"):
        """
        Adds a message to the chat display.

        Args:
            sender (str): The sender of the message (e.g., "user", "ai", "system").
            message (str): The content of the message.
            message_type (str, optional): The type of message, used for styling.
                                           Defaults to "normal".
        """
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
            formatted_message = f"[{timestamp}] 👤 You: {message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("user", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("user", foreground="#007acc")
        elif message_type == "result":
            formatted_message = f"[{timestamp}] 📊 Result:\n{message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("result", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("result", foreground="#ffaa00")
        elif message_type == "ai":
            formatted_message = f"[{timestamp}] 🤖 AI:\n{message}\n\n"
            self.chat_display.insert(tk.END, formatted_message)
            self.chat_display.tag_add("ai", f"end-{len(formatted_message)+1}c", "end-1c")
            self.chat_display.tag_config("ai", foreground="#28a745")
        elif message_type == "error":
            formatted_message = f"[{timestamp}] ❌ Error: {message}\n\n"
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
        """
        Adds a system message to the chat.

        Args:
            message (str): The system message.
        """
        self.add_message("system", message, "system")
        
    def scan_folder(self):
        """Handles the 'Scan Folder' button click event."""
        if self.scanning:
            messagebox.showwarning("Scanning", "Please wait for the current scan to finish.")
            return
            
        folder_path = filedialog.askdirectory(title="Select a folder to scan")
        if not folder_path:
            return
            
        self.scanning = True
        self.status_label.config(text="🟡 Scanning...", fg='#ffaa00')
        self.scan_btn.config(state=tk.DISABLED)
        
        # Run scan in separate thread
        thread = threading.Thread(target=self._perform_scan, args=(folder_path,))
        thread.daemon = True
        thread.start()
        
    def _perform_scan(self, folder_path):
        """
        Performs the folder scan in a background thread.

        Args:
            folder_path (str): The path to the folder to scan.
        """
        try:
            self.add_system_message(f"🔍 Starting to scan folder: {folder_path}")
            
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
                self.add_system_message(f"✅ Scan complete! Session ID: {self.current_session_id}")
                self.session_label.config(text=f"Session: {self.current_session_id[:8]}...")
                
                # Collect file data for AI analysis
                self._collect_file_data()
                
            else:
                self.add_system_message(f"❌ Scan failed: {result}")
                
        except Exception as e:
            self.add_system_message(f"❌ An error occurred: {str(e)}")
        finally:
            self.scanning = False
            self.status_label.config(text="🟢 Ready", fg='#00ff00')
            self.scan_btn.config(state=tk.NORMAL)
            
    def _collect_file_data(self):
        """Collects file data for AI analysis after a scan."""
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
            
            self.add_system_message("📊 File data is ready for AI analysis")
            
        except Exception as e:
            self.add_system_message(f"⚠️ Could not collect file data: {str(e)}")
            
    def send_message(self, event=None):
        """Handles the send message event."""
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
        """
        Processes the user's message in a background thread.

        Args:
            message (str): The user's message.
        """
        try:
            if not self.current_session_id:
                self.add_system_message("⚠️ Please scan a folder before use.")
                return
                
            # Check for special commands
            if message.lower().startswith("/help"):
                self._show_help()
                return
            elif message.lower().startswith("/scan"):
                self.add_system_message("Use the 'Scan Folder' button to scan a new folder.")
                return
            elif message.lower().startswith("/ai"):
                self._process_ai_query(message[3:].strip())
                return
            elif message.lower().startswith("/clear"):
                self.clear_chat()
                return
                
            # Check if it's an AI query
            if self.ai_analyzer.is_connected() and any(keyword in message.lower() for keyword in 
                ['analyze', 'explain', 'suggest', 'report', 'structure', 'issue', 'improve']):
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
                    self.add_message("error", result_data.get('error', 'Could not process'), "error")
            except json.JSONDecodeError:
                self.add_message("result", result, "result")
                
        except Exception as e:
            self.add_message("error", f"An error occurred: {str(e)}", "error")
            
    def _process_ai_query(self, query):
        """
        Processes an AI query.

        Args:
            query (str): The AI query.
        """
        if not self.ai_analyzer.is_connected():
            self.add_message("error", "Could not connect to AI", "error")
            return
            
        if not self.file_data:
            self.add_message("error", "No file data for AI analysis", "error")
            return
            
        self.add_system_message("🤖 Processing with AI...")
        
        # Run AI analysis in separate thread
        thread = threading.Thread(target=self._run_ai_analysis, args=(query,))
        thread.daemon = True
        thread.start()
        
    def _run_ai_analysis(self, query):
        """
        Runs the AI analysis in a background thread.

        Args:
            query (str): The AI query.
        """
        try:
            result = self.ai_analyzer.analyze_with_ai(self.file_data, query)
            if result:
                self.add_message("ai", result, "ai")
            else:
                self.add_message("error", "Could not analyze with AI", "error")
        except Exception as e:
            self.add_message("error", f"An error occurred during AI analysis: {str(e)}", "error")
            
    def _format_result(self, data):
        """
        Formats the result for display.

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
        Formats a list of dictionaries as a string table.

        Args:
            data (list): The data to format.

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
        """Displays the help message."""
        help_text = """
📋 Available Commands:

🔍 Natural Language Queries:
• "show me large files"
• "find duplicate files"
• "give me summary"
• "show files with extension .py"

🤖 AI Commands:
• /ai analyze structure
• /ai generate report
• /ai get suggestions
• Use keywords like "analyze", "explain", "suggest" to trigger AI

🔧 Special Commands:
• /help - Show this help message
• /scan - Scan information
• /clear - Clear the chat

💡 Tips:
• Use natural language for searching.
• The AI will help analyze and provide recommendations.
• The system processes in real-time.
        """
        self.add_system_message(help_text)
        
    def clear_chat(self):
        """Clears the chat display and history."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the entire conversation?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.chat_history.clear()
            self.add_system_message("🗑️ Conversation cleared.")
            
    def export_results(self):
        """Exports the chat history to a text file."""
        if not self.current_session_id:
            messagebox.showwarning("No Data", "Please scan a folder before exporting results.")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Results"
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
                    
                messagebox.showinfo("Success", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export: {str(e)}")
                
    def quick_ai_analysis(self):
        """Performs a quick AI analysis."""
        if not self.ai_analyzer.is_connected():
            messagebox.showwarning("AI Not Ready", "Could not connect to AI.")
            return
            
        if not self.file_data:
            messagebox.showwarning("No Data", "Please scan a folder before using AI.")
            return
            
        # Run quick analysis
        thread = threading.Thread(target=self._quick_ai_analysis)
        thread.daemon = True
        thread.start()
        
    def _quick_ai_analysis(self):
        """
        Performs a quick AI analysis in a background thread.
        """
        try:
            self.add_system_message("🤖 Analyzing with AI...")
            
            # Get AI suggestions
            suggestions = self.ai_analyzer.get_suggestions(self.file_data)
            if suggestions:
                self.add_message("ai", f"💡 AI Suggestions:\n{suggestions}", "ai")
            
            # Get structure explanation
            structure = self.ai_analyzer.explain_structure(self.file_data)
            if structure:
                self.add_message("ai", f"📁 Structure Analysis:\n{structure}", "ai")
                
        except Exception as e:
            self.add_message("error", f"An error occurred during AI analysis: {str(e)}", "error")
            
    # AI Analysis tab methods
    def ai_analyze_structure(self):
        """Analyzes the structure with AI."""
        if not self._check_ai_ready():
            return
            
        thread = threading.Thread(target=self._ai_analyze_structure)
        thread.daemon = True
        thread.start()
        
    def _ai_analyze_structure(self):
        """
        Analyzes the structure with AI in a background thread.
        """
        try:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, "🤖 Analyzing structure...\n")
            self.ai_display.config(state=tk.DISABLED)
            
            result = self.ai_analyzer.explain_structure(self.file_data)
            if result:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, f"📁 Structure Analysis:\n\n{result}")
                self.ai_display.config(state=tk.DISABLED)
            else:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, "❌ Could not analyze")
                self.ai_display.config(state=tk.DISABLED)
                
        except Exception as e:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, f"❌ An error occurred: {str(e)}")
            self.ai_display.config(state=tk.DISABLED)
            
    def ai_generate_report(self):
        """Generates a report with AI."""
        if not self._check_ai_ready():
            return
            
        thread = threading.Thread(target=self._ai_generate_report)
        thread.daemon = True
        thread.start()
        
    def _ai_generate_report(self):
        """
        Generates a report with AI in a background thread.
        """
        try:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, "🤖 Generating report...\n")
            self.ai_display.config(state=tk.DISABLED)
            
            result = self.ai_analyzer.generate_report(self.file_data)
            if result:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, f"📋 Analysis Report:\n\n{result}")
                self.ai_display.config(state=tk.DISABLED)
            else:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, "❌ Could not generate report")
                self.ai_display.config(state=tk.DISABLED)
                
        except Exception as e:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, f"❌ An error occurred: {str(e)}")
            self.ai_display.config(state=tk.DISABLED)
            
    def ai_get_suggestions(self):
        """Gets suggestions from AI."""
        if not self._check_ai_ready():
            return
            
        thread = threading.Thread(target=self._ai_get_suggestions)
        thread.daemon = True
        thread.start()
        
    def _ai_get_suggestions(self):
        """
        Gets suggestions from AI in a background thread.
        """
        try:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, "🤖 Generating suggestions...\n")
            self.ai_display.config(state=tk.DISABLED)
            
            result = self.ai_analyzer.get_suggestions(self.file_data)
            if result:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, f"💡 AI Suggestions:\n\n{result}")
                self.ai_display.config(state=tk.DISABLED)
            else:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, "❌ Could not generate suggestions")
                self.ai_display.config(state=tk.DISABLED)
                
        except Exception as e:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, f"❌ An error occurred: {str(e)}")
            self.ai_display.config(state=tk.DISABLED)
            
    def ai_advanced_analysis(self):
        """Performs advanced analysis with AI."""
        if not self._check_ai_ready():
            return
            
        # Create custom query dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Advanced Analysis")
        dialog.geometry("500x300")
        dialog.configure(bg='#2d2d2d')
        
        tk.Label(dialog, text="Advanced Analysis",
                font=('Segoe UI', 14, 'bold'), fg='#ffffff', bg='#2d2d2d').pack(pady=10)
        
        tk.Label(dialog, text="Question or command:",
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
        
        tk.Button(dialog, text="Analyze", command=run_analysis,
                 bg='#007acc', fg='white', font=('Segoe UI', 10, 'bold'),
                 relief=tk.FLAT, padx=20, pady=5).pack()
        
    def _run_advanced_analysis(self, query):
        """
        Runs the advanced analysis in a background thread.

        Args:
            query (str): The advanced query.
        """
        try:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, f"🤖 Analyzing: {query}\n")
            self.ai_display.config(state=tk.DISABLED)
            
            result = self.ai_analyzer.analyze_with_ai(self.file_data, query)
            if result:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, f"🔍 Analysis Result:\n\n{result}")
                self.ai_display.config(state=tk.DISABLED)
            else:
                self.ai_display.config(state=tk.NORMAL)
                self.ai_display.delete(1.0, tk.END)
                self.ai_display.insert(1.0, "❌ Could not analyze")
                self.ai_display.config(state=tk.DISABLED)
                
        except Exception as e:
            self.ai_display.config(state=tk.NORMAL)
            self.ai_display.delete(1.0, tk.END)
            self.ai_display.insert(1.0, f"❌ An error occurred: {str(e)}")
            self.ai_display.config(state=tk.DISABLED)
            
    def _check_ai_ready(self):
        """Checks if the AI is ready for a query."""
        if not self.ai_analyzer.is_connected():
            messagebox.showwarning("AI Not Ready", "Could not connect to AI.")
            return False
            
        if not self.file_data:
            messagebox.showwarning("No Data", "Please scan a folder before using AI.")
            return False
            
        return True

def main():
    """Main function to run the application."""
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
>>>>>>> REPLACE
