"""
Agent Routes - Custom Agent Builder API

This module provides endpoints for creating, managing, and executing custom agents.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json

# Import database and auth
try:
    from src.database import get_db_connection
    from src.models.user import User
except ImportError:
    # Fallback imports
    def get_db_connection():
        return None
    
    class User:
        pass

# Security
security = HTTPBearer()

# Pydantic models
class AgentBase(BaseModel):
    name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    config: Dict[str, Any] = Field(..., description="Agent configuration")
    is_active: bool = Field(True, description="Whether the agent is active")

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class Agent(AgentBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ExecutionInput(BaseModel):
    input_data: Dict[str, Any] = Field(..., description="Input data for agent execution")

class Execution(BaseModel):
    id: str
    agent_id: str
    status: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Create router
router = APIRouter(prefix="/agents", tags=["agents"])

# Dependency for authentication (placeholder)
async def get_current_user(token: str = Depends(security)):
    # TODO: Implement proper JWT token validation
    return {"id": "user-123", "email": "user@example.com"}

class AgentModel:
    """Agent model for database operations"""
    
    def __init__(self, db_connection):
        self.conn = db_connection
        self.cursor = db_connection.cursor()

    def create_agent(self, agent_data):
        """Create a new agent"""
        try:
            query = """
                INSERT INTO agents (id, user_id, name, description, config, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """
            values = (
                agent_data['id'],
                agent_data['user_id'],
                agent_data['name'],
                agent_data.get('description'),
                json.dumps(agent_data['config']),
                agent_data.get('is_active', True),
                datetime.utcnow(),
                datetime.utcnow()
            )
            
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()
            self.conn.commit()
            
            if result:
                return {
                    'success': True,
                    'agent': self._format_agent(result)
                }
            return {'success': False, 'message': 'Failed to create agent'}
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'message': str(e)}

    def get_user_agents(self, user_id, page=1, per_page=20):
        """Get agents for a specific user"""
        try:
            offset = (page - 1) * per_page
            
            # Get total count
            count_query = "SELECT COUNT(*) FROM agents WHERE user_id = %s"
            self.cursor.execute(count_query, (user_id,))
            total = self.cursor.fetchone()[0]
            
            # Get agents
            query = """
                SELECT * FROM agents 
                WHERE user_id = %s 
                ORDER BY updated_at DESC 
                LIMIT %s OFFSET %s
            """
            self.cursor.execute(query, (user_id, per_page, offset))
            results = self.cursor.fetchall()
            
            agents = [self._format_agent(row) for row in results]
            
            return {
                'success': True,
                'agents': agents,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def get_agent_by_id(self, agent_id, user_id=None):
        """Get agent by ID"""
        try:
            query = "SELECT * FROM agents WHERE id = %s"
            params = [agent_id]
            
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
                
            self.cursor.execute(query, params)
            result = self.cursor.fetchone()
            
            if result:
                return {
                    'success': True,
                    'agent': self._format_agent(result)
                }
            return {'success': False, 'message': 'Agent not found'}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def update_agent(self, agent_id, user_id, update_data):
        """Update an agent"""
        try:
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for key, value in update_data.items():
                if key in ['name', 'description', 'is_active']:
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
                elif key == 'config':
                    set_clauses.append("config = %s")
                    values.append(json.dumps(value))
            
            if not set_clauses:
                return {'success': False, 'message': 'No valid fields to update'}
            
            set_clauses.append("updated_at = %s")
            values.append(datetime.utcnow())
            values.extend([agent_id, user_id])
            
            query = f"""
                UPDATE agents 
                SET {', '.join(set_clauses)}
                WHERE id = %s AND user_id = %s
                RETURNING *
            """
            
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()
            self.conn.commit()
            
            if result:
                return {
                    'success': True,
                    'agent': self._format_agent(result)
                }
            return {'success': False, 'message': 'Agent not found or update failed'}
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'message': str(e)}

    def delete_agent(self, agent_id, user_id):
        """Delete an agent"""
        try:
            query = "DELETE FROM agents WHERE id = %s AND user_id = %s"
            self.cursor.execute(query, (agent_id, user_id))
            
            if self.cursor.rowcount > 0:
                self.conn.commit()
                return {'success': True, 'message': 'Agent deleted successfully'}
            return {'success': False, 'message': 'Agent not found'}
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'message': str(e)}

    def create_execution(self, execution_data):
        """Create a new agent execution"""
        try:
            query = """
                INSERT INTO agent_executions (id, agent_id, status, input_data, started_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
            """
            values = (
                execution_data['id'],
                execution_data['agent_id'],
                'running',
                json.dumps(execution_data['input_data']),
                datetime.utcnow()
            )
            
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()
            self.conn.commit()
            
            if result:
                return {
                    'success': True,
                    'execution': self._format_execution(result)
                }
            return {'success': False, 'message': 'Failed to create execution'}
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'message': str(e)}

    def update_execution(self, execution_id, update_data):
        """Update an execution"""
        try:
            set_clauses = []
            values = []
            
            for key, value in update_data.items():
                if key == 'status':
                    set_clauses.append("status = %s")
                    values.append(value)
                elif key == 'output_data':
                    set_clauses.append("output_data = %s")
                    values.append(json.dumps(value))
                elif key == 'error_message':
                    set_clauses.append("error_message = %s")
                    values.append(value)
                elif key == 'completed_at':
                    set_clauses.append("completed_at = %s")
                    values.append(value)
            
            if not set_clauses:
                return {'success': False, 'message': 'No valid fields to update'}
            
            values.append(execution_id)
            
            query = f"""
                UPDATE agent_executions 
                SET {', '.join(set_clauses)}
                WHERE id = %s
                RETURNING *
            """
            
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()
            self.conn.commit()
            
            if result:
                return {
                    'success': True,
                    'execution': self._format_execution(result)
                }
            return {'success': False, 'message': 'Execution not found'}
            
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'message': str(e)}

    def get_agent_executions(self, agent_id, page=1, per_page=20):
        """Get executions for an agent"""
        try:
            offset = (page - 1) * per_page
            
            # Get total count
            count_query = "SELECT COUNT(*) FROM agent_executions WHERE agent_id = %s"
            self.cursor.execute(count_query, (agent_id,))
            total = self.cursor.fetchone()[0]
            
            # Get executions
            query = """
                SELECT * FROM agent_executions 
                WHERE agent_id = %s 
                ORDER BY started_at DESC 
                LIMIT %s OFFSET %s
            """
            self.cursor.execute(query, (agent_id, per_page, offset))
            results = self.cursor.fetchall()
            
            executions = [self._format_execution(row) for row in results]
            
            return {
                'success': True,
                'executions': executions,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _format_agent(self, row):
        """Format agent data from database row"""
        return {
            'id': row[0],
            'user_id': row[1],
            'name': row[2],
            'description': row[3],
            'config': json.loads(row[4]) if row[4] else {},
            'is_active': row[5],
            'created_at': row[6].isoformat() if row[6] else None,
            'updated_at': row[7].isoformat() if row[7] else None
        }

    def _format_execution(self, row):
        """Format execution data from database row"""
        return {
            'id': row[0],
            'agent_id': row[1],
            'status': row[2],
            'input_data': json.loads(row[3]) if row[3] else {},
            'output_data': json.loads(row[4]) if row[4] else {},
            'error_message': row[5],
            'started_at': row[6].isoformat() if row[6] else None,
            'completed_at': row[7].isoformat() if row[7] else None
        }

# API Endpoints
@router.get("/", response_model=List[Agent])
async def get_agents(
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get user's agents"""
    try:
        user_id = current_user["id"]
        
        with get_db_connection() as conn:
            agent_model_db = AgentModel(conn)
            result = agent_model_db.get_user_agents(user_id, page, per_page)

        if result["success"]:
            return result["agents"]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent: AgentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new agent"""
    try:
        user_id = current_user["id"]
        
        agent_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': agent.name,
            'description': agent.description,
            'config': agent.config,
            'is_active': agent.is_active
        }

        with get_db_connection() as conn:
            agent_model_db = AgentModel(conn)
            result = agent_model_db.create_agent(agent_data)

        if result["success"]:
            return result["agent"]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get agent by ID"""
    try:
        user_id = current_user["id"]

        with get_db_connection() as conn:
            agent_model_db = AgentModel(conn)
            result = agent_model_db.get_agent_by_id(agent_id, user_id)

        if result["success"]:
            return result["agent"]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

@router.put("/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: str,
    agent_update: AgentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an agent"""
    try:
        user_id = current_user["id"]
        update_data = agent_update.dict(exclude_unset=True)

        with get_db_connection() as conn:
            agent_model_db = AgentModel(conn)
            result = agent_model_db.update_agent(agent_id, user_id, update_data)

        if result["success"]:
            return result["agent"]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an agent"""
    try:
        user_id = current_user["id"]

        with get_db_connection() as conn:
            agent_model_db = AgentModel(conn)
            result = agent_model_db.delete_agent(agent_id, user_id)

        if result["success"]:
            return {"message": "Agent deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

@router.post("/{agent_id}/execute", response_model=Execution)
async def execute_agent(
    agent_id: str,
    execution_input: ExecutionInput,
    current_user: dict = Depends(get_current_user)
):
    """Execute an agent"""
    try:
        user_id = current_user["id"]
        
        # First, verify the agent exists and belongs to the user
        with get_db_connection() as conn:
            agent_model_db = AgentModel(conn)
            agent_result = agent_model_db.get_agent_by_id(agent_id, user_id)
            
            if not agent_result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agent not found"
                )
            
            agent = agent_result["agent"]
            if not agent["is_active"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Agent is not active"
                )
            
            # Create execution record
            execution_data = {
                'id': str(uuid.uuid4()),
                'agent_id': agent_id,
                'input_data': execution_input.input_data
            }
            
            execution_result = agent_model_db.create_execution(execution_data)
            
            if not execution_result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=execution_result["message"]
                )
            
            execution = execution_result["execution"]
            
            # TODO: Implement actual agent execution logic here
            # For now, we'll simulate execution
            try:
                # Simulate processing
                output_data = {
                    'result': f"Processed input: {execution_input.input_data}",
                    'agent_config': agent['config'],
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Update execution with results
                update_result = agent_model_db.update_execution(
                    execution['id'], 
                    {
                        'status': 'completed',
                        'output_data': output_data,
                        'completed_at': datetime.utcnow()
                    }
                )
                
                if update_result["success"]:
                    return update_result["execution"]
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to update execution"
                    )
                    
            except Exception as exec_error:
                # Update execution with error
                agent_model_db.update_execution(
                    execution['id'],
                    {
                        'status': 'failed',
                        'error_message': str(exec_error),
                        'completed_at': datetime.utcnow()
                    }
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Agent execution failed: {str(exec_error)}"
                )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

@router.get("/{agent_id}/executions", response_model=List[Execution])
async def get_agent_executions(
    agent_id: str,
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get agent execution history"""
    try:
        user_id = current_user["id"]

        # Verify agent belongs to user
        with get_db_connection() as conn:
            agent_model_db = AgentModel(conn)
            agent_result = agent_model_db.get_agent_by_id(agent_id, user_id)
            
            if not agent_result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agent not found"
                )
            
            result = agent_model_db.get_agent_executions(agent_id, page, per_page)

        if result["success"]:
            return result["executions"]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

