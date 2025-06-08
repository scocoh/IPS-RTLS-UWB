-- Name: create_rules_table.sql
-- Version: 0.1.0
-- Created: 250601
-- Modified: 250601
-- Creator: ParcoAdmin
-- Description: SQL script to create tlk_rules table for TETSE rules
-- Location: /home/parcoadmin/parco_fastapi/app/scripts/create_rules_table.sql
-- Role: Database Schema
-- Status: Active
-- Dependent: FALSE

-- Create tlk_rules table
CREATE TABLE IF NOT EXISTS tlk_rules (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    priority INTEGER NOT NULL DEFAULT 1,
    conditions JSONB NOT NULL,
    actions JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by TEXT DEFAULT CURRENT_USER,
    updated_by TEXT DEFAULT CURRENT_USER
);

-- Index for faster rule lookup
CREATE INDEX idx_tlk_rules_is_enabled_priority ON tlk_rules (is_enabled, priority DESC);

-- Insert sample rule (replaces hard-coded rule)
INSERT INTO tlk_rules (name, is_enabled, priority, conditions, actions)
VALUES (
    'Backyard_Animal_Deterrent',
    TRUE,
    1,
    '{
        "trigger": "AnimalDetected",
        "zone": "Backyard",
        "entity_status": "indoors"
    }'::JSONB,
    '[
        {
            "action_type": "mqtt_publish",
            "parameters": {
                "topic": "homeassistant/switch/deterrent/backyard/set",
                "payload": "ON"
            }
        }
    ]'::JSONB
)
ON CONFLICT (name) DO NOTHING;

-- Comment on table
COMMENT ON TABLE tlk_rules IS 'Stores rules for TETSE to evaluate events and trigger actions';
COMMENT ON COLUMN tlk_rules.conditions IS 'JSONB object specifying conditions (e.g., trigger, zone, entity_status)';
COMMENT ON COLUMN tlk_rules.actions IS 'JSONB array of actions (e.g., mqtt_publish with topic and payload)';