-- =====================================================
-- AI Orchestrator Database Schema
-- PostgreSQL Database for AI Tool Management System
-- Created by: Orion Senior Dev
-- Date: 2025-08-21
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. NODES TABLE - Worker Nodes Management
-- =====================================================
CREATE TABLE nodes (
    node_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    node_type VARCHAR(50) NOT NULL CHECK (node_type IN ('TOOL_EXECUTOR', 'OBSERVATION_NODE', 'ANALYSIS_NODE', 'STORAGE_NODE')),
    address VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'INACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'MAINTENANCE', 'ERROR')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 2. TOOLS TABLE - AI Tools Management
-- =====================================================
CREATE TABLE tools (
    tool_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    status VARCHAR(20) NOT NULL DEFAULT 'ENABLED' CHECK (status IN ('ENABLED', 'DISABLED', 'DEPRECATED')),
    input_schema JSONB,
    output_schema JSONB,
    target_node_id UUID REFERENCES nodes(node_id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 3. TOOL_TAGS TABLE - Many-to-Many Relationship
-- =====================================================
CREATE TABLE tool_tags (
    tool_id UUID NOT NULL REFERENCES tools(tool_id) ON DELETE CASCADE,
    tag_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (tool_id, tag_name)
);

-- =====================================================
-- 4. ARTIFACTS TABLE - File Output Metadata
-- =====================================================
CREATE TABLE artifacts (
    artifact_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_name VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    storage_pointer TEXT NOT NULL,
    size_bytes BIGINT NOT NULL CHECK (size_bytes >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by_tool_id UUID REFERENCES tools(tool_id) ON DELETE SET NULL
);

-- =====================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- =====================================================

-- Nodes table indexes
CREATE INDEX idx_nodes_node_type ON nodes(node_type);
CREATE INDEX idx_nodes_status ON nodes(status);
CREATE INDEX idx_nodes_created_at ON nodes(created_at);
CREATE INDEX idx_nodes_updated_at ON nodes(updated_at);

-- Tools table indexes
CREATE INDEX idx_tools_name ON tools(name);
CREATE INDEX idx_tools_category ON tools(category);
CREATE INDEX idx_tools_status ON tools(status);
CREATE INDEX idx_tools_target_node_id ON tools(target_node_id);
CREATE INDEX idx_tools_created_at ON tools(created_at);
CREATE INDEX idx_tools_updated_at ON tools(updated_at);

-- Tool_tags table indexes
CREATE INDEX idx_tool_tags_tag_name ON tool_tags(tag_name);
CREATE INDEX idx_tool_tags_created_at ON tool_tags(created_at);

-- Artifacts table indexes
CREATE INDEX idx_artifacts_file_name ON artifacts(file_name);
CREATE INDEX idx_artifacts_mime_type ON artifacts(mime_type);
CREATE INDEX idx_artifacts_created_at ON artifacts(created_at);
CREATE INDEX idx_artifacts_created_by_tool_id ON artifacts(created_by_tool_id);
CREATE INDEX idx_artifacts_size_bytes ON artifacts(size_bytes);

-- =====================================================
-- JSONB INDEXES FOR SCHEMA QUERIES
-- =====================================================

-- Indexes for JSONB columns in tools table
CREATE INDEX idx_tools_input_schema_gin ON tools USING GIN (input_schema);
CREATE INDEX idx_tools_output_schema_gin ON tools USING GIN (output_schema);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at columns
CREATE TRIGGER update_nodes_updated_at 
    BEFORE UPDATE ON nodes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tools_updated_at 
    BEFORE UPDATE ON tools 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- View for active tools with node information
CREATE VIEW active_tools_with_nodes AS
SELECT 
    t.tool_id,
    t.name,
    t.description,
    t.category,
    t.version,
    t.status as tool_status,
    n.node_id,
    n.node_type,
    n.address,
    n.status as node_status
FROM tools t
LEFT JOIN nodes n ON t.target_node_id = n.node_id
WHERE t.status = 'ENABLED';

-- View for tools with tags
CREATE VIEW tools_with_tags AS
SELECT 
    t.tool_id,
    t.name,
    t.description,
    t.category,
    t.version,
    t.status,
    array_agg(tt.tag_name) as tags
FROM tools t
LEFT JOIN tool_tags tt ON t.tool_id = tt.tool_id
GROUP BY t.tool_id, t.name, t.description, t.category, t.version, t.status;

-- View for artifacts with tool information
CREATE VIEW artifacts_with_tools AS
SELECT 
    a.artifact_id,
    a.file_name,
    a.mime_type,
    a.storage_pointer,
    a.size_bytes,
    a.created_at,
    t.tool_id,
    t.name as tool_name,
    t.category as tool_category
FROM artifacts a
LEFT JOIN tools t ON a.created_by_tool_id = t.tool_id;

-- =====================================================
-- SAMPLE DATA INSERTION
-- =====================================================

-- Insert sample nodes
INSERT INTO nodes (node_type, address, status) VALUES
('TOOL_EXECUTOR', 'http://worker-1:8000', 'ACTIVE'),
('OBSERVATION_NODE', 'http://observer-1:8001', 'ACTIVE'),
('ANALYSIS_NODE', 'http://analyzer-1:8002', 'ACTIVE'),
('STORAGE_NODE', 'http://storage-1:8003', 'ACTIVE');

-- Insert sample tools
INSERT INTO tools (name, description, category, version, status, target_node_id, input_schema, output_schema) VALUES
('file_analyzer', 'Analyze file content and extract metadata', 'ANALYSIS', '1.0.0', 'ENABLED', 
 (SELECT node_id FROM nodes WHERE node_type = 'ANALYSIS_NODE' LIMIT 1),
 '{"type": "object", "properties": {"file_path": {"type": "string"}}}',
 '{"type": "object", "properties": {"metadata": {"type": "object"}}}'),
 
('image_processor', 'Process and transform images', 'PROCESSING', '2.1.0', 'ENABLED',
 (SELECT node_id FROM nodes WHERE node_type = 'TOOL_EXECUTOR' LIMIT 1),
 '{"type": "object", "properties": {"image_url": {"type": "string"}, "operations": {"type": "array"}}}',
 '{"type": "object", "properties": {"processed_url": {"type": "string"}}}'),
 
('data_validator', 'Validate data against schemas', 'VALIDATION', '1.5.0', 'ENABLED',
 (SELECT node_id FROM nodes WHERE node_type = 'TOOL_EXECUTOR' LIMIT 1),
 '{"type": "object", "properties": {"data": {"type": "object"}, "schema": {"type": "object"}}}',
 '{"type": "object", "properties": {"is_valid": {"type": "boolean"}, "errors": {"type": "array"}}}');

-- Insert sample tags
INSERT INTO tool_tags (tool_id, tag_name) VALUES
((SELECT tool_id FROM tools WHERE name = 'file_analyzer'), 'analysis'),
((SELECT tool_id FROM tools WHERE name = 'file_analyzer'), 'metadata'),
((SELECT tool_id FROM tools WHERE name = 'image_processor'), 'processing'),
((SELECT tool_id FROM tools WHERE name = 'image_processor'), 'image'),
((SELECT tool_id FROM tools WHERE name = 'data_validator'), 'validation'),
((SELECT tool_id FROM tools WHERE name = 'data_validator'), 'schema');

-- Insert sample artifacts
INSERT INTO artifacts (file_name, mime_type, storage_pointer, size_bytes, created_by_tool_id) VALUES
('analysis_report.json', 'application/json', 's3://artifacts-bucket/reports/analysis_report.json', 2048,
 (SELECT tool_id FROM tools WHERE name = 'file_analyzer')),
('processed_image.png', 'image/png', 's3://artifacts-bucket/images/processed_image.png', 1024000,
 (SELECT tool_id FROM tools WHERE name = 'image_processor')),
('validation_log.txt', 'text/plain', 's3://artifacts-bucket/logs/validation_log.txt', 512,
 (SELECT tool_id FROM tools WHERE name = 'data_validator'));

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE nodes IS 'Worker nodes for AI tool execution and observation';
COMMENT ON TABLE tools IS 'AI tools available in the orchestrator system';
COMMENT ON TABLE tool_tags IS 'Many-to-many relationship between tools and tags';
COMMENT ON TABLE artifacts IS 'Metadata for output files generated by tools';

COMMENT ON COLUMN nodes.node_id IS 'Unique identifier for each worker node';
COMMENT ON COLUMN nodes.node_type IS 'Type of node: TOOL_EXECUTOR, OBSERVATION_NODE, etc.';
COMMENT ON COLUMN nodes.address IS 'Network address of the worker node';
COMMENT ON COLUMN nodes.status IS 'Current status of the node';

COMMENT ON COLUMN tools.tool_id IS 'Unique identifier for each AI tool';
COMMENT ON COLUMN tools.name IS 'Unique name of the tool';
COMMENT ON COLUMN tools.input_schema IS 'JSON schema defining the input format';
COMMENT ON COLUMN tools.output_schema IS 'JSON schema defining the output format';
COMMENT ON COLUMN tools.target_node_id IS 'Node responsible for executing this tool';

COMMENT ON COLUMN artifacts.artifact_id IS 'Unique identifier for each output artifact';
COMMENT ON COLUMN artifacts.storage_pointer IS 'Pointer to the actual file location (URL, path, etc.)';
COMMENT ON COLUMN artifacts.size_bytes IS 'Size of the artifact in bytes';

-- =====================================================
-- GRANT PERMISSIONS (adjust as needed)
-- =====================================================

-- Grant permissions to application user (replace 'app_user' with actual username)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- =====================================================
-- SCHEMA CREATION COMPLETE
-- =====================================================

-- Display table information
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name IN ('nodes', 'tools', 'tool_tags', 'artifacts')
ORDER BY table_name, ordinal_position;
