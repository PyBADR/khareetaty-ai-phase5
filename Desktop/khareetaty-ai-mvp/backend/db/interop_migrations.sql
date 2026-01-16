-- Interoperability Database Schema
-- API keys and service account management

-- API Keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    service_name TEXT UNIQUE NOT NULL,
    api_key TEXT UNIQUE NOT NULL,
    permissions TEXT CHECK (permissions IN ('read', 'write', 'admin')) DEFAULT 'read',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_api_keys_key ON api_keys(api_key);
CREATE INDEX idx_api_keys_service ON api_keys(service_name);

-- API Request Log table
CREATE TABLE IF NOT EXISTS api_request_log (
    id SERIAL PRIMARY KEY,
    service_name TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    status INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_api_log_service ON api_request_log(service_name);
CREATE INDEX idx_api_log_timestamp ON api_request_log(timestamp);

-- Webhook Subscriptions table
CREATE TABLE IF NOT EXISTS webhook_subscriptions (
    id SERIAL PRIMARY KEY,
    service_name TEXT NOT NULL,
    webhook_url TEXT NOT NULL,
    event_types TEXT[] NOT NULL,  -- Array of event types to subscribe to
    secret TEXT NOT NULL,  -- Shared secret for signature verification
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_webhooks_service ON webhook_subscriptions(service_name);

-- Webhook Delivery Log table
CREATE TABLE IF NOT EXISTS webhook_delivery_log (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER REFERENCES webhook_subscriptions(id),
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    status INTEGER,  -- HTTP status code
    delivered BOOLEAN DEFAULT FALSE,
    attempts INTEGER DEFAULT 0,
    last_attempt TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_webhook_log_subscription ON webhook_delivery_log(subscription_id);
CREATE INDEX idx_webhook_log_delivered ON webhook_delivery_log(delivered);

-- External System Registry
CREATE TABLE IF NOT EXISTS external_systems (
    id SERIAL PRIMARY KEY,
    system_name TEXT UNIQUE NOT NULL,
    system_type TEXT NOT NULL,  -- moi, fire, municipal, traffic, etc.
    contact_email TEXT,
    contact_phone TEXT,
    base_url TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert default external systems
INSERT INTO external_systems (system_name, system_type, contact_email, active)
VALUES 
    ('MOI Central System', 'moi', 'moi@gov.kw', true),
    ('Fire Department', 'fire', 'fire@gov.kw', true),
    ('Municipal Services', 'municipal', 'municipal@gov.kw', true),
    ('Traffic Department', 'traffic', 'traffic@gov.kw', true),
    ('Civil Defense', 'civil_defense', 'civildefense@gov.kw', true)
ON CONFLICT (system_name) DO NOTHING;

-- Comments
COMMENT ON TABLE api_keys IS 'API keys for external service authentication';
COMMENT ON TABLE api_request_log IS 'Log of all API requests for monitoring and rate limiting';
COMMENT ON TABLE webhook_subscriptions IS 'Webhook subscriptions for external systems';
COMMENT ON TABLE webhook_delivery_log IS 'Log of webhook delivery attempts';
COMMENT ON TABLE external_systems IS 'Registry of external government systems';
