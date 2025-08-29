#!/usr/bin/env python3
"""
API Endpoints Testing Script for Chonost System
ทดสอบ API endpoints ที่เสร็จแล้วตาม CURRENT_STATUS_SUMMARY.md
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

class ChonostAPITester:
    """Tester for Chonost API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results: List[Dict[str, Any]] = []
        
    def log_test(self, endpoint: str, method: str, success: bool, response: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        """Log test results"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "success": success,
            "response": response,
            "error": error
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {method} {endpoint}")
        if error:
            print(f"   Error: {error}")
        if response:
            print(f"   Response: {json.dumps(response, indent=2, ensure_ascii=False)}")
        print()
    
    def test_health_check(self) -> bool:
        """Test system health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/integrated/system/health")
            success = response.status_code == 200
            self.log_test("/api/integrated/system/health", "GET", success, 
                         response.json() if success else None,
                         str(f"Status: {response.status_code}") if not success else None)
            return success
        except Exception as e:
            self.log_test("/api/integrated/system/health", "GET", False, error=str(e))
            return False
    
    def test_create_manuscript(self) -> bool:
        """Test manuscript creation"""
        try:
            data = {
                "user_id": "test_user_123",
                "title": "Test Manuscript",
                "content": "This is a test manuscript for API testing."
            }
            response = self.session.post(f"{self.base_url}/api/integrated/manuscripts", json=data)
            success = response.status_code == 201
            self.log_test("/api/integrated/manuscripts", "POST", success,
                         response.json() if success else None,
                         str(f"Status: {response.status_code}") if not success else None)
            return success
        except Exception as e:
            self.log_test("/api/integrated/manuscripts", "POST", False, error=str(e))
            return False
    
    def test_get_manuscripts(self) -> bool:
        """Test getting manuscripts list"""
        try:
            response = self.session.get(f"{self.base_url}/api/integrated/manuscripts?user_id=test_user_123")
            success = response.status_code == 200
            self.log_test("/api/integrated/manuscripts", "GET", success,
                         response.json() if success else None,
                         str(f"Status: {response.status_code}") if not success else None)
            return success
        except Exception as e:
            self.log_test("/api/integrated/manuscripts", "GET", False, error=str(e))
            return False
    
    def test_ai_character_analysis(self) -> bool:
        """Test AI character analysis"""
        try:
            data = {
                "content": "John is a brave knight who protects the kingdom. Mary is a wise wizard who helps him on his quest."
            }
            response = self.session.post(f"{self.base_url}/api/integrated/ai/analyze-characters", json=data)
            success = response.status_code == 200
            self.log_test("/api/integrated/ai/analyze-characters", "POST", success,
                         response.json() if success else None,
                         str(f"Status: {response.status_code}") if not success else None)
            return success
        except Exception as e:
            self.log_test("/api/integrated/ai/analyze-characters", "POST", False, error=str(e))
            return False
    
    def test_ai_plot_analysis(self) -> bool:
        """Test AI plot analysis"""
        try:
            data = {
                "content": "The story begins with John discovering a mysterious map. He embarks on a journey to find the hidden treasure."
            }
            response = self.session.post(f"{self.base_url}/api/integrated/ai/analyze-plot", json=data)
            success = response.status_code == 200
            self.log_test("/api/integrated/ai/analyze-plot", "POST", success,
                         response.json() if success else None,
                         str(f"Status: {response.status_code}") if not success else None)
            return success
        except Exception as e:
            self.log_test("/api/integrated/ai/analyze-plot", "POST", False, error=str(e))
            return False
    
    def test_writing_assistant(self) -> bool:
        """Test writing assistant"""
        try:
            data = {
                "content": "The hero walked into the cave.",
                "type": "improve"
            }
            response = self.session.post(f"{self.base_url}/api/integrated/ai/writing-assistant", json=data)
            success = response.status_code == 200
            self.log_test("/api/integrated/ai/writing-assistant", "POST", success,
                         response.json() if success else None,
                         str(f"Status: {response.status_code}") if not success else None)
            return success
        except Exception as e:
            self.log_test("/api/integrated/ai/writing-assistant", "POST", False, error=str(e))
            return False
    
    def test_rag_search(self) -> bool:
        """Test RAG search"""
        try:
            data = {
                "query": "character relationships"
            }
            response = self.session.post(f"{self.base_url}/api/integrated/ai/rag-search", json=data)
            success = response.status_code == 200
            self.log_test("/api/integrated/ai/rag-search", "POST", success,
                         response.json() if success else None,
                         str(f"Status: {response.status_code}") if not success else None)
            return success
        except Exception as e:
            self.log_test("/api/integrated/ai/rag-search", "POST", False, error=str(e))
            return False
    
    def test_analytics_overview(self) -> bool:
        """Test analytics overview"""
        try:
            response = self.session.get(f"{self.base_url}/api/integrated/analytics/overview")
            success = response.status_code == 200
            self.log_test("/api/integrated/analytics/overview", "GET", success,
                         response.json() if success else None,
                         str(f"Status: {response.status_code}") if not success else None)
            return success
        except Exception as e:
            self.log_test("/api/integrated/analytics/overview", "GET", False, error=str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all API tests"""
        print("🚀 Starting Chonost API Endpoints Testing")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Create Manuscript", self.test_create_manuscript),
            ("Get Manuscripts", self.test_get_manuscripts),
            ("AI Character Analysis", self.test_ai_character_analysis),
            ("AI Plot Analysis", self.test_ai_plot_analysis),
            ("Writing Assistant", self.test_writing_assistant),
            ("RAG Search", self.test_rag_search),
            ("Analytics Overview", self.test_analytics_overview),
        ]
        
        results = {}
        total_tests = len(tests)
        passed_tests = 0
        
        for test_name, test_func in tests:
            print(f"Testing: {test_name}")
            try:
                success = test_func()
                results[test_name] = success
                if success:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Exception in {test_name}: {e}")
                results[test_name] = False
        
        # Summary
        print("=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for test_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "results": results,
            "detailed_results": self.test_results
        }

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Chonost API endpoints")
    parser.add_argument("--base-url", default="http://localhost:5000", 
                       help="Base URL for the API (default: http://localhost:5000)")
    parser.add_argument("--output", help="Output file for detailed results")
    
    args = parser.parse_args()
    
    tester = ChonostAPITester(args.base_url)
    results = tester.run_all_tests()
    
    # Save detailed results if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n📄 Detailed results saved to: {args.output}")
    
    # Exit with appropriate code
    if results["passed_tests"] == results["total_tests"]:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {results['failed_tests']} test(s) failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
