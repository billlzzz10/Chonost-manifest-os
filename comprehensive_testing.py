"""
Comprehensive Testing Script for Chonost Desktop App
ทดสอบระบบแบบครบถ้วนตามแผนการทดสอบ
"""

import requests  # pyright: ignore[reportMissingModuleSource]
import time
import webbrowser
import json
from datetime import datetime

class ComprehensiveTesting:
    def __init__(self):
        self.frontend_url = "http://localhost:1420"
        self.backend_url = "http://localhost:8000"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "frontend_tests": {},
            "backend_tests": {},
            "rag_tests": {},
            "performance_tests": {},
            "overall_score": 0
        }
        
    def test_frontend_connectivity(self):
        """ทดสอบการเชื่อมต่อ Frontend"""
        print("🌐 Testing Frontend Connectivity...")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                self.test_results["frontend_tests"]["connectivity"] = {
                    "status": "PASS",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
                print("✅ Frontend connectivity: PASS")
                return True
            else:
                self.test_results["frontend_tests"]["connectivity"] = {
                    "status": "FAIL",
                    "error": f"Status code: {response.status_code}"
                }
                print(f"❌ Frontend connectivity: FAIL (Status: {response.status_code})")
                return False
        except Exception as e:
            self.test_results["frontend_tests"]["connectivity"] = {
                "status": "FAIL",
                "error": str(e)
            }
            print(f"❌ Frontend connectivity: FAIL ({e})")
            return False
    
    def test_backend_connectivity(self):
        """ทดสอบการเชื่อมต่อ Backend"""
        print("🔧 Testing Backend Connectivity...")
        
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.test_results["backend_tests"]["connectivity"] = {
                    "status": "PASS",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code,
                    "service": data.get("service", "unknown")
                }
                print("✅ Backend connectivity: PASS")
                return True
            else:
                self.test_results["backend_tests"]["connectivity"] = {
                    "status": "FAIL",
                    "error": f"Status code: {response.status_code}"
                }
                print(f"❌ Backend connectivity: FAIL (Status: {response.status_code})")
                return False
        except Exception as e:
            self.test_results["backend_tests"]["connectivity"] = {
                "status": "FAIL",
                "error": str(e)
            }
            print(f"❌ Backend connectivity: FAIL ({e})")
            return False
    
    def test_rag_functionality(self):
        """ทดสอบ RAG Functionality"""
        print("🔍 Testing RAG Functionality...")
        
        # Test RAG Info
        try:
            response = requests.get(f"{self.backend_url}/api/rag/info", timeout=10)
            if response.status_code == 200:
                rag_info = response.json()
                self.test_results["rag_tests"]["info"] = {
                    "status": "PASS",
                    "total_documents": rag_info.get("total_documents", 0),
                    "total_chunks": rag_info.get("total_chunks", 0),
                    "response_time": response.elapsed.total_seconds()
                }
                print(f"✅ RAG Info: PASS ({rag_info.get('total_documents', 0)} documents)")
            else:
                self.test_results["rag_tests"]["info"] = {
                    "status": "FAIL",
                    "error": f"Status code: {response.status_code}"
                }
                print(f"❌ RAG Info: FAIL (Status: {response.status_code})")
        except Exception as e:
            self.test_results["rag_tests"]["info"] = {
                "status": "FAIL",
                "error": str(e)
            }
            print(f"❌ RAG Info: FAIL ({e})")
        
        # Test RAG Search
        search_queries = [
            "Trinity Layout",
            "AI Integration",
            "File Management",
            "Performance Testing",
            "Development Roadmap"
        ]
        
        search_results = []
        for query in search_queries:
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.backend_url}/api/rag/search",
                    params={"query": query, "limit": 3},
                    timeout=10
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    results = response.json()
                    search_results.append({
                        "query": query,
                        "status": "PASS",
                        "results_count": len(results),
                        "response_time": response_time,
                        "results": results[:2]  # Store first 2 results
                    })
                    print(f"✅ RAG Search '{query}': PASS ({len(results)} results, {response_time:.3f}s)")
                else:
                    search_results.append({
                        "query": query,
                        "status": "FAIL",
                        "error": f"Status code: {response.status_code}"
                    })
                    print(f"❌ RAG Search '{query}': FAIL (Status: {response.status_code})")
            except Exception as e:
                search_results.append({
                    "query": query,
                    "status": "FAIL",
                    "error": str(e)
                })
                print(f"❌ RAG Search '{query}': FAIL ({e})")
        
        self.test_results["rag_tests"]["search"] = search_results
    
    def test_performance(self):
        """ทดสอบ Performance"""
        print("⚡ Testing Performance...")
        
        # Test API Response Times
        endpoints = [
            "/health",
            "/api/rag/info",
            "/api/rag/search?query=test&limit=1"
        ]
        
        performance_results = {}
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    performance_results[endpoint] = {
                        "status": "PASS",
                        "response_time": response_time,
                        "status_code": response.status_code
                    }
                    print(f"✅ {endpoint}: {response_time:.3f}s")
                else:
                    performance_results[endpoint] = {
                        "status": "FAIL",
                        "error": f"Status code: {response.status_code}"
                    }
                    print(f"❌ {endpoint}: FAIL (Status: {response.status_code})")
            except Exception as e:
                performance_results[endpoint] = {
                    "status": "FAIL",
                    "error": str(e)
                }
                print(f"❌ {endpoint}: FAIL ({e})")
        
        self.test_results["performance_tests"] = performance_results
    
    def calculate_overall_score(self):
        """คำนวณคะแนนรวม"""
        total_tests = 0
        passed_tests = 0

        def count_tests_recursive(obj):
            nonlocal total_tests, passed_tests
            if isinstance(obj, dict):
                if "status" in obj:
                    total_tests += 1
                    if obj.get("status") == "PASS":
                        passed_tests += 1
                else:
                    for value in obj.values():
                        count_tests_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    count_tests_recursive(item)

        # Count tests recursively in all categories
        for category in self.test_results.values():
            if isinstance(category, dict):
                count_tests_recursive(category)

        if total_tests > 0:
            self.test_results["overall_score"] = (passed_tests / total_tests) * 100
        else:
            self.test_results["overall_score"] = 0
    
    def generate_test_report(self):
        """สร้างรายงานการทดสอบ"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        # Frontend Tests
        print("\n🌐 FRONTEND TESTS:")
        for test_name, result in self.test_results["frontend_tests"].items():
            status = "✅ PASS" if result.get("status") == "PASS" else "❌ FAIL"
            print(f"   {test_name}: {status}")
            if "response_time" in result:
                print(f"     Response Time: {result['response_time']:.3f}s")
        
        # Backend Tests
        print("\n🔧 BACKEND TESTS:")
        for test_name, result in self.test_results["backend_tests"].items():
            status = "✅ PASS" if result.get("status") == "PASS" else "❌ FAIL"
            print(f"   {test_name}: {status}")
            if "response_time" in result:
                print(f"     Response Time: {result['response_time']:.3f}s")
        
        # RAG Tests
        print("\n🔍 RAG TESTS:")
        if "info" in self.test_results["rag_tests"]:
            info_result = self.test_results["rag_tests"]["info"]
            status = "✅ PASS" if info_result.get("status") == "PASS" else "❌ FAIL"
            print(f"   Info: {status}")
            if "total_documents" in info_result:
                print(f"     Documents: {info_result['total_documents']}")
                print(f"     Chunks: {info_result['total_chunks']}")
        
        if "search" in self.test_results["rag_tests"]:
            search_results = self.test_results["rag_tests"]["search"]
            print(f"   Search Tests: {len([r for r in search_results if r.get('status') == 'PASS'])}/{len(search_results)} PASS")
        
        # Performance Tests
        print("\n⚡ PERFORMANCE TESTS:")
        for endpoint, result in self.test_results["performance_tests"].items():
            status = "✅ PASS" if result.get("status") == "PASS" else "❌ FAIL"
            print(f"   {endpoint}: {status}")
            if "response_time" in result:
                print(f"     Response Time: {result['response_time']:.3f}s")
        
        # Overall Score
        print("\n" + "=" * 60)
        print(f"🎯 OVERALL SCORE: {self.test_results['overall_score']:.1f}%")
        
        if self.test_results['overall_score'] >= 90:
            print("🏆 EXCELLENT - System is ready for production!")
        elif self.test_results['overall_score'] >= 75:
            print("✅ GOOD - System is functional with minor issues")
        elif self.test_results['overall_score'] >= 50:
            print("⚠️ FAIR - System needs improvements")
        else:
            print("❌ POOR - System needs significant fixes")
        
        print("=" * 60)
    
    def save_test_report(self):
        """บันทึกรายงานการทดสอบ"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Test report saved to: {filename}")
    
    def open_browser_for_manual_testing(self):
        """เปิด browser สำหรับ manual testing"""
        print("\n🌐 Opening browser for manual testing...")
        try:
            webbrowser.open(self.frontend_url)
            print("✅ Browser opened successfully")
            print("\n📝 MANUAL TESTING CHECKLIST:")
            print("1. ✅ The Trinity Layout - ตรวจสอบ 3 panels")
            print("2. ✅ Editor/Whiteboard switching - ทดสอบการสลับ view")
            print("3. ✅ KnowledgeExplorer sidebar - ตรวจสอบ sidebar ซ้าย")
            print("4. ✅ AssistantPanel sidebar - ตรวจสอบ sidebar ขวา")
            print("5. ✅ RAG Search functionality - ทดสอบการค้นหา")
            print("6. ✅ UI Responsiveness - ทดสอบการตอบสนอง")
        except Exception as e:
            print(f"❌ Failed to open browser: {e}")
    
    def run_all_tests(self):
        """รันการทดสอบทั้งหมด"""
        print("🚀 Starting Comprehensive Testing...")
        print("=" * 60)
        
        # Run tests
        self.test_frontend_connectivity()
        self.test_backend_connectivity()
        self.test_rag_functionality()
        self.test_performance()
        
        # Calculate score and generate report
        self.calculate_overall_score()
        self.generate_test_report()
        self.save_test_report()
        
        # Open browser for manual testing
        self.open_browser_for_manual_testing()

def main():
    tester = ComprehensiveTesting()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
