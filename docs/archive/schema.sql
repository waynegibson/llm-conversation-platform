CREATE TABLE models (
 id UUID PRIMARY KEY,

 provider VARCHAR(100) NOT NULL,      
 model_name VARCHAR(150) NOT NULL,    
 model_tag VARCHAR(100),              
 model_family VARCHAR(100),           

 parameter_count BIGINT,
 quantization VARCHAR(50),

 context_window INTEGER,

 storage_path TEXT,

 active BOOLEAN DEFAULT TRUE,

 created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE conversations (
  id UUID PRIMARY KEY,
  user_id UUID,
  title VARCHAR(255),
  status VARCHAR(50) DEFAULT 'active',

  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE messages (

 id UUID PRIMARY KEY,

 conversation_id UUID NOT NULL
 REFERENCES conversations(id),

 model_id UUID
 REFERENCES models(id),

 role VARCHAR(20) NOT NULL,   
 -- system/user/assistant/tool

 content TEXT NOT NULL,

 prompt_tokens INTEGER,
 completion_tokens INTEGER,
 total_tokens INTEGER,

 latency_ms INTEGER,

 temperature NUMERIC(4,2),
 top_p NUMERIC(4,2),

 request_payload JSONB,
 response_payload JSONB,

 created_at TIMESTAMPTZ
 DEFAULT now()
);

CREATE INDEX idx_messages_conversation
ON messages(conversation_id);

CREATE INDEX idx_messages_model
ON messages(model_id);

CREATE INDEX idx_messages_created
ON messages(created_at);