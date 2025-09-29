from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from pydantic import BaseModel

router = APIRouter()

security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")

class RAGRequest(BaseModel):
    query: str
    # Add other fields for RAG/Notion logic as needed

@router.post("/rag")
async def rag_endpoint(
    request: RAGRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    RAG endpoint with JWT validation for secure access.
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        # TODO: Integrate existing RAG/Notion logic here
        # For now, stub response
        rag_response = f"RAG/Notion response for query: {request.query} (User: {user_id})"
        
        return {
            "success": True,
            "data": rag_response,
            "user_id": user_id
        }
    
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
