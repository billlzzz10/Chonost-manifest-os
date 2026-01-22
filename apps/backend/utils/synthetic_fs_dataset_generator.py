#!/usr/bin/env python3
"""
Dataset Generator for File System MCP Tool Training.
This script generates a dataset for training an AI agent to understand how
to use the file system management tools.
"""

import json
import random
from datetime import datetime


class FileSystemDatasetGenerator:
    """
    A dataset generator for training an AI agent.

    This class provides methods for generating a dataset for training an AI
    agent to understand how to use the file system management tools.
    """

    def __init__(self, db_path: str = "file_system_analysis.db"):
        """
        Initializes the FileSystemDatasetGenerator.

        Args:
            db_path (str, optional): The path to the database. Defaults to
                                     "file_system_analysis.db".
        """
        self.db_path = db_path
        self.dataset = []

    def generate_training_dataset(
        self, output_file: str = "file_system_training_dataset.json"
    ):
        """
        Generates a training dataset for the AI agent.

        Args:
            output_file (str, optional): The path to the output file.
                                      Defaults to "file_system_training_dataset.json".
        """
        print("🚀 Starting to generate the training dataset for the AI agent...")

        # 1. Generate basic queries
        self._generate_basic_queries()

        # 2. Generate file search queries
        self._generate_file_search_queries()

        # 3. Generate analysis queries
        self._generate_analysis_queries()

        # 4. Generate SQL queries
        self._generate_sql_queries()

        # 5. Generate file management queries
        self._generate_file_management_queries()

        # 6. Generate reporting queries
        self._generate_reporting_queries()

        # 7. Save the dataset
        self._save_dataset(output_file)

        print(f"✅ Successfully generated the dataset: {len(self.dataset)} items")
        print(f"📁 Saved to: {output_file}")

    def _generate_basic_queries(self):
        """Generates a set of basic queries."""
        basic_queries = [
            {
                "instruction": "Summarize this folder for me.",
                "correct_action": {
                    "action": "query_function",
                    "function": "get_directory_summary",
                    "session_id": "scan_xxx",
                    "args": [],
                },
                "category": "basic",
                "description": "Request a basic summary of the folder.",
            },
            {
                "instruction": "How many files are in this folder in total?",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT COUNT(*) as total_files FROM files WHERE session_id = ?",
                    "params": ["scan_xxx"],
                },
                "category": "basic",
                "description": "Count the total number of files.",
            },
            {
                "instruction": "What is the total size of the folder?",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT SUM(file_size) as total_size FROM files WHERE session_id = ?",
                    "params": ["scan_xxx"],
                },
                "category": "basic",
                "description": "Calculate the total size of the folder.",
            },
            {
                "instruction": "Show the 10 largest files.",
                "correct_action": {
                    "action": "query_function",
                    "function": "get_largest_files",
                    "session_id": "scan_xxx",
                    "args": [10],
                },
                "category": "basic",
                "description": "Show the largest files.",
            },
            {
                "instruction": "Are there any duplicate files?",
                "correct_action": {
                    "action": "query_function",
                    "function": "get_duplicate_files",
                    "session_id": "scan_xxx",
                    "args": [],
                },
                "category": "basic",
                "description": "Check for duplicate files.",
            },
        ]

        self.dataset.extend(basic_queries)

    def _generate_file_search_queries(self):
        """Generates a set of file search queries."""
        file_search_queries = [
            {
                "instruction": "Find the 5 largest Word document files.",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, file_size FROM files WHERE session_id = ? AND file_extension = '.docx' ORDER BY file_size DESC LIMIT 5",
                    "params": ["scan_xxx"],
                },
                "category": "file_search",
                "description": "Find large Word files.",
            },
            {
                "instruction": "Show all image files.",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, file_size FROM files WHERE session_id = ? AND mime_type LIKE 'image/%'",
                    "params": ["scan_xxx"],
                },
                "category": "file_search",
                "description": "Find image files.",
            },
            {
                "instruction": "How many PDF files are in the system?",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT COUNT(*) as pdf_count FROM files WHERE session_id = ? AND file_extension = '.pdf'",
                    "params": ["scan_xxx"],
                },
                "category": "file_search",
                "description": "Count PDF files.",
            },
            {
                "instruction": "Show all files with 'report' in the name that are PDFs.",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_path FROM files WHERE session_id = ? AND file_name LIKE '%report%' AND file_extension = '.pdf'",
                    "params": ["scan_xxx"],
                },
                "category": "file_search",
                "description": "Find PDF files with 'report' in the name.",
            },
            {
                "instruction": "Find the largest Python code file.",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, file_size FROM files WHERE session_id = ? AND file_extension = '.py' ORDER BY file_size DESC LIMIT 1",
                    "params": ["scan_xxx"],
                },
                "category": "file_search",
                "description": "Find the largest Python file.",
            },
            {
                "instruction": "Show all JavaScript files.",
                "correct_action": {
                    "action": "query_function",
                    "function": "find_files_by_extension",
                    "session_id": "scan_xxx",
                    "args": [".js"],
                },
                "category": "file_search",
                "description": "Find JavaScript files.",
            },
            {
                "instruction": "Which duplicate files are taking up the most space?",
                "correct_action": {
                    "action": "query_function",
                    "function": "get_duplicate_files",
                    "session_id": "scan_xxx",
                    "args": [],
                },
                "category": "file_search",
                "description": "Check for duplicate files that are taking up the most space.",
            },
        ]

        self.dataset.extend(file_search_queries)

    def _generate_analysis_queries(self):
        """Generates a set of analysis queries."""
        analysis_queries = [
            {
                "instruction": "Analyze the file types found in the folder.",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_extension, COUNT(*) as count, SUM(file_size) as total_size FROM files WHERE session_id = ? GROUP BY file_extension ORDER BY count DESC",
                    "params": ["scan_xxx"],
                },
                "category": "analysis",
                "description": "Analyze file types.",
            },
            {
                "instruction": "Which file types use the most space?",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_extension, SUM(file_size) as total_size FROM files WHERE session_id = ? GROUP BY file_extension ORDER BY total_size DESC LIMIT 5",
                    "params": ["scan_xxx"],
                },
                "category": "analysis",
                "description": "Analyze which files use the most space.",
            },
            {
                "instruction": "How many hidden files are there?",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT COUNT(*) as hidden_count FROM files WHERE session_id = ? AND is_hidden = 1",
                    "params": ["scan_xxx"],
                },
                "category": "analysis",
                "description": "Count hidden files.",
            },
            {
                "instruction": "Which are the oldest files?",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, created_date FROM files WHERE session_id = ? ORDER BY created_date ASC LIMIT 10",
                    "params": ["scan_xxx"],
                },
                "category": "analysis",
                "description": "Find the oldest files.",
            },
            {
                "instruction": "Which files were modified most recently?",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, modified_date FROM files WHERE session_id = ? ORDER BY modified_date DESC LIMIT 10",
                    "params": ["scan_xxx"],
                },
                "category": "analysis",
                "description": "Find the most recently modified files.",
            },
        ]

        self.dataset.extend(analysis_queries)

    def _generate_sql_queries(self):
        """Generates a set of SQL queries."""
        sql_queries = [
            {
                "instruction": "Show files larger than 100MB.",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, file_size FROM files WHERE session_id = ? AND file_size > 104857600 ORDER BY file_size DESC",
                    "params": ["scan_xxx"],
                },
                "category": "sql",
                "description": "Find large files.",
            },
            {
                "instruction": "What are the image files larger than 10MB?",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, file_size FROM files WHERE session_id = ? AND mime_type LIKE 'image/%' AND file_size > 10485760",
                    "params": ["scan_xxx"],
                },
                "category": "sql",
                "description": "Find large image files.",
            },
            {
                "instruction": "Show files created this month.",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, created_date FROM files WHERE session_id = ? AND created_date >= date('now', 'start of month')",
                    "params": ["scan_xxx"],
                },
                "category": "sql",
                "description": "Find files created this month.",
            },
            {
                "instruction": "What files were modified this week?",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, modified_date FROM files WHERE session_id = ? AND modified_date >= date('now', '-7 days')",
                    "params": ["scan_xxx"],
                },
                "category": "sql",
                "description": "Find files modified this week.",
            },
            {
                "instruction": "Show files with no extension.",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path FROM files WHERE session_id = ? AND (file_extension = '' OR file_extension IS NULL)",
                    "params": ["scan_xxx"],
                },
                "category": "sql",
                "description": "Find files with no extension.",
            },
        ]

        self.dataset.extend(sql_queries)

    def _generate_file_management_queries(self):
        """Generates a set of file management queries."""
        management_queries = [
            {
                "instruction": "Which files should be deleted to save space?",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, file_size FROM files WHERE session_id = ? AND file_size > 52428800 ORDER BY file_size DESC LIMIT 20",
                    "params": ["scan_xxx"],
                },
                "category": "management",
                "description": "Find files that should be deleted.",
            },
            {
                "instruction": "What temporary files are there?",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path FROM files WHERE session_id = ? AND (file_name LIKE '%.tmp' OR file_name LIKE 'temp%' OR file_name LIKE '%cache%')",
                    "params": ["scan_xxx"],
                },
                "category": "management",
                "description": "Find temporary files.",
            },
            {
                "instruction": "Which files were accessed most recently?",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, accessed_date FROM files WHERE session_id = ? ORDER BY accessed_date DESC LIMIT 10",
                    "params": ["scan_xxx"],
                },
                "category": "management",
                "description": "Find the most recently accessed files.",
            },
            {
                "instruction": "Show files that might be viruses.",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path FROM files WHERE session_id = ? AND file_extension IN ('.exe', '.bat', '.cmd', '.scr', '.pif')",
                    "params": ["scan_xxx"],
                },
                "category": "management",
                "description": "Find files that might be viruses.",
            },
        ]

        self.dataset.extend(management_queries)

    def _generate_reporting_queries(self):
        """Generates a set of reporting queries."""
        reporting_queries = [
            {
                "instruction": "Create a summary report of the folder.",
                "correct_action": {
                    "action": "query_function",
                    "function": "get_directory_summary",
                    "session_id": "scan_xxx",
                    "args": [],
                },
                "category": "reporting",
                "description": "Create a summary report.",
            },
            {
                "instruction": "Report the 20 largest files.",
                "correct_action": {
                    "action": "query_function",
                    "function": "get_largest_files",
                    "session_id": "scan_xxx",
                    "args": [20],
                },
                "category": "reporting",
                "description": "Report large files.",
            },
            {
                "instruction": "Report all duplicate files.",
                "correct_action": {
                    "action": "query_function",
                    "function": "get_duplicate_files",
                    "session_id": "scan_xxx",
                    "args": [],
                },
                "category": "reporting",
                "description": "Report duplicate files.",
            },
            {
                "instruction": "File type statistics.",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_extension, COUNT(*) as count, AVG(file_size) as avg_size FROM files WHERE session_id = ? GROUP BY file_extension ORDER BY count DESC",
                    "params": ["scan_xxx"],
                },
                "category": "reporting",
                "description": "File type statistics.",
            },
        ]

        self.dataset.extend(reporting_queries)

    def _save_dataset(self, output_file: str):
        """
        Saves the dataset to a file.

        Args:
            output_file (str): The path to the output file.
        """
        dataset_info = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_samples": len(self.dataset),
                "categories": list(set(item["category"] for item in self.dataset)),
                "description": "Dataset for training an AI agent to understand how to use the File System MCP Tool.",
            },
            "dataset": self.dataset,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(dataset_info, f, ensure_ascii=False, indent=2)

    def generate_variations(
        self, base_dataset_file: str, output_file: str = "expanded_dataset.json"
    ):
        """
        Generates a more diverse dataset by creating variations of the
        instructions in the base dataset.

        Args:
            base_dataset_file (str): The path to the base dataset file.
            output_file (str, optional): The path to the output file.
                                      Defaults to "expanded_dataset.json".
        """
        print("🔄 Generating a more diverse dataset...")

        with open(base_dataset_file, "r", encoding="utf-8") as f:
            base_data = json.load(f)

        expanded_dataset = base_data["dataset"].copy()

        # Create a variety of commands
        variations = [
            (
                "Show large files",
                [
                    "Show the largest files",
                    "Which files are the largest",
                    "What are the large files",
                ],
            ),
            (
                "Find duplicate files",
                [
                    "Are there duplicate files",
                    "Which files are duplicates",
                    "Check for duplicate files",
                ],
            ),
            (
                "Summarize data",
                ["Summarize the folder", "Summary data", "Summary report"],
            ),
            ("Image files", ["All image files", "Image file", "What are the images"]),
            ("Document files", ["Word files", "All documents", ".docx files"]),
        ]

        for original, variations_list in variations:
            for variation in variations_list:
                # Find the entry that matches the original
                for entry in base_data["dataset"]:
                    if original in entry["instruction"]:
                        new_entry = entry.copy()
                        new_entry["instruction"] = entry["instruction"].replace(
                            original, variation
                        )
                        new_entry["category"] = "variation"
                        expanded_dataset.append(new_entry)

        # Save the expanded dataset
        expanded_info = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_samples": len(expanded_dataset),
                "base_samples": len(base_data["dataset"]),
                "variations_added": len(expanded_dataset) - len(base_data["dataset"]),
                "description": "Expanded dataset with variations",
            },
            "dataset": expanded_dataset,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(expanded_info, f, ensure_ascii=False, indent=2)

        print(
            f"✅ Successfully generated the expanded dataset: {len(expanded_dataset)} items"
        )

    def generate_test_dataset(
        self, training_dataset_file: str, output_file: str = "test_dataset.json"
    ):
        """
        Generates a test dataset from the training dataset.

        Args:
            training_dataset_file (str): The path to the training dataset file.
            output_file (str, optional): The path to the output file.
                                      Defaults to "test_dataset.json".
        """
        print("🧪 Generating a test dataset...")

        with open(training_dataset_file, "r", encoding="utf-8") as f:
            training_data = json.load(f)

        # Randomly select 20% for testing
        test_samples = random.sample(
            training_data["dataset"], min(len(training_data["dataset"]) // 5, 50)
        )

        test_info = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_samples": len(test_samples),
                "source": training_dataset_file,
                "description": "Test dataset for File System MCP Tool",
            },
            "dataset": test_samples,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(test_info, f, ensure_ascii=False, indent=2)

        print(f"✅ Successfully generated the test dataset: {len(test_samples)} items")

    def analyze_dataset(self, dataset_file: str):
        """
        Analyzes a dataset.

        Args:
            dataset_file (str): The path to the dataset file.
        """
        print(f"📊 Analyzing dataset: {dataset_file}")

        with open(dataset_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        dataset = data["dataset"]

        # Analyze by category
        categories = {}
        for item in dataset:
            cat = item["category"]
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1

        print("\n📈 Dataset statistics:")
        print(f"• Total number of samples: {len(dataset)}")
        print(f"• Number of categories: {len(categories)}")

        print("\n📋 Categories:")
        for cat, count in sorted(categories.items()):
            percentage = (count / len(dataset)) * 100
            print(f"  • {cat}: {count} ({percentage:.1f}%)")

        # Analyze actions
        actions = {}
        for item in dataset:
            action = item["correct_action"]["action"]
            if action not in actions:
                actions[action] = 0
            actions[action] += 1

        print("\n🔧 Actions used:")
        for action, count in sorted(actions.items()):
            percentage = (count / len(dataset)) * 100
            print(f"  • {action}: {count} ({percentage:.1f}%)")


def main():
    """The main function of the script."""
    print("🚀 File System MCP Dataset Generator")
    print("=" * 50)

    generator = FileSystemDatasetGenerator()

    # Generate the base dataset
    generator.generate_training_dataset("file_system_training_dataset.json")

    # Generate the expanded dataset
    generator.generate_variations(
        "file_system_training_dataset.json", "expanded_dataset.json"
    )

    # Generate the test dataset
    generator.generate_test_dataset(
        "file_system_training_dataset.json", "test_dataset.json"
    )

    # Analyze the datasets
    print("\n" + "=" * 50)
    generator.analyze_dataset("file_system_training_dataset.json")

    print("\n" + "=" * 50)
    generator.analyze_dataset("expanded_dataset.json")

    print("\n" + "=" * 50)
    generator.analyze_dataset("test_dataset.json")

    print("\n🎉 Dataset generation complete!")
    print("\n📁 Files created:")
    print("  • file_system_training_dataset.json - Base dataset")
    print("  • expanded_dataset.json - Expanded dataset")
    print("  • test_dataset.json - Test dataset")


if __name__ == "__main__":
    main()
