#!/usr/bin/env python3
"""
สคริปต์สำหรับการสร้างดาต้าเซ็ตอัตโนมัติ
"""

import sys
import os
from pathlib import Path

# เพิ่ม src directory เข้าไปใน Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    from dataset_generator import DatasetGenerator
except ImportError:
    print("Error: Could not import DatasetGenerator")
    print("Make sure the dataset_generator.py file exists in the src directory")
    sys.exit(1)

def main() -> None:
    """ฟังก์ชันหลักสำหรับการรันการสร้างดาต้าเซ็ต"""
    
    # ตรวจสอบ arguments
    if len(sys.argv) < 2:
        print("Usage: python generate_datasets.py <log_file_path>")
        print("Example: python generate_datasets.py logs/conversation.log")
        sys.exit(1)
    
    log_file_path = sys.argv[1]
    
    # ตรวจสอบว่าไฟล์ log มีอยู่จริงหรือไม่
    if not os.path.exists(log_file_path):
        print(f"Error: Log file not found: {log_file_path}")
        print("Please provide a valid log file path")
        sys.exit(1)
    
    try:
        # สร้าง generator
        generator = DatasetGenerator()
        
        print(f"Starting dataset generation from: {log_file_path}")
        print("=" * 50)
        
        # สร้างดาต้าเซ็ตทั้งหมด
        results = generator.generate_all_datasets(log_file_path)
        
        if not results:
            print("Error: No datasets were generated")
            sys.exit(1)
        
        # สร้างรายงานสรุป
        summary_file = generator.create_dataset_summary(results)
        
        print("\n" + "=" * 50)
        print("Dataset generation completed successfully!")
        print("=" * 50)
        
        print(f"\nSummary saved to: {summary_file}")
        print(f"\nGenerated datasets:")
        
        for dataset_type, file_path in results.items():
            print(f"  📁 {dataset_type.upper()}: {file_path}")
        
        print(f"\nTotal datasets created: {len(results)}")
        
        # แสดงสถิติ
        print("\n📊 Statistics:")
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                import json
                summary = json.load(f)
                stats = summary.get('statistics', {})
                
                for dataset_type, count in stats.items():
                    print(f"  - {dataset_type}: {count} entries")
        except Exception as e:
            print(f"  Error reading statistics: {e}")
        
        print("\n✅ All done! Your datasets are ready for use.")
        
    except Exception as e:
        print(f"Error during dataset generation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
