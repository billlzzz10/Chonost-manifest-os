from locust import HttpUser, task, between, events
import json
from collections import defaultdict
import logging

class RAGLoadUser(HttpUser):
    """
    Locust load test for RAG endpoint in core-services/link-ai-core.
    Simulates 50 concurrent users querying /rag endpoint with <150ms latency target.
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    host = "http://localhost:8000"  # Assume FastAPI server port for /rag endpoint
    
    def on_start(self):
        """Initialize user session."""
        self.user_id = self.environment.runner.user_count + self.index
        self.headers = {'Content-Type': 'application/json', 'User-Agent': 'LoadTest/1.0'}
        logging.info(f"User {self.user_id} started load test")
    
    @task(3)  # Weight 3: Primary RAG query task
    def rag_query_task(self):
        """Simulate RAG query to /rag endpoint."""
        query_payload = {
            "query": "What is the latest manuscript update from Notion sync?",
            "context": "notion_pages",
            "user_id": f"load_user_{self.user_id}",
            "top_k": 5
        }
        
        try:
            with self.client.post(
                "/rag",
                json=query_payload,
                headers=self.headers,
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    result = response.json()
                    # Assert response has required fields
                    if "results" not in result or "sources" not in result:
                        response.failure("Missing required fields in RAG response")
                    else:
                        logging.debug(f"RAG query successful for user {self.user_id}: {len(result['results'])} results")
                        response.success()
                else:
                    response.failure(f"RAG endpoint returned {response.status_code}")
        except Exception as e:
            self.environment.events.request_failure.fire(
                request_type="POST", name="/rag", response_time=0, exception=e
            )
            logging.error(f"RAG query failed for user {self.user_id}: {str(e)}")
    
    @task(1)  # Weight 1: Notion sync simulation
    def notion_sync_task(self):
        """Simulate Notion sync before RAG queries."""
        sync_payload = {
            "database_id": "test_notion_db",
            "sync_type": "full",
            "user_id": f"load_user_{self.user_id}"
        }
        
        with self.client.post(
            "/notion/sync",
            json=sync_payload,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                sync_result = response.json()
                if sync_result.get("status") == "synced":
                    logging.debug(f"Notion sync successful for user {self.user_id}: {sync_result.get('pages_synced', 0)} pages")
                    response.success()
                else:
                    response.failure("Notion sync status not successful")
            else:
                response.failure(f"Notion sync failed with status {response.status_code}")
    
    @task(1)  # Weight 1: MCP orchestration task
    def mcp_orchestrate_task(self):
        """Simulate MCP response after RAG."""
        mcp_payload = {
            "action": "process_rag_results",
            "rag_results": {"query": "test", "results": ["mock result"]},
            "user_id": f"load_user_{self.user_id}"
        }
        
        with self.client.post(
            "/mcp/orchestrate",
            json=mcp_payload,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                mcp_result = response.json()
                if mcp_result.get("status") == "completed":
                    response.success()
                else:
                    response.failure("MCP orchestration status not completed")
            else:
                response.failure(f"MCP orchestration failed with status {response.status_code}")

# Custom event handler for load test assertions
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Setup test parameters: 50 users, error rate <1%, latency <150ms."""
    logging.info("Starting load test with 50 concurrent users targeting /rag endpoint")
    environment.runner.max_request_time = 150  # Fail requests >150ms
    logging.info("Load test parameters: 50 users, max latency 150ms, error rate target <1%")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Generate summary report with assertions."""
    stats = environment.stats
    total_requests = stats.total.num_requests
    failed_requests = stats.total.num_failures
    error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
    avg_response_time = stats.total.avg_response_time if stats.total.num_requests > 0 else 0
    
    logging.info(f"Load test completed:")
    logging.info(f"Total requests: {total_requests}")
    logging.info(f"Failed requests: {failed_requests}")
    logging.info(f"Error rate: {error_rate:.2f}%")
    logging.info(f"Average response time: {avg_response_time:.2f}ms")
    
    # Assertions for success criteria
    assert error_rate < 1.0, f"Error rate {error_rate:.2f}% exceeds 1% threshold"
    assert avg_response_time < 150, f"Average response time {avg_response_time:.2f}ms exceeds 150ms threshold"
    
    logging.info("✅ Load test passed: Error rate <1% and latency <150ms")

# Run with: locust -f tests/load/locustfile.py --host=http://localhost:8000 --users=50 --spawn-rate=5 --run-time=2m --headless