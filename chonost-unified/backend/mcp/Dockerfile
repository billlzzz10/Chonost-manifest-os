# Universal File System MCP Server Docker Image - Multi-stage optimized

# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY requirements_enhanced_rag.txt .
COPY requirements_notion_integration.txt .
COPY requirements_agent_ecosystem.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements_minimal.txt

# Production stage
FROM python:3.11-slim AS production

WORKDIR /app

# Install runtime dependencies (minimal)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code (only necessary files)
COPY src/ ./src/
COPY *.py ./
COPY *.md ./

# Create necessary directories
RUN mkdir -p /data /logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV MCP_SERVER_MODE=production

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "src/server/universal_fs_mcp_server.py"]
