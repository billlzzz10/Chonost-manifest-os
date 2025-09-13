"""A file system analyzer that scans directories and stores metadata in a database."""
import sqlite3
import os
import hashlib
import json
import mimetypes
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import magic
from contextlib import contextmanager
import argparse

# For LangChain integration (if used)
try:
    from langchain.tools import BaseTool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Fallback class if langchain is not available
    class BaseTool:
        """Fallback class for BaseTool if LangChain is not available."""
        def __init__(self):
            pass

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileSystemDatabase:
    """
    Handles the database operations for the file system analyzer.

    Attributes:
        db_path (str): The path to the SQLite database file.
    """
    def __init__(self, db_path: str = "file_system_analysis.db"):
        """
        Initializes the FileSystemDatabase.

        Args:
            db_path (str, optional): The path to the database file.
                Defaults to "file_system_analysis.db".
        """
        self.db_path = db_path
        self.init_database()

    @contextmanager
    def get_connection(self):
        """
        Provides a database connection using a context manager.

        Yields:
            sqlite3.Connection: The database connection.
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            yield conn
        finally:
            if conn:
                conn.close()

    def init_database(self):
        """Initializes the database by creating tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_sessions (
                session_id TEXT PRIMARY KEY, root_path TEXT NOT NULL, scan_start_time DATETIME NOT NULL,
                scan_end_time DATETIME, total_files INTEGER, total_directories INTEGER, total_size INTEGER,
                scan_config TEXT, scan_status TEXT DEFAULT 'running', scan_errors TEXT
            )
            ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, file_path TEXT NOT NULL,
                file_name TEXT NOT NULL, parent_directory TEXT, depth_level INTEGER, file_size INTEGER,
                file_extension TEXT, mime_type TEXT, encoding TEXT, created_date DATETIME, modified_date DATETIME,
                accessed_date DATETIME, permissions TEXT, owner_user TEXT, owner_group TEXT, hash_md5 TEXT,
                hash_sha256 TEXT, is_hidden BOOLEAN, is_system BOOLEAN, is_symlink BOOLEAN, symlink_target TEXT,
                inode_number INTEGER, hard_link_count INTEGER, specific_metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES scan_sessions(session_id)
            )
            ''')
            cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_files_path_session ON files(session_id, file_path)')
            conn.commit()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """
        Executes a SQL query.

        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): The parameters for the query. Defaults to ().

        Returns:
            List[tuple]: The result of the query.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_many(self, query: str, data: List[tuple]):
        """
        Executes a SQL query for multiple sets of parameters.

        Args:
            query (str): The SQL query to execute.
            data (List[tuple]): A list of parameter tuples.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, data)
            conn.commit()

class FileSystemAnalyzer:
    """
    Analyzes a directory and stores file metadata in a database.

    Attributes:
        db (FileSystemDatabase): The database handler.
        max_workers (int): The maximum number of worker threads for scanning.
        scan_errors (List[Dict]): A list of errors encountered during a scan.
    """
    def __init__(self, db: FileSystemDatabase, max_workers: int = os.cpu_count() or 1):
        """
        Initializes the FileSystemAnalyzer.

        Args:
            db (FileSystemDatabase): The database handler.
            max_workers (int, optional): The maximum number of worker threads.
                Defaults to the number of CPU cores.
        """
        self.db = db
        self.max_workers = max_workers
        self.scan_errors = []

    def analyze_directory(self, root_path: str, session_id: Optional[str] = None, config: Optional[Dict] = None) -> str:
        """
        Analyzes a directory and stores the file metadata in the database.

        Args:
            root_path (str): The path to the directory to analyze.
            session_id (Optional[str], optional): The session ID for the scan.
                If not provided, a new one is generated. Defaults to None.
            config (Optional[Dict], optional): The configuration for the scan.
                Defaults to None.

        Returns:
            str: A message indicating the completion of the scan and the session ID.
        """
        session_id = session_id or f"scan_{int(time.time())}"
        config = config or {
            "max_depth": 50, "include_hidden": True, "calculate_hashes": True,
            "hash_size_limit_mb": 100
        }
        scan_start = datetime.now()
        logging.info(f"Starting scan for session '{session_id}' on path '{root_path}'")
        try:
            self._create_scan_session(session_id, root_path, scan_start, config)
            self._scan_filesystem(root_path, session_id, config)
            self._update_scan_completion(session_id, datetime.now())
            logging.info(f"Scan completed for session '{session_id}'.")
            return f"Scan completed. Session ID: {session_id}"
        except Exception as e:
            logging.error(f"Scan failed for session '{session_id}': {e}", exc_info=True)
            self._update_scan_error(session_id, str(e))
            raise

    def _create_scan_session(self, session_id: str, root_path: str, start_time: datetime, config: Dict):
        """
        Creates a new scan session in the database.

        Args:
            session_id (str): The session ID.
            root_path (str): The root path of the scan.
            start_time (datetime): The start time of the scan.
            config (Dict): The configuration for the scan.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = "INSERT INTO scan_sessions (session_id, root_path, scan_start_time, scan_config, scan_status) VALUES (?, ?, ?, ?, 'running')"
            cursor.execute(query, (session_id, root_path, start_time, json.dumps(config)))
            conn.commit()

    def _update_scan_completion(self, session_id: str, end_time: datetime):
        """
        Updates a scan session to mark it as completed.

        Args:
            session_id (str): The session ID.
            end_time (datetime): The end time of the scan.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            errors_json = json.dumps(self.scan_errors) if self.scan_errors else None
            query = "UPDATE scan_sessions SET scan_end_time = ?, scan_status = 'completed', scan_errors = ? WHERE session_id = ?"
            cursor.execute(query, (end_time, errors_json, session_id))
            conn.commit()

    def _update_scan_error(self, session_id: str, error_msg: str):
        """
        Updates a scan session to mark it as failed.

        Args:
            session_id (str): The session ID.
            error_msg (str): The error message.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = "UPDATE scan_sessions SET scan_status = 'failed', scan_errors = ? WHERE session_id = ?"
            cursor.execute(query, (error_msg, session_id))
            conn.commit()

    def _scan_filesystem(self, root_path: str, session_id: str, config: Dict):
        """
        Scans the file system and collects file metadata.

        Args:
            root_path (str): The root path to scan.
            session_id (str): The session ID for the scan.
            config (Dict): The configuration for the scan.
        """
        files_to_process = []
        logging.info("Walking directory tree to collect paths...")
        for root, dirs, files in os.walk(root_path, topdown=True):
            if not config.get("include_hidden", True):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]
            depth = root.replace(root_path, '').count(os.sep)
            if depth > config.get("max_depth", 50):
                del dirs[:]; continue
            for file in files:
                file_path = os.path.join(root, file)
                files_to_process.append((file_path, session_id, depth + 1, config))
        
        logging.info(f"Found {len(files_to_process)} files. Starting metadata extraction with {self.max_workers} workers.")
        files_data = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(self._get_file_metadata, *params): params for params in files_to_process}
            for i, future in enumerate(as_completed(future_to_file)):
                file_path = future_to_file[future][0]
                try:
                    if metadata := future.result(): files_data.append(metadata)
                except Exception as exc:
                    self.scan_errors.append({'path': file_path, 'error': str(exc)})
                if (i + 1) % 1000 == 0: logging.info(f"Processed {i+1}/{len(files_to_process)} files...")
        
        logging.info("Batch inserting file data into database...")
        if files_data:
            columns = files_data[0].keys()
            query = f"INSERT OR IGNORE INTO files ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(columns))})"
            data_tuples = [tuple(d.values()) for d in files_data]
            self.db.execute_many(query, data_tuples)

    def _get_file_metadata(self, file_path: str, session_id: str, depth: int, config: Dict) -> Optional[Dict]:
        """
        Gets the metadata for a single file.

        Args:
            file_path (str): The path to the file.
            session_id (str): The session ID for the scan.
            depth (int): The depth of the file in the directory tree.
            config (Dict): The configuration for the scan.

        Returns:
            Optional[Dict]: A dictionary of file metadata, or None if the file cannot be processed.
        """
        try:
            stat = os.lstat(file_path)
            path_obj = Path(file_path)
            metadata = {
                'session_id': session_id, 
                'file_path': file_path, 
                'file_name': path_obj.name, 
                'parent_directory': str(path_obj.parent), 
                'depth_level': depth, 
                'file_size': stat.st_size, 
                'file_extension': path_obj.suffix.lower(), 
                'created_date': datetime.fromtimestamp(stat.st_ctime), 
                'modified_date': datetime.fromtimestamp(stat.st_mtime), 
                'accessed_date': datetime.fromtimestamp(stat.st_atime), 
                'permissions': oct(stat.st_mode)[-3:], 
                'is_hidden': path_obj.name.startswith('.'), 
                'is_symlink': path_obj.is_symlink(), 
                'symlink_target': os.readlink(file_path) if path_obj.is_symlink() else None, 
                'inode_number': stat.st_ino, 
                'hard_link_count': stat.st_nlink, 
                'owner_user': None, 
                'owner_group': None, 
                'is_system': False, 
                'mime_type': None, 
                'encoding': None, 
                'hash_md5': None, 
                'hash_sha256': None, 
                'specific_metadata': None
            }
            
            # Try to get owner info (may fail on Windows)
            try: 
                metadata.update({'owner_user': path_obj.owner(), 'owner_group': path_obj.group()})
            except (ImportError, KeyError, OSError, NotImplementedError): 
                pass # Windows doesn't have pwd/grp or owner() not supported
            
            # Get MIME type
            try:
                metadata['mime_type'] = magic.from_file(file_path, mime=True)
            except Exception:
                metadata['mime_type'] = 'application/octet-stream'
            
            # Calculate hashes if enabled and file size is within limit
            hash_limit = config.get("hash_size_limit_mb", 100) * 1024 * 1024
            if config.get("calculate_hashes", True) and 0 < stat.st_size < hash_limit:
                try:
                    with open(file_path, 'rb') as f: 
                        content = f.read()
                        metadata['hash_md5'] = hashlib.md5(content).hexdigest()
                        metadata['hash_sha256'] = hashlib.sha256(content).hexdigest()
                except Exception:
                    pass  # Skip hash calculation if file can't be read
            
            # Get specific metadata (e.g., image EXIF)
            try:
                if specific_meta := self._get_specific_metadata(file_path, metadata['mime_type']): 
                    metadata['specific_metadata'] = json.dumps(specific_meta)
            except Exception:
                pass  # Skip specific metadata if it fails
            
            return metadata
        except (FileNotFoundError, PermissionError) as e:
            logging.warning(f"Skipping file {file_path}: {e}")
            return None

    def _get_specific_metadata(self, file_path: str, mime_type: Optional[str]) -> Optional[Dict]:
        """
        Gets specific metadata for a file based on its MIME type.

        Args:
            file_path (str): The path to the file.
            mime_type (Optional[str]): The MIME type of the file.

        Returns:
            Optional[Dict]: A dictionary of specific metadata, or None if not applicable.
        """
        if mime_type and mime_type.startswith('image/') and PIL_AVAILABLE:
            try:
                with Image.open(file_path) as img:
                    exif_data = {}
                    if hasattr(img, '_getexif') and img._getexif():
                        exif_data = {TAGS.get(tag, tag): str(value) if isinstance(value, bytes) else value 
                                   for tag, value in img._getexif().items()}
                    return {'format': img.format, 'mode': img.mode, 'size': f"{img.width}x{img.height}", 'exif': exif_data}
            except Exception: 
                return None
        return None

class SQLDirectAccess:
    """Provides direct SQL access to the file system database."""
    def __init__(self, db: FileSystemDatabase):
        """
        Initializes the SQLDirectAccess class.

        Args:
            db (FileSystemDatabase): The database handler.
        """
        self.db = db
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """
        Executes a SQL query.

        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): The parameters for the query. Defaults to ().

        Returns:
            List[tuple]: The result of the query.
        """
        return self.db.execute_query(query, params)

class FileSystemQueries:
    """Provides high-level queries for the file system data."""
    def __init__(self, db: FileSystemDatabase):
        """
        Initializes the FileSystemQueries class.

        Args:
            db (FileSystemDatabase): The database handler.
        """
        self.db = db
    def get_largest_files(self, session_id: str, limit: int = 10) -> List[Dict]:
        """
        Gets the largest files in a scan session.

        Args:
            session_id (str): The session ID of the scan.
            limit (int, optional): The maximum number of files to return. Defaults to 10.

        Returns:
            List[Dict]: A list of the largest files.
        """
        rows = self.db.execute_query("SELECT file_name, file_path, file_size FROM files WHERE session_id = ? ORDER BY file_size DESC LIMIT ?", (session_id, limit))
        return [{'name': r[0], 'path': r[1], 'size': r[2]} for r in rows]
    def find_files_by_extension(self, session_id: str, extension: str) -> List[Dict]:
        """
        Finds files by their extension.

        Args:
            session_id (str): The session ID of the scan.
            extension (str): The file extension to search for.

        Returns:
            List[Dict]: A list of files with the specified extension.
        """
        rows = self.db.execute_query("SELECT file_name, file_path, file_size FROM files WHERE session_id = ? AND file_extension = ? ORDER BY file_size DESC", (session_id, extension))
        return [{'name': r[0], 'path': r[1], 'size': r[2]} for r in rows]
    def get_duplicate_files(self, session_id: str) -> List[Dict]:
        """
        Gets duplicate files based on their hash.

        Args:
            session_id (str): The session ID of the scan.

        Returns:
            List[Dict]: A list of duplicate files.
        """
        rows = self.db.execute_query("SELECT hash_md5, COUNT(*), GROUP_CONCAT(file_path, CHAR(10)) as paths, SUM(file_size) - MIN(file_size) as wasted_space FROM files WHERE session_id = ? AND hash_md5 IS NOT NULL GROUP BY hash_md5 HAVING COUNT(*) > 1 ORDER BY wasted_space DESC", (session_id,))
        return [{'hash': r[0], 'count': r[1], 'paths': r[2].split('\n'), 'wasted_space': r[3]} for r in rows]
    def get_directory_summary(self, session_id: str) -> Dict:
        """
        Gets a summary of the directory scan.

        Args:
            session_id (str): The session ID of the scan.

        Returns:
            Dict: A dictionary containing the directory summary.
        """
        result = self.db.execute_query("SELECT COUNT(*), SUM(file_size), AVG(file_size) FROM files WHERE session_id = ?", (session_id,))[0]
        return {'file_count': result[0] or 0, 'total_size': result[1] or 0, 'average_size': result[2] or 0}

class NaturalLanguageQuery:
    """Processes natural language queries for file system data."""
    def __init__(self, queries: FileSystemQueries):
        """
        Initializes the NaturalLanguageQuery class.

        Args:
            queries (FileSystemQueries): The file system queries handler.
        """
        self.queries = queries
        self.command_mapping = { 
            'large files': self.queries.get_largest_files, 
            'duplicate files': self.queries.get_duplicate_files, 
            'summary': self.queries.get_directory_summary 
        }
    def process_request(self, user_request: str, session_id: str) -> Dict:
        """
        Processes a natural language request.

        Args:
            user_request (str): The natural language request from the user.
            session_id (str): The session ID of the scan.

        Returns:
            Dict: A dictionary containing the result of the request.
        """
        request_lower = user_request.lower()
        for keyword, function in self.command_mapping.items():
            if keyword in request_lower:
                return {'success': True, 'data': function(session_id=session_id)}
        if 'extension' in request_lower:
            import re
            if match := re.search(r'\.(\w+)', request_lower):
                ext = '.' + match.group(1)
                return {'success': True, 'data': self.queries.find_files_by_extension(session_id, ext)}
        return {'success': False, 'error': 'Could not understand the request'}

class FileSystemMCPTool(BaseTool):
    """A tool for scanning, analyzing, and querying file system metadata."""
    name = "file_system_analyzer"
    description = "Tool to scan, analyze, and query file system metadata."
    db: FileSystemDatabase
    analyzer: FileSystemAnalyzer
    sql_access: SQLDirectAccess
    queries: FileSystemQueries
    nl_query: NaturalLanguageQuery

    def __init__(self):
        """Initializes the FileSystemMCPTool."""
        super().__init__()
        self.db = FileSystemDatabase()
        self.analyzer = FileSystemAnalyzer(self.db)
        self.sql_access = SQLDirectAccess(self.db)
        self.queries = FileSystemQueries(self.db)
        self.nl_query = NaturalLanguageQuery(self.queries)

    def _run(self, action_input: str) -> str:
        """
        Runs the tool with the given input.

        Args:
            action_input (str): A JSON string representing the action and its parameters.

        Returns:
            str: A JSON string representing the result of the action.
        """
        try:
            params = json.loads(action_input)
            action = params['action']
            if action == 'scan':
                return self.analyzer.analyze_directory(params['path'], params.get('session_id'), params.get('config'))
            
            session_id = params.get('session_id')
            if not session_id:
                return json.dumps({'success': False, 'error': 'session_id is required for query actions'})
                
            if action == 'query_sql':
                result = self.sql_access.execute_query(params['sql'], tuple(params.get('params', [])))
                return json.dumps(result, default=str)
            if action == 'query_function':
                func = getattr(self.queries, params['function'])
                args = params.get('args', [])
                result = func(session_id=session_id, *args)
                return json.dumps(result, default=str)
            if action == 'query_natural':
                return json.dumps(self.nl_query.process_request(params['request'], session_id), default=str)
            return f"Unknown action: {action}"
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
