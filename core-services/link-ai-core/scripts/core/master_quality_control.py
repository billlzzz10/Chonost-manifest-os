#!/usr/bin/env python3
"""
🎯 Master Quality Control System
ระบบควบคุมคุณภาพขั้นสูงที่รวมทุกอย่างเข้าด้วยกัน
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

class MasterQualityControl:
    """Master Quality Control System"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.resolve()
        self.master_path = self.project_root / "master_quality_control"
        self.master_path.mkdir(parents=True, exist_ok=True)
        
    def run_complete_quality_cycle(self, model_path: str = "models/chonost-compact-local") -> Dict[str, Any]:
        """รัน complete quality cycle"""
        print("🎯 Starting Master Quality Control Cycle...")
        
        cycle_results = {
            "cycle_start": datetime.now().isoformat(),
            "model_path": model_path,
            "steps": [],
            "final_results": {},
            "recommendations": []
        }
        
        # Step 1: Quality Assessment
        print("\n🔍 Step 1: Quality Assessment")
        step1_result = self.run_quality_assessment(model_path)
        cycle_results["steps"].append({
            "step": "quality_assessment",
            "result": step1_result,
            "timestamp": datetime.now().isoformat()
        })
        
        # Step 2: Analyze Results
        print("\n📊 Step 2: Analyze Results")
        step2_result = self.analyze_quality_results(step1_result)
        cycle_results["steps"].append({
            "step": "analysis",
            "result": step2_result,
            "timestamp": datetime.now().isoformat()
        })
        
        # Step 3: Generate Enhanced Dataset
        print("\n📚 Step 3: Generate Enhanced Dataset")
        step3_result = self.generate_enhanced_dataset(step1_result, step2_result)
        cycle_results["steps"].append({
            "step": "enhanced_dataset",
            "result": step3_result,
            "timestamp": datetime.now().isoformat()
        })
        
        # Step 4: Retraining Decision
        print("\n🤔 Step 4: Retraining Decision")
        step4_result = self.make_retraining_decision(step1_result, step2_result)
        cycle_results["steps"].append({
            "step": "retraining_decision",
            "result": step4_result,
            "timestamp": datetime.now().isoformat()
        })
        
        # Step 5: Execute Retraining (if needed)
        if step4_result["should_retrain"]:
            print("\n🔄 Step 5: Execute Retraining")
            step5_result = self.execute_retraining(model_path, step3_result["enhanced_dataset_path"])
            cycle_results["steps"].append({
                "step": "retraining",
                "result": step5_result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 6: Re-assessment
            if step5_result["success"]:
                print("\n🔍 Step 6: Re-assessment")
                step6_result = self.run_quality_assessment(step5_result["new_model_path"])
                cycle_results["steps"].append({
                    "step": "re_assessment",
                    "result": step6_result,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Step 7: Improvement Analysis
                print("\n📈 Step 7: Improvement Analysis")
                step7_result = self.analyze_improvement(step1_result, step6_result)
                cycle_results["steps"].append({
                    "step": "improvement_analysis",
                    "result": step7_result,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Final Results
        cycle_results["final_results"] = {
            "initial_quality": step1_result,
            "final_quality": cycle_results["steps"][-1]["result"] if cycle_results["steps"] else step1_result,
            "improvement": self.calculate_improvement(step1_result, cycle_results["steps"][-1]["result"] if cycle_results["steps"] else step1_result)
        }
        
        # Generate Recommendations
        cycle_results["recommendations"] = self.generate_final_recommendations(cycle_results)
        
        # Save Results
        cycle_results["cycle_end"] = datetime.now().isoformat()
        self.save_cycle_results(cycle_results)
        
        return cycle_results
    
    def run_quality_assessment(self, model_path: str) -> Dict[str, Any]:
        """รัน quality assessment"""
        try:
            # Import quality assessment framework
            from quality_assessment import QualityAssessmentFramework
            framework = QualityAssessmentFramework()
            
            # Create test suite
            test_suite = framework.create_quality_test_suite()
            
            # Assess model quality
            results = framework.assess_model_quality(model_path, test_suite)
            
            # Save quality report
            report_path = framework.save_quality_report(results)
            
            return {
                "success": True,
                "quality_report_path": str(report_path),
                "results": results,
                "grade": results["quality_grade"],
                "score": results["total_score"] / results["max_score"] * 100
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "grade": "F",
                "score": 0
            }
    
    def analyze_quality_results(self, quality_result: Dict[str, Any]) -> Dict[str, Any]:
        """วิเคราะห์ผลลัพธ์คุณภาพ"""
        if not quality_result["success"]:
            return {
                "success": False,
                "error": "Quality assessment failed"
            }
        
        results = quality_result["results"]
        
        analysis = {
            "success": True,
            "overall_score": results["total_score"] / results["max_score"] * 100,
            "grade": results["quality_grade"],
            "category_analysis": {},
            "weak_points": [],
            "strong_points": [],
            "critical_issues": []
        }
        
        # วิเคราะห์แต่ละหมวดหมู่
        for category, scores in results["category_scores"].items():
            percentage = scores["percentage"]
            analysis["category_analysis"][category] = {
                "score": percentage,
                "status": "strong" if percentage >= 80 else "moderate" if percentage >= 60 else "weak"
            }
            
            if percentage < 60:
                analysis["weak_points"].append(f"{category}: {percentage:.1f}%")
                if percentage < 40:
                    analysis["critical_issues"].append(f"{category}: {percentage:.1f}%")
            elif percentage >= 80:
                analysis["strong_points"].append(f"{category}: {percentage:.1f}%")
        
        return analysis
    
    def generate_enhanced_dataset(self, quality_result: Dict[str, Any], analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """สร้าง enhanced dataset"""
        if not quality_result["success"] or not analysis_result["success"]:
            return {
                "success": False,
                "error": "Cannot generate dataset without quality results"
            }
        
        try:
            # Import retraining system
            from advanced_retraining import AdvancedRetrainingSystem
            retraining_system = AdvancedRetrainingSystem()
            
            # Load quality report
            quality_report = retraining_system.load_quality_report(quality_result["quality_report_path"])
            
            # Analyze failure patterns
            failure_analysis = retraining_system.analyze_failure_patterns(quality_report)
            
            # Create enhanced dataset
            enhanced_data = retraining_system.create_enhanced_dataset(quality_report, failure_analysis)
            
            # Save enhanced dataset
            dataset_path = retraining_system.save_retraining_dataset(enhanced_data)
            
            return {
                "success": True,
                "enhanced_dataset_path": str(dataset_path),
                "dataset_size": len(enhanced_data),
                "failure_analysis": failure_analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def make_retraining_decision(self, quality_result: Dict[str, Any], analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """ตัดสินใจว่าจะเทรนซ้ำหรือไม่"""
        decision = {
            "should_retrain": False,
            "reason": "",
            "priority": "low",
            "estimated_iterations": 0
        }
        
        if not quality_result["success"]:
            decision["should_retrain"] = True
            decision["reason"] = "Quality assessment failed - retraining required"
            decision["priority"] = "critical"
            decision["estimated_iterations"] = 3
            return decision
        
        score = quality_result["score"]
        
        if score < 50:
            decision["should_retrain"] = True
            decision["reason"] = "Critical quality issues - immediate retraining required"
            decision["priority"] = "critical"
            decision["estimated_iterations"] = 3
        elif score < 70:
            decision["should_retrain"] = True
            decision["reason"] = "Moderate quality issues - retraining recommended"
            decision["priority"] = "high"
            decision["estimated_iterations"] = 2
        elif score < 85:
            decision["should_retrain"] = True
            decision["reason"] = "Minor quality issues - optional retraining"
            decision["priority"] = "medium"
            decision["estimated_iterations"] = 1
        else:
            decision["should_retrain"] = False
            decision["reason"] = "Quality is acceptable - no retraining needed"
            decision["priority"] = "none"
            decision["estimated_iterations"] = 0
        
        return decision
    
    def execute_retraining(self, model_path: str, enhanced_dataset_path: str) -> Dict[str, Any]:
        """เทรนซ้ำโมเดล"""
        try:
            # Import retraining system
            from advanced_retraining import AdvancedRetrainingSystem
            retraining_system = AdvancedRetrainingSystem()
            
            # Load enhanced dataset
            enhanced_data = []
            with open(enhanced_dataset_path, 'r', encoding='utf-8') as f:
                for line in f:
                    enhanced_data.append(json.loads(line.strip()))
            
            # Retrain model
            success = retraining_system.retrain_model(model_path, enhanced_data, 1)
            
            if success:
                new_model_path = str(retraining_system.retraining_path / "retrained_model_iteration_1")
                return {
                    "success": True,
                    "new_model_path": new_model_path,
                    "original_model_path": model_path
                }
            else:
                return {
                    "success": False,
                    "error": "Retraining failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_improvement(self, initial_result: Dict[str, Any], final_result: Dict[str, Any]) -> Dict[str, Any]:
        """วิเคราะห์การปรับปรุง"""
        if not initial_result["success"] or not final_result["success"]:
            return {
                "success": False,
                "error": "Cannot analyze improvement without both results"
            }
        
        initial_score = initial_result["score"]
        final_score = final_result["score"]
        
        improvement = {
            "success": True,
            "initial_score": initial_score,
            "final_score": final_score,
            "score_improvement": final_score - initial_score,
            "percentage_improvement": ((final_score - initial_score) / initial_score * 100) if initial_score > 0 else 0,
            "grade_improvement": self.compare_grades(initial_result["grade"], final_result["grade"]),
            "status": "improved" if final_score > initial_score else "same" if final_score == initial_score else "worsened"
        }
        
        return improvement
    
    def compare_grades(self, initial_grade: str, final_grade: str) -> str:
        """เปรียบเทียบเกรด"""
        grade_order = ["F", "C", "C+", "B", "B+", "A", "A+"]
        
        try:
            initial_index = next(i for i, grade in enumerate(grade_order) if grade in initial_grade)
            final_index = next(i for i, grade in enumerate(grade_order) if grade in final_grade)
            
            if final_index > initial_index:
                return "improved"
            elif final_index < initial_index:
                return "worsened"
            else:
                return "same"
        except:
            return "unknown"
    
    def calculate_improvement(self, initial_result: Dict[str, Any], final_result: Dict[str, Any]) -> Dict[str, Any]:
        """คำนวณการปรับปรุง"""
        if not initial_result["success"] or not final_result["success"]:
            return {"success": False}
        
        return {
            "success": True,
            "score_improvement": final_result["score"] - initial_result["score"],
            "grade_improvement": self.compare_grades(initial_result["grade"], final_result["grade"])
        }
    
    def generate_final_recommendations(self, cycle_results: Dict[str, Any]) -> List[str]:
        """สร้างคำแนะนำสุดท้าย"""
        recommendations = []
        
        final_quality = cycle_results["final_results"]["final_quality"]
        improvement = cycle_results["final_results"]["improvement"]
        
        if not final_quality["success"]:
            recommendations.append("🔴 CRITICAL: Model quality assessment failed")
            recommendations.append("🔄 Immediate retraining required")
            return recommendations
        
        score = final_quality["score"]
        grade = final_quality["grade"]
        
        if score >= 90:
            recommendations.append("🟢 EXCELLENT: Model quality is outstanding")
            recommendations.append("🚀 Ready for production deployment")
            recommendations.append("📈 Consider advanced optimization techniques")
        elif score >= 80:
            recommendations.append("🟢 GOOD: Model quality is very good")
            recommendations.append("✅ Ready for most use cases")
            recommendations.append("🔧 Minor optimizations may be beneficial")
        elif score >= 70:
            recommendations.append("🟡 MODERATE: Model quality is acceptable")
            recommendations.append("⚠️ Monitor performance in production")
            recommendations.append("📚 Consider additional training data")
        elif score >= 60:
            recommendations.append("🟡 NEEDS IMPROVEMENT: Model quality needs work")
            recommendations.append("🔄 Additional retraining recommended")
            recommendations.append("📊 Focus on weak categories")
        else:
            recommendations.append("🔴 POOR: Model quality is insufficient")
            recommendations.append("🔄 Extensive retraining required")
            recommendations.append("📚 Significant data improvements needed")
        
        # Add improvement-specific recommendations
        if improvement["success"]:
            if improvement["score_improvement"] > 10:
                recommendations.append("📈 Significant improvement achieved!")
            elif improvement["score_improvement"] > 0:
                recommendations.append("📈 Some improvement achieved")
            elif improvement["score_improvement"] < 0:
                recommendations.append("📉 Quality decreased - investigate issues")
        
        return recommendations
    
    def save_cycle_results(self, cycle_results: Dict[str, Any]):
        """บันทึกผลลัพธ์ cycle"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.master_path / f"quality_cycle_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(cycle_results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Cycle results saved: {results_file}")
        return results_file
    
    def generate_summary_report(self, cycle_results: Dict[str, Any]) -> str:
        """สร้างรายงานสรุป"""
        summary = f"""
# 🎯 Master Quality Control Report

## 📊 Cycle Summary
- **Start Time**: {cycle_results['cycle_start']}
- **End Time**: {cycle_results['cycle_end']}
- **Model Path**: {cycle_results['model_path']}

## 📈 Quality Results
- **Initial Grade**: {cycle_results['final_results']['initial_quality']['grade']}
- **Final Grade**: {cycle_results['final_results']['final_quality']['grade']}
- **Initial Score**: {cycle_results['final_results']['initial_quality']['score']:.1f}%
- **Final Score**: {cycle_results['final_results']['final_quality']['score']:.1f}%

## 🔄 Improvement Analysis
- **Score Improvement**: {cycle_results['final_results']['improvement']['score_improvement']:.1f}%
- **Grade Improvement**: {cycle_results['final_results']['improvement']['grade_improvement']}

## 📋 Steps Executed
"""
        
        for step in cycle_results['steps']:
            summary += f"- **{step['step']}**: {step['timestamp']}\n"
        
        summary += f"""
## 💡 Recommendations
"""
        
        for rec in cycle_results['recommendations']:
            summary += f"- {rec}\n"
        
        return summary

def main():
    """Main function"""
    master_control = MasterQualityControl()
    
    print("🎯 Master Quality Control System")
    print("1. Run Complete Quality Cycle")
    print("2. Generate Summary Report")
    print("3. View Previous Results")
    
    choice = input("\nเลือกตัวเลือก (1-3): ").strip()
    
    try:
        if choice == "1":
            model_path = input("Enter model path (default: models/chonost-compact-local): ").strip()
            if not model_path:
                model_path = "models/chonost-compact-local"
            
            results = master_control.run_complete_quality_cycle(model_path)
            
            # Generate summary
            summary = master_control.generate_summary_report(results)
            print("\n" + summary)
            
        elif choice == "2":
            # Generate summary from existing results
            results_files = list(master_control.master_path.glob("quality_cycle_results_*.json"))
            if results_files:
                latest_file = max(results_files, key=lambda x: x.stat().st_mtime)
                with open(latest_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                
                summary = master_control.generate_summary_report(results)
                print("\n" + summary)
            else:
                print("❌ No previous results found")
                
        elif choice == "3":
            # View previous results
            results_files = list(master_control.master_path.glob("quality_cycle_results_*.json"))
            if results_files:
                print("\n📁 Previous Results:")
                for file in sorted(results_files, key=lambda x: x.stat().st_mtime, reverse=True):
                    print(f"- {file.name}")
            else:
                print("❌ No previous results found")
                
        else:
            print("❌ Invalid choice!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
