-- =====================================================
-- AI Orchestrator - Useful Queries and Functions
-- PostgreSQL Queries for AI Tool Management System
-- Created by: Orion Senior Dev
-- Date: 2025-08-21
-- =====================================================

-- =====================================================
-- COMMON QUERIES FOR AI ORCHESTRATOR
-- =====================================================

-- 1. Get all active tools with their assigned nodes
SELECT 
    t.name as tool_name,
    t.category,
    t.version,
    t.status as tool_status,
    n.node_type,
    n.address,
    n.status as node_status
FROM tools t
LEFT JOIN nodes n ON t.target_node_id = n.node_id
WHERE t.status = 'ENABLED'
ORDER BY t.category, t.name;

-- 2. Find tools by category with tags
SELECT 
    t.name,
    t.description,
    t.category,
    array_agg(tt.tag_name) as tags,
    COUNT(a.artifact_id) as artifact_count
FROM tools t
LEFT JOIN tool_tags tt ON t.tool_id = tt.tool_id
LEFT JOIN artifacts a ON t.tool_id = a.created_by_tool_id
WHERE t.status = 'ENABLED'
GROUP BY t.tool_id, t.name, t.description, t.category
ORDER BY t.category, t.name;

-- 3. Get node health status with tool count
SELECT 
    n.node_id,
    n.node_type,
    n.address,
    n.status,
    COUNT(t.tool_id) as assigned_tools,
    COUNT(CASE WHEN t.status = 'ENABLED' THEN 1 END) as active_tools
FROM nodes n
LEFT JOIN tools t ON n.node_id = t.target_node_id
GROUP BY n.node_id, n.node_type, n.address, n.status
ORDER BY n.node_type, n.status;

-- 4. Find large artifacts by tool
SELECT 
    t.name as tool_name,
    t.category,
    COUNT(a.artifact_id) as total_artifacts,
    SUM(a.size_bytes) as total_size_bytes,
    AVG(a.size_bytes) as avg_size_bytes,
    MAX(a.size_bytes) as max_size_bytes
FROM tools t
LEFT JOIN artifacts a ON t.tool_id = a.created_by_tool_id
WHERE t.status = 'ENABLED'
GROUP BY t.tool_id, t.name, t.category
HAVING COUNT(a.artifact_id) > 0
ORDER BY total_size_bytes DESC;

-- 5. Search tools by JSON schema properties
SELECT 
    t.name,
    t.description,
    t.category,
    t.input_schema,
    t.output_schema
FROM tools t
WHERE t.input_schema ? 'properties'
AND t.input_schema->'properties' ? 'file_path'
AND t.status = 'ENABLED';

-- =====================================================
-- USEFUL FUNCTIONS
-- =====================================================

