# Universal File System MCP Server Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements_enhanced_rag.txt .
COPY requirements_notion_integration.txt .
COPY requirements_agent_ecosystem.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_minimal.txt

# Copy application code
COPY src/ ./src/
COPY datasets/ ./datasets/
COPY scripts/ ./scripts/
COPY *.py ./
COPY *.md ./

# Create necessary directories
RUN mkdir -p /data /logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV MCP_SERVER_MODE=production

# Expose port for HTTP API (if needed)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command
CMD ["python", "src/server/universal_fs_mcp_server.py"]
