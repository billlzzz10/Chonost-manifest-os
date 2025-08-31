"""
The Forge - Code Interpreter System
ตาม DEVELOPMENT_ROADMAP.md Phase 2.2
"""

import os
import json
import asyncio
import tempfile
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

import docker
from jupyter_client import KernelManager, KernelClient
from jupyter_client.kernelspec import KernelSpecManager

import dramatiq
from dramatiq.brokers.redis import RedisBroker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis broker for background tasks
redis_broker = RedisBroker(host="localhost", port=6379)
dramatiq.set_broker(redis_broker)

class DockerKernelManager:
    """Docker-based kernel management for The Forge"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.kernel_containers: Dict[str, Any] = {}
        self.kernel_specs = {
            'python3': {
                'image': 'jupyter/scipy-notebook:latest',
                'command': ['jupyter', 'kernel', '--kernel=python3'],
                'environment': {
                    'JUPYTER_ENABLE_LAB': 'no',
                    'JUPYTER_TOKEN': '',
                    'JUPYTER_PASSWORD': ''
                }
            }
        }
    
    def create_kernel(self, kernel_id: str, kernel_type: str = 'python3') -> bool:
        """Create a new kernel container"""
        try:
            if kernel_id in self.kernel_containers:
                logger.warning(f"Kernel {kernel_id} already exists")
                return True
            
            spec = self.kernel_specs.get(kernel_type)
            if not spec:
                logger.error(f"Unknown kernel type: {kernel_type}")
                return False
            
            # Create container
            container = self.docker_client.containers.run(
                spec['image'],
                command=spec['command'],
                environment=spec['environment'],
                detach=True,
                remove=True,
                name=f"chonost-kernel-{kernel_id}",
                ports={'8888/tcp': None}  # Random port
            )
            
            self.kernel_containers[kernel_id] = {
                'container': container,
                'type': kernel_type,
                'created_at': datetime.now(),
                'status': 'running'
            }
            
            logger.info(f"Created kernel {kernel_id} with type {kernel_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating kernel {kernel_id}: {e}")
            return False
    
    def destroy_kernel(self, kernel_id: str) -> bool:
        """Destroy a kernel container"""
        try:
            if kernel_id not in self.kernel_containers:
                logger.warning(f"Kernel {kernel_id} not found")
                return True
            
            kernel_info = self.kernel_containers[kernel_id]
            container = kernel_info['container']
            
            # Stop and remove container
            container.stop(timeout=10)
            container.remove()
            
            del self.kernel_containers[kernel_id]
            logger.info(f"Destroyed kernel {kernel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error destroying kernel {kernel_id}: {e}")
            return False
    
    def get_kernel_status(self, kernel_id: str) -> Optional[Dict]:
        """Get kernel status"""
        if kernel_id not in self.kernel_containers:
            return None
        
        kernel_info = self.kernel_containers[kernel_id]
        container = kernel_info['container']
        
        try:
            container.reload()
            return {
                'id': kernel_id,
                'type': kernel_info['type'],
                'status': container.status,
                'created_at': kernel_info['created_at'].isoformat(),
                'ports': container.ports
            }
        except Exception as e:
            logger.error(f"Error getting kernel status: {e}")
            return None
    
    def list_kernels(self) -> List[Dict]:
        """List all active kernels"""
        kernels = []
        for kernel_id, kernel_info in self.kernel_containers.items():
            status = self.get_kernel_status(kernel_id)
            if status:
                kernels.append(status)
        return kernels

class CodeExecutor:
    """Code execution engine for The Forge"""
    
    def __init__(self):
        self.kernel_manager = DockerKernelManager()
        self.execution_history: Dict[str, Dict] = {}
    
    async def execute_code(self, code: str, kernel_id: Optional[str] = None) -> Dict:
        """Execute code in a kernel"""
        try:
            # Generate kernel ID if not provided
            if not kernel_id:
                kernel_id = str(uuid.uuid4())
            
            # Create kernel if it doesn't exist
            if kernel_id not in self.kernel_manager.kernel_containers:
                success = self.kernel_manager.create_kernel(kernel_id)
                if not success:
                    return {
                        'success': False,
                        'error': 'Failed to create kernel',
                        'kernel_id': kernel_id
                    }
            
            # Execute code (simplified - in real implementation, you'd use Jupyter client)
            result = await self._execute_in_kernel(kernel_id, code)
            
            # Store execution history
            execution_id = str(uuid.uuid4())
            self.execution_history[execution_id] = {
                'kernel_id': kernel_id,
                'code': code,
                'result': result,
                'executed_at': datetime.now().isoformat()
            }
            
            return {
                'success': True,
                'execution_id': execution_id,
                'kernel_id': kernel_id,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Error executing code: {e}")
            return {
                'success': False,
                'error': str(e),
                'kernel_id': kernel_id
            }
    
    async def _execute_in_kernel(self, kernel_id: str, code: str) -> Dict:
        """Execute code in a specific kernel (simplified implementation)"""
        # This is a simplified implementation
        # In a real implementation, you'd use Jupyter client to communicate with the kernel
        
        # Simulate execution
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Basic code analysis
        lines = code.split('\n')
        line_count = len(lines)
        char_count = len(code)
        
        # Simple output simulation
        if 'print(' in code:
            output = "Hello from The Forge!\n"
        elif 'import' in code:
            output = "Module imported successfully\n"
        else:
            output = f"Code executed: {line_count} lines, {char_count} characters\n"
        
        return {
            'stdout': output,
            'stderr': '',
            'display_data': [],
            'execution_count': 1,
            'status': 'ok'
        }
    
    def get_execution_history(self, kernel_id: Optional[str] = None) -> List[Dict]:
        """Get execution history"""
        if kernel_id:
            return [
                {**exec_info, 'execution_id': exec_id}
                for exec_id, exec_info in self.execution_history.items()
                if exec_info['kernel_id'] == kernel_id
            ]
        else:
            return [
                {**exec_info, 'execution_id': exec_id}
                for exec_id, exec_info in self.execution_history.items()
            ]

class DataAnalyzer:
    """Data analysis and visualization for The Forge"""
    
    def __init__(self):
        self.analysis_templates = {
            'basic_stats': {
                'description': 'Basic statistical analysis',
                'code_template': '''
import pandas as pd
import numpy as np

# Load data
data = pd.read_csv('{data_file}')

# Basic statistics
print("Dataset shape:", data.shape)
print("\\nColumn names:", list(data.columns))
print("\\nData types:")
print(data.dtypes)
print("\\nBasic statistics:")
print(data.describe())
'''
            },
            'visualization': {
                'description': 'Create basic visualizations',
                'code_template': '''
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Load data
data = pd.read_csv('{data_file}')

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Histogram
axes[0, 0].hist(data['{numeric_column}'], bins=20)
axes[0, 0].set_title('Histogram of {numeric_column}')

# Box plot
axes[0, 1].boxplot(data['{numeric_column}'])
axes[0, 1].set_title('Box Plot of {numeric_column}')

# Correlation heatmap (if multiple numeric columns)
numeric_cols = data.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 1:
    sns.heatmap(data[numeric_cols].corr(), ax=axes[1, 0])
    axes[1, 0].set_title('Correlation Heatmap')

plt.tight_layout()
plt.show()
'''
            }
        }
    
    def get_analysis_templates(self) -> Dict:
        """Get available analysis templates"""
        return self.analysis_templates
    
    def generate_analysis_code(self, template_name: str, **kwargs) -> str:
        """Generate analysis code from template"""
        if template_name not in self.analysis_templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = self.analysis_templates[template_name]['code_template']
        return template.format(**kwargs)

class TheForge:
    """The Forge - Main code interpreter system"""
    
    def __init__(self):
        self.code_executor = CodeExecutor()
        self.data_analyzer = DataAnalyzer()
        self.kernel_manager = DockerKernelManager()
    
    async def execute_code(self, code: str, kernel_id: Optional[str] = None) -> Dict:
        """Execute code"""
        return await self.code_executor.execute_code(code, kernel_id)
    
    def create_kernel(self, kernel_id: str, kernel_type: str = 'python3') -> bool:
        """Create a new kernel"""
        return self.kernel_manager.create_kernel(kernel_id, kernel_type)
    
    def destroy_kernel(self, kernel_id: str) -> bool:
        """Destroy a kernel"""
        return self.kernel_manager.destroy_kernel(kernel_id)
    
    def list_kernels(self) -> List[Dict]:
        """List all kernels"""
        return self.kernel_manager.list_kernels()
    
    def get_kernel_status(self, kernel_id: str) -> Optional[Dict]:
        """Get kernel status"""
        return self.kernel_manager.get_kernel_status(kernel_id)
    
    def get_execution_history(self, kernel_id: Optional[str] = None) -> List[Dict]:
        """Get execution history"""
        return self.code_executor.get_execution_history(kernel_id)
    
    def get_analysis_templates(self) -> Dict:
        """Get analysis templates"""
        return self.data_analyzer.get_analysis_templates()
    
    def generate_analysis_code(self, template_name: str, **kwargs) -> str:
        """Generate analysis code"""
        return self.data_analyzer.generate_analysis_code(template_name, **kwargs)

@dramatiq.actor
def execute_code_async(code: str, kernel_id: str):
    """Background task for code execution"""
    try:
        forge = TheForge()
        result = asyncio.run(forge.execute_code(code, kernel_id))
        logger.info(f"Async code execution completed for kernel {kernel_id}")
        return result
    except Exception as e:
        logger.error(f"Error in async code execution: {e}")
        return {'success': False, 'error': str(e)}

# FastAPI integration
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="The Forge - Code Interpreter API")

class CodeExecutionRequest(BaseModel):
    code: str
    kernel_id: Optional[str] = None

class CodeExecutionResponse(BaseModel):
    success: bool
    execution_id: Optional[str] = None
    kernel_id: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None

@app.post("/forge/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """Execute code in The Forge"""
    forge = TheForge()
    result = await forge.execute_code(request.code, request.kernel_id)
    return CodeExecutionResponse(**result)

@app.get("/forge/kernels")
async def list_kernels():
    """List all active kernels"""
    forge = TheForge()
    return forge.list_kernels()

@app.post("/forge/kernels/{kernel_id}")
async def create_kernel(kernel_id: str, kernel_type: str = "python3"):
    """Create a new kernel"""
    forge = TheForge()
    success = forge.create_kernel(kernel_id, kernel_type)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create kernel")
    return {"success": True, "kernel_id": kernel_id}

@app.delete("/forge/kernels/{kernel_id}")
async def destroy_kernel(kernel_id: str):
    """Destroy a kernel"""
    forge = TheForge()
    success = forge.destroy_kernel(kernel_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to destroy kernel")
    return {"success": True, "kernel_id": kernel_id}

@app.get("/forge/templates")
async def get_analysis_templates():
    """Get available analysis templates"""
    forge = TheForge()
    return forge.get_analysis_templates()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