-- Function to get tools by tag
CREATE OR REPLACE FUNCTION get_tools_by_tag(tag_search VARCHAR)
RETURNS TABLE (
    tool_id UUID,
    tool_name VARCHAR,
    description TEXT,
    category VARCHAR,
    tags TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.tool_id,
        t.name,
        t.description,
        t.category,
        array_agg(tt.tag_name) as tags
    FROM tools t
    JOIN tool_tags tt ON t.tool_id = tt.tool_id
    WHERE tt.tag_name ILIKE '%' || tag_search || '%'
    AND t.status = 'ENABLED'
    GROUP BY t.tool_id, t.name, t.description, t.category
    ORDER BY t.name;
END;
$$ LANGUAGE plpgsql;

-- Function to get node statistics
CREATE OR REPLACE FUNCTION get_node_statistics()
RETURNS TABLE (
    node_id UUID,
    node_type VARCHAR,
    address VARCHAR,
    status VARCHAR,
    total_tools INTEGER,
    active_tools INTEGER,
    total_artifacts BIGINT,
    total_storage_bytes BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        n.node_id,
        n.node_type,
        n.address,
        n.status,
        COUNT(DISTINCT t.tool_id)::INTEGER as total_tools,
        COUNT(DISTINCT CASE WHEN t.status = 'ENABLED' THEN t.tool_id END)::INTEGER as active_tools,
        COUNT(a.artifact_id)::BIGINT as total_artifacts,
        COALESCE(SUM(a.size_bytes), 0)::BIGINT as total_storage_bytes
    FROM nodes n
    LEFT JOIN tools t ON n.node_id = t.target_node_id
    LEFT JOIN artifacts a ON t.tool_id = a.created_by_tool_id
    GROUP BY n.node_id, n.node_type, n.address, n.status
    ORDER BY n.node_type, n.status;
END;
$$ LANGUAGE plpgsql;

-- Function to search tools by schema
CREATE OR REPLACE FUNCTION search_tools_by_schema(
    input_property VARCHAR DEFAULT NULL,
    output_property VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    tool_id UUID,
    tool_name VARCHAR,
    category VARCHAR,
    input_schema JSONB,
    output_schema JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.tool_id,
        t.name,
        t.category,
        t.input_schema,
        t.output_schema
    FROM tools t
    WHERE t.status = 'ENABLED'
    AND (input_property IS NULL OR t.input_schema->'properties' ? input_property)
    AND (output_property IS NULL OR t.output_schema->'properties' ? output_property)
    ORDER BY t.category, t.name;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- MAINTENANCE QUERIES
-- =====================================================

-- Clean up orphaned artifacts (no associated tool)
DELETE FROM artifacts 
WHERE created_by_tool_id IS NULL 
OR created_by_tool_id NOT IN (SELECT tool_id FROM tools);

-- Update tool status based on node status
UPDATE tools 
SET status = 'DISABLED'
WHERE target_node_id IN (
    SELECT node_id FROM nodes WHERE status IN ('INACTIVE', 'MAINTENANCE', 'ERROR')
)
AND status = 'ENABLED';

-- Find tools without assigned nodes
SELECT 
    t.tool_id,
    t.name,
    t.category,
    t.status
FROM tools t
WHERE t.target_node_id IS NULL
AND t.status = 'ENABLED';

-- =====================================================
-- PERFORMANCE MONITORING QUERIES
-- =====================================================

-- Get storage usage by category
SELECT 
    t.category,
    COUNT(a.artifact_id) as artifact_count,
    SUM(a.size_bytes) as total_size_bytes,
    AVG(a.size_bytes) as avg_size_bytes,
    MIN(a.created_at) as oldest_artifact,
    MAX(a.created_at) as newest_artifact
FROM tools t
LEFT JOIN artifacts a ON t.tool_id = a.created_by_tool_id
GROUP BY t.category
ORDER BY total_size_bytes DESC;

-- Get tool usage statistics
SELECT 
    t.name,
    t.category,
    COUNT(a.artifact_id) as usage_count,
    SUM(a.size_bytes) as total_output_size,
    AVG(a.size_bytes) as avg_output_size,
    MAX(a.created_at) as last_used
FROM tools t
LEFT JOIN artifacts a ON t.tool_id = a.created_by_tool_id
GROUP BY t.tool_id, t.name, t.category
ORDER BY usage_count DESC, last_used DESC;

-- =====================================================
-- EXAMPLE USAGE OF FUNCTIONS
-- =====================================================

-- Get all tools with 'analysis' tag
SELECT * FROM get_tools_by_tag('analysis');

-- Get all tools with 'processing' tag
SELECT * FROM get_tools_by_tag('processing');

-- Get node statistics
SELECT * FROM get_node_statistics();

-- Search tools that accept 'file_path' input
SELECT * FROM search_tools_by_schema('file_path');

-- Search tools that return 'metadata' output
SELECT * FROM search_tools_by_schema(NULL, 'metadata');

-- =====================================================
-- BACKUP AND RESTORE QUERIES
-- =====================================================

-- Export tools configuration
SELECT 
    t.tool_id,
    t.name,
    t.description,
    t.category,
    t.version,
    t.status,
    t.input_schema,
    t.output_schema,
    n.node_type,
    n.address,
    array_agg(tt.tag_name) as tags
FROM tools t
LEFT JOIN nodes n ON t.target_node_id = n.node_id
LEFT JOIN tool_tags tt ON t.tool_id = tt.tool_id
GROUP BY t.tool_id, t.name, t.description, t.category, t.version, t.status, 
         t.input_schema, t.output_schema, n.node_type, n.address
ORDER BY t.category, t.name;

-- Export node configuration
SELECT 
    node_id,
    node_type,
    address,
    status,
    created_at,
    updated_at
FROM nodes
ORDER BY node_type, address;

-- =====================================================
-- HEALTH CHECK QUERIES
-- =====================================================

-- Check for data integrity issues
SELECT 'Tools without nodes' as issue, COUNT(*) as count
FROM tools 
WHERE target_node_id IS NULL AND status = 'ENABLED'
UNION ALL
SELECT 'Nodes without tools' as issue, COUNT(*) as count
FROM nodes n
LEFT JOIN tools t ON n.node_id = t.target_node_id
WHERE t.tool_id IS NULL
UNION ALL
SELECT 'Orphaned artifacts' as issue, COUNT(*) as count
FROM artifacts a
LEFT JOIN tools t ON a.created_by_tool_id = t.tool_id
WHERE t.tool_id IS NULL;

-- Check for performance issues
SELECT 
    'Large artifacts' as issue,
    COUNT(*) as count
FROM artifacts 
WHERE size_bytes > 100000000; -- 100MB

-- =====================================================
-- END OF QUERIES FILE
-- =====================================================
