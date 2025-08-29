-- Migration: 002_agent_tables.sql
-- Description: Create tables for Custom Agent Builder
-- Date: 2025-01-15

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Agent executions table
CREATE TABLE IF NOT EXISTS agent_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Agent capabilities table (for defining what each agent can do)
CREATE TABLE IF NOT EXISTS agent_capabilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    capability_type VARCHAR(100) NOT NULL,
    capability_config JSONB,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Agent templates table (predefined agent configurations)
CREATE TABLE IF NOT EXISTS agent_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    template_config JSONB NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    usage_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Agent template ratings table
CREATE TABLE IF NOT EXISTS agent_template_ratings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID NOT NULL REFERENCES agent_templates(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(template_id, user_id)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_agents_user_id ON agents(user_id);
CREATE INDEX IF NOT EXISTS idx_agents_is_active ON agents(is_active);
CREATE INDEX IF NOT EXISTS idx_agent_executions_agent_id ON agent_executions(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON agent_executions(status);
CREATE INDEX IF NOT EXISTS idx_agent_capabilities_agent_id ON agent_capabilities(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_templates_category ON agent_templates(category);
CREATE INDEX IF NOT EXISTS idx_agent_templates_public ON agent_templates(is_public);
CREATE INDEX IF NOT EXISTS idx_agent_templates_rating ON agent_templates(rating);
CREATE INDEX IF NOT EXISTS idx_agent_template_ratings_template_id ON agent_template_ratings(template_id);

-- Update triggers for updated_at columns
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_templates_updated_at BEFORE UPDATE ON agent_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update template rating when a new rating is added
CREATE OR REPLACE FUNCTION update_template_rating()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE agent_templates 
    SET rating = (
        SELECT AVG(rating)::DECIMAL(3,2) 
        FROM agent_template_ratings 
        WHERE template_id = NEW.template_id
    )
    WHERE id = NEW.template_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update template rating
CREATE TRIGGER update_template_rating_trigger
    AFTER INSERT OR UPDATE OR DELETE ON agent_template_ratings
    FOR EACH ROW EXECUTE FUNCTION update_template_rating();

-- Function to increment template usage count
CREATE OR REPLACE FUNCTION increment_template_usage()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE agent_templates 
    SET usage_count = usage_count + 1
    WHERE id = (
        SELECT template_id 
        FROM agents 
        WHERE id = NEW.id 
        AND config ? 'template_id'
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Sample agent templates
INSERT INTO agent_templates (id, name, description, category, template_config, is_public, created_at) VALUES
(uuid_generate_v4(), 'Data Analyzer', 'Analyze and visualize data from various sources', 'Analytics', 
 '{"capabilities": ["data_analysis", "visualization"], "tools": ["pandas", "matplotlib"], "prompt_template": "Analyze the following data and provide insights: {input}"}', 
 true, CURRENT_TIMESTAMP),

(uuid_generate_v4(), 'Content Writer', 'Generate high-quality content for various purposes', 'Content', 
 '{"capabilities": ["text_generation", "content_optimization"], "tools": ["nlp", "seo"], "prompt_template": "Write content about: {topic} with tone: {tone}"}', 
 true, CURRENT_TIMESTAMP),

(uuid_generate_v4(), 'Code Assistant', 'Help with programming tasks and code review', 'Development', 
 '{"capabilities": ["code_generation", "code_review"], "tools": ["ast", "linting"], "prompt_template": "Help with this code: {code} Language: {language}"}', 
 true, CURRENT_TIMESTAMP),

(uuid_generate_v4(), 'Research Assistant', 'Conduct research and summarize findings', 'Research', 
 '{"capabilities": ["web_search", "summarization"], "tools": ["search_api", "nlp"], "prompt_template": "Research topic: {topic} and provide summary"}', 
 true, CURRENT_TIMESTAMP),

(uuid_generate_v4(), 'Task Automator', 'Automate repetitive tasks and workflows', 'Automation', 
 '{"capabilities": ["workflow_automation", "api_integration"], "tools": ["requests", "scheduling"], "prompt_template": "Automate task: {task} with parameters: {params}"}', 
 true, CURRENT_TIMESTAMP);

