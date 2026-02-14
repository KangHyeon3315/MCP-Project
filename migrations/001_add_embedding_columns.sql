-- Migration: Add embedding columns for semantic search
-- Date: 2026-02-14
-- Description: Add vector embedding columns to domain_document and project_convention tables

-- Add embedding column to domain_document table
ALTER TABLE domain_document
ADD COLUMN embedding vector(384);

-- Add embedding column to project_convention table
ALTER TABLE project_convention
ADD COLUMN embedding vector(384);

-- Create HNSW index for domain_document embedding (cosine similarity)
-- Use WHERE clause to index only rows with embeddings
CREATE INDEX idx_domain_document_embedding
ON domain_document USING hnsw (embedding vector_cosine_ops)
WHERE embedding IS NOT NULL;

-- Create HNSW index for project_convention embedding (cosine similarity)
CREATE INDEX idx_project_convention_embedding
ON project_convention USING hnsw (embedding vector_cosine_ops)
WHERE embedding IS NOT NULL;

-- Comment on columns
COMMENT ON COLUMN domain_document.embedding IS 'Vector embedding for semantic search (384 dimensions)';
COMMENT ON COLUMN project_convention.embedding IS 'Vector embedding for semantic search (384 dimensions)';
