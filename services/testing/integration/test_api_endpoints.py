import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add the application's source directory directly to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'core-services', 'link-ai-core')))

from main import app
from database import Base, get_db
from db_models import Manuscript, Node, Edge

# --- Test Database Setup ---
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# --- Dependency Override for Testing ---
async def override_get_db():
    """
    Dependency override to use the test database.
    """
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# --- Pytest Fixtures ---
@pytest.fixture(scope="session")
def event_loop():
    """
    Creates an instance of the default event loop for the session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """
    Fixture to set up the test database before any tests run,
    and tear it down after all tests are complete.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Clean up the test database file
    if os.path.exists("./test.db"):
        os.remove("./test.db")

@pytest.fixture(scope="function")
async def client() -> AsyncClient:
    """
    Fixture to provide an async test client for making API requests.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# --- Test Cases ---
@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """
    Tests the main health check endpoint.
    """
    response = await client.get("/health")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "healthy"
    assert "service" in json_response

@pytest.mark.asyncio
async def test_create_and_get_manuscript(client: AsyncClient):
    """
    Tests creating a manuscript and then retrieving it.
    """
    # Create a manuscript
    create_response = await client.post(
        "/api/v1/manuscripts",
        json={"title": "My Test Manuscript", "content": "Once upon a time..."}
    )
    assert create_response.status_code == 201
    manuscript_data = create_response.json()
    manuscript_id = manuscript_data["id"]
    assert manuscript_data["title"] == "My Test Manuscript"

    # Get the manuscript
    get_response = await client.get(f"/api/v1/manuscripts/{manuscript_id}")
    assert get_response.status_code == 200
    retrieved_data = get_response.json()
    assert retrieved_data["id"] == manuscript_id
    assert retrieved_data["title"] == "My Test Manuscript"

@pytest.mark.asyncio
async def test_get_all_manuscripts(client: AsyncClient):
    """
    Tests retrieving a list of all manuscripts.
    """
    # Create a couple of manuscripts to ensure the list is not empty
    await client.post("/api/v1/manuscripts", json={"title": "Manuscript A"})
    await client.post("/api/v1/manuscripts", json={"title": "Manuscript B"})

    response = await client.get("/api/v1/manuscripts")
    assert response.status_code == 200
    manuscripts = response.json()
    assert isinstance(manuscripts, list)
    assert len(manuscripts) >= 2

@pytest.mark.asyncio
async def test_update_manuscript(client: AsyncClient):
    """
    Tests updating an existing manuscript.
    """
    # Create a manuscript
    create_response = await client.post("/api/v1/manuscripts", json={"title": "Original Title"})
    manuscript_id = create_response.json()["id"]

    # Update the manuscript
    update_response = await client.put(
        f"/api/v1/manuscripts/{manuscript_id}",
        json={"title": "Updated Title", "is_archived": True}
    )
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["title"] == "Updated Title"
    assert updated_data["is_archived"] is True

@pytest.mark.asyncio
async def test_delete_manuscript(client: AsyncClient):
    """
    Tests deleting a manuscript.
    """
    # Create a manuscript to delete
    create_response = await client.post("/api/v1/manuscripts", json={"title": "To Be Deleted"})
    manuscript_id = create_response.json()["id"]

    # Delete it
    delete_response = await client.delete(f"/api/v1/manuscripts/{manuscript_id}")
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/manuscripts/{manuscript_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_create_node_and_edge_for_manuscript(client: AsyncClient):
    """
    Tests creating a manuscript, adding nodes, and connecting them with an edge.
    """
    # 1. Create Manuscript
    manuscript_res = await client.post("/api/v1/manuscripts", json={"title": "Story with Nodes"})
    manuscript_id = manuscript_res.json()["id"]

    # 2. Create two Nodes linked to the manuscript
    node1_res = await client.post(
        "/api/v1/nodes",
        json={"title": "Character A", "type": "CHARACTER", "manuscript_id": manuscript_id}
    )
    assert node1_res.status_code == 201
    node1_id = node1_res.json()["id"]

    node2_res = await client.post(
        "/api/v1/nodes",
        json={"title": "Location X", "type": "LOCATION", "manuscript_id": manuscript_id}
    )
    assert node2_res.status_code == 201
    node2_id = node2_res.json()["id"]

    # 3. Create an Edge connecting the two nodes
    edge_res = await client.post(
        "/api/v1/edges",
        json={
            "source_id": node1_id,
            "target_id": node2_id,
            "type": "RELATED_TO",
            "label": "was at"
        }
    )
    assert edge_res.status_code == 201
    edge_data = edge_res.json()
    assert edge_data["label"] == "was at"
    assert edge_data["source_id"] == node1_id
    assert edge_data["target_id"] == node2_id

    # 4. Verify the nodes are associated with the manuscript
    manuscript_data = (await client.get(f"/api/v1/manuscripts/{manuscript_id}")).json()

    # NOTE: The current API doesn't automatically return nested nodes.
    # A full test would query the nodes endpoint filtered by manuscript_id.
    nodes_res = await client.get(f"/api/v1/nodes?manuscript_id={manuscript_id}")
    assert nodes_res.status_code == 200
    nodes_data = nodes_res.json()
    assert len(nodes_data) == 2
    assert {n["id"] for n in nodes_data} == {node1_id, node2_id}