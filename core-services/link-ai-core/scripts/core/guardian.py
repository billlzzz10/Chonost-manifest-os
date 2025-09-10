# scripts/guardian.py (v4.0 - Enhanced & Accurate)
import pathlib
import re
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()
ROADMAP_PATH = PROJECT_ROOT / "ROADMAP.md"

class TaskAnalyzer:
    """Analyzer for development roadmap tasks"""
    
    def __init__(self) -> None:
        self.tasks: List[Dict] = []
        self.phases: Dict[str, Dict] = {}
        self.current_phase = ""
        self.current_section = ""
        
    def parse_roadmap_content(self, content: str) -> None:
        """Parse roadmap content and extract tasks with proper structure"""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            line = line.strip()
            
            # Detect Phase headers (both formats)
            if line.startswith('## Phase') or line.startswith('## 🚀 PHASE'):
                self.current_phase = line
                self.phases[line] = {
                    'tasks': [],
                    'completed': 0,
                    'total': 0
                }
                continue
                
            # Detect section headers
            if line.startswith('### ') and not line.startswith('### Phase'):
                self.current_section = line
                continue
                
            # Detect subsection headers
            if line.startswith('#### '):
                self.current_section = line
                continue
                
            # Parse task lines with various formats
            task_info = self._parse_task_line(line)
            if task_info:
                task_info.update({
                    'phase': self.current_phase,
                    'section': self.current_section,
                    'line_number': line_num
                })
                self.tasks.append(task_info)
                
                # Update phase statistics
                if self.current_phase in self.phases:
                    self.phases[self.current_phase]['total'] += 1
                    if task_info['completed']:
                        self.phases[self.current_phase]['completed'] += 1
                    self.phases[self.current_phase]['tasks'].append(task_info)
    
    def _parse_task_line(self, line: str) -> Optional[Dict]:
        """Parse individual task line with multiple formats"""
        # Format 1: - [x] Task name [file: path]
        # Format 2: - [ ] Task name [file: path] 
        # Format 3: - [x] Task name
        # Format 4: - [ ] Task name
        
        # Updated regex patterns to match actual roadmap format
        patterns = [
            # Pattern for tasks with file references
            r'^\s*-\s*\[([x\sX])\]\s*(.*?)\s*\[file:\s*(.*?)\]\s*$',
            # Pattern for regular tasks (with or without [x] or [ ])
            r'^\s*-\s*\[([x\sX])\]\s*(.*?)$',
            # Additional patterns for edge cases
            r'^\s*-\s*\[([x\sX])\]\s+(.*?)(?:\s*\[file:\s*(.*?)\])?\s*$',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                status = groups[0] if groups[0] else ' '
                task_name = groups[1] if len(groups) > 1 and groups[1] else ''
                file_path = groups[2] if len(groups) > 2 and groups[2] else ''
                
                # Clean up the extracted data
                task_name = task_name.strip()
                file_path = file_path.strip() if file_path else ''
                
                # Skip empty task names
                if not task_name:
                    continue
                    
                return {
                    'completed': status.lower() == 'x',
                    'task_name': task_name,
                    'file_path': file_path,
                    'raw_line': line
                }
        
        return None
    
    def verify_file_existence(self) -> Dict[str, List[Dict]]:
        """Verify if files mentioned in tasks actually exist"""
        verification_results: Dict[str, List[Dict]] = {
            'existing_files': [],
            'missing_files': [],
            'no_file_specified': []
        }
        
        for task in self.tasks:
            if task['file_path']:
                file_path = PROJECT_ROOT / task['file_path']
                if file_path.exists():
                    verification_results['existing_files'].append(task)
                else:
                    verification_results['missing_files'].append(task)
            else:
                verification_results['no_file_specified'].append(task)
        
        return verification_results
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks if task['completed'])
        
        # Phase statistics
        phase_stats = {}
        for phase_name, phase_data in self.phases.items():
            if phase_data['total'] > 0:
                completion_rate = (phase_data['completed'] / phase_data['total']) * 100
                phase_stats[phase_name] = {
                    'completed': phase_data['completed'],
                    'total': phase_data['total'],
                    'completion_rate': completion_rate
                }
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'overall_completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'phase_statistics': phase_stats,
            'phases_count': len(self.phases)
        }
    
    def generate_detailed_report(self) -> str:
        """Generate detailed analysis report"""
        stats = self.get_statistics()
        verification = self.verify_file_existence()
        
        report = []
        report.append("🛡️  Blueprint Guardian Analysis Report (v4.0)")
        report.append("=" * 60)
        report.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"📁 Project Root: {PROJECT_ROOT}")
        report.append("")
        
        # Overall Statistics
        report.append("📊 OVERALL PROGRESS")
        report.append("-" * 30)
        report.append(f"Total Tasks: {stats['total_tasks']}")
        report.append(f"Completed: {stats['completed_tasks']}")
        report.append(f"Completion Rate: {stats['overall_completion_rate']:.2f}%")
        report.append("")
        
        # Phase Statistics
        report.append("📋 PHASE BREAKDOWN")
        report.append("-" * 30)
        for phase_name, phase_data in stats['phase_statistics'].items():
            report.append(f"{phase_name}:")
            report.append(f"  Completed: {phase_data['completed']}/{phase_data['total']}")
            report.append(f"  Rate: {phase_data['completion_rate']:.2f}%")
        report.append("")
        
        # File Verification
        report.append("📁 FILE VERIFICATION")
        report.append("-" * 30)
        report.append(f"Files with tasks: {len(verification['existing_files'])}")
        report.append(f"Missing files: {len(verification['missing_files'])}")
        report.append(f"Tasks without files: {len(verification['no_file_specified'])}")
        
        if verification['missing_files']:
            report.append("")
            report.append("⚠️  MISSING FILES:")
            for task in verification['missing_files'][:5]:  # Show first 5
                report.append(f"  - {task['file_path']} (Task: {task['task_name'][:50]}...)")
            if len(verification['missing_files']) > 5:
                report.append(f"  ... and {len(verification['missing_files']) - 5} more")
        
        report.append("")
        report.append("🎯 RECOMMENDATIONS")
        report.append("-" * 30)
        
        # Generate recommendations
        if stats['overall_completion_rate'] < 50:
            report.append("• Focus on completing Phase 1 and 2 tasks first")
        if verification['missing_files']:
            report.append("• Create missing files or update file paths in roadmap")
        if len(verification['no_file_specified']) > stats['total_tasks'] * 0.3:
            report.append("• Add file references to more tasks for better tracking")
        
        return "\n".join(report)

def analyze_and_verify_roadmap() -> None:
    """
    วิเคราะห์ Roadmap, นับความคืบหน้า, และตรวจสอบไฟล์ในโค้ดเบส
    เวอร์ชันที่ปรับปรุงแล้ว - แม่นยำและครบถ้วน
    """
    print("\n🛡️  Starting Blueprint Guardian (v4.0 - Enhanced)...")
    
    # Check if roadmap file exists
    if not ROADMAP_PATH.exists():
        print(f"❌ CRITICAL ERROR: Roadmap file not found at {ROADMAP_PATH}")
        return
    
    try:
        content = ROADMAP_PATH.read_text(encoding="utf-8")
        print(f"✅ Successfully loaded roadmap from: {ROADMAP_PATH}")
    except Exception as e:
        print(f"❌ ERROR reading roadmap file: {e}")
        return
    
    # Initialize analyzer
    analyzer = TaskAnalyzer()
    
    # Parse content
    print("📖 Parsing roadmap content...")
    analyzer.parse_roadmap_content(content)
    
    if not analyzer.tasks:
        print("⚠️  WARNING: No tasks found in the roadmap file.")
        print("   Make sure tasks are formatted as: - [x] Task name [file: path]")
        return
    
    # Generate and display report
    print("\n" + "=" * 60)
    report = analyzer.generate_detailed_report()
    print(report)
    print("=" * 60)
    
    # Additional insights
    print("\n🔍 ADDITIONAL INSIGHTS:")
    
    # Find most active phases
    stats = analyzer.get_statistics()
    if stats['phase_statistics']:
        most_active_phase = max(stats['phase_statistics'].items(), 
                              key=lambda x: x[1]['total'])
        print(f"• Most active phase: {most_active_phase[0]} ({most_active_phase[1]['total']} tasks)")
    
    # Find completion trends
    completed_tasks = [task for task in analyzer.tasks if task['completed']]
    if completed_tasks:
        recent_completions = [task for task in completed_tasks 
                            if task['phase'] in ['## Phase 1', '## Phase 2']]
        print(f"• Foundation phases (1-2): {len(recent_completions)} completed tasks")
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    analyze_and_verify_roadmap()
