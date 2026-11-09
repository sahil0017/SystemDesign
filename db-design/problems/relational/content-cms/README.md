# Content Management System (CMS) Database Schema Design

## Problem Statement

Design a database schema for a Content Management System that supports articles, categories, tags, authors, revisions, media assets, and comments. The schema must handle versioning with draft/published states, full-text search, rich text content, and a comment moderation workflow.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Articles**: Title, slug, body (rich text), excerpt, status (draft/published/scheduled/archived).
- **Revisions**: Version history with diff support, rollback to previous version.
- **Categories**: Hierarchical categories (parent-child), slugs, descriptions.
- **Tags**: Flat tags with many-to-many relationship to articles.
- **Authors**: Writers, editors, with role-based permissions.
- **Media Assets**: Images, videos, documents with metadata and CDN URLs.
- **Comments**: Nested comments, moderation (pending/approved/flagged/spam).
- **Scheduling**: Publish articles at a scheduled date/time.

### Non-Functional Requirements
- **Full-text search**: Search across titles, bodies, and tags.
- **Versioning**: Unlimited revisions without performance degradation.
- **SEO**: Unique slugs, metadata fields (OG tags, canonical URLs).
- **Scalability**: Support 1M+ articles and 100K daily reads.
- **Comment moderation**: Auto-moderation with spam detection flags.

## Key Design Decisions

- **Revision table**: Separate `article_revisions` for versioning; `articles` stores current state.
- **Slug uniqueness**: Unique constraint on slug; auto-generate from title with suffix for conflicts.
- **Tag denormalization**: Store tag list in articles for listing queries; normalize in junction table.
- **Comment moderation**: Default to `pending` for new users; auto-approve for trusted users.
- **Full-text search**: PostgreSQL `tsvector` for native full-text search.

## Schema Design

### Core Tables

```sql
-- Authors
CREATE TABLE authors (
    author_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    bio TEXT,
    avatar_url TEXT,
    role VARCHAR(50) DEFAULT 'writer', -- 'writer', 'editor', 'admin'
    article_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Categories (hierarchical)
CREATE TABLE categories (
    category_id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id BIGINT,
    sort_order INT DEFAULT 0,
    article_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (parent_id) REFERENCES categories(category_id)
);

-- Articles
CREATE TABLE articles (
    article_id BIGINT PRIMARY KEY,
    author_id BIGINT NOT NULL,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    body TEXT NOT NULL,
    excerpt TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    -- 'draft', 'published', 'scheduled', 'archived'
    current_revision_id BIGINT,
    view_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    featured_image_id BIGINT,
    og_title VARCHAR(500),
    og_description TEXT,
    og_image_url TEXT,
    canonical_url TEXT,
    scheduled_at TIMESTAMP,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    search_vector tsvector, -- Full-text search index
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

-- Article Revisions (versioning)
CREATE TABLE article_revisions (
    revision_id BIGINT PRIMARY KEY,
    article_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    title VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,
    excerpt TEXT,
    change_summary VARCHAR(500), -- "Fixed typo in intro"
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (article_id) REFERENCES articles(article_id),
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

-- Tags
CREATE TABLE tags (
    tag_id BIGINT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    article_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Article Tags (many-to-many)
CREATE TABLE article_tags (
    article_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    PRIMARY KEY (article_id, tag_id),
    FOREIGN KEY (article_id) REFERENCES articles(article_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
);

-- Article Categories (many-to-many)
CREATE TABLE article_categories (
    article_id BIGINT NOT NULL,
    category_id BIGINT NOT NULL,
    PRIMARY KEY (article_id, category_id),
    FOREIGN KEY (article_id) REFERENCES articles(article_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

-- Media Assets
CREATE TABLE media_assets (
    asset_id BIGINT PRIMARY KEY,
    uploaded_by BIGINT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    size_bytes BIGINT NOT NULL,
    cdn_url TEXT NOT NULL,
    thumbnail_url TEXT,
    width INT,
    height INT,
    alt_text VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (uploaded_by) REFERENCES authors(author_id)
);

-- Comments
CREATE TABLE comments (
    comment_id BIGINT PRIMARY KEY,
    article_id BIGINT NOT NULL,
    author_name VARCHAR(100) NOT NULL,
    author_email VARCHAR(255),
    author_url VARCHAR(500),
    parent_comment_id BIGINT,
    body TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    -- 'pending', 'approved', 'flagged', 'spam'
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (article_id) REFERENCES articles(article_id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments(comment_id)
);

-- Comment Moderation Log
CREATE TABLE comment_moderation_log (
    log_id BIGINT PRIMARY KEY,
    comment_id BIGINT NOT NULL,
    moderator_id BIGINT NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (comment_id) REFERENCES comments(comment_id),
    FOREIGN KEY (moderator_id) REFERENCES authors(author_id)
);
```

### Full-Text Search Trigger

```sql
-- Auto-update search_vector on insert/update
CREATE OR REPLACE FUNCTION update_article_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        to_tsvector('english', COALESCE(NEW.title, '')) ||
        to_tsvector('english', COALESCE(NEW.body, '')) ||
        to_tsvector('english', COALESCE(NEW.excerpt, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_search_vector
    BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_article_search_vector();

-- GIN index for full-text search
CREATE INDEX idx_articles_search ON articles USING GIN (search_vector);
```

## Indexes Strategy

| Table | Index | Purpose |
|-------|-------|---------|
| `articles` | Unique on `slug` | SEO-friendly URL lookup |
| `articles` | `(status, published_at DESC)` | Published articles listing |
| `articles` | `(author_id, status, created_at DESC)` | Author's articles |
| `articles` | GIN on `search_vector` | Full-text search |
| `article_revisions` | `(article_id, created_at DESC)` | Revision history |
| `article_tags` | `(tag_id)` | Articles by tag |
| `article_categories` | `(category_id)` | Articles by category |
| `categories` | `(parent_id, sort_order)` | Category hierarchy |
| `comments` | `(article_id, status, created_at DESC)` | Approved comments |
| `comments` | `(parent_comment_id, created_at)` | Reply threads |
| `comments` | `(author_email, created_at DESC)` | Spam detection |
| `media_assets` | `(uploaded_by, created_at DESC)` | User's uploads |
| `tags` | Unique on `slug` | Tag lookup |

## Staff-Level Design Considerations

### Versioning Strategy
- **Full snapshot per revision**: Each revision stores complete title, body, and excerpt.
- **Staff insight**: Don't store diffs — they're expensive to compute and reconstruct. Storage is cheap; store full snapshots. For very large articles (>100KB), consider storing body in S3 and keeping only metadata in the database.

### Full-Text Search
- **PostgreSQL tsvector**: Native full-text search with ranking, highlighting, and thesaurus support.
- **Staff insight**: For < 1M articles, PostgreSQL full-text search is sufficient. For > 1M articles or complex search (fuzzy, synonym, faceted), use Elasticsearch. The trigger keeps the search vector in sync with article updates.

### Slug Uniqueness
- **Auto-generation**: `my-article` → `my-article-1` → `my-article-2` on conflict.
- **Staff insight**: Use a database-level unique constraint, not just application-level checking. Race conditions during concurrent article creation can cause duplicate slugs without a DB constraint.

### Comment Moderation Workflow
- **Pending by default**: New comments from untrusted users go to `pending` status.
- **Staff insight**: Use a reputation system — users whose comments are frequently approved get auto-approve status. Track spam patterns (same IP, same email, keyword matching) and auto-flag suspicious comments. Use Akismet or similar API for spam detection.

### Category Hierarchy
- **Adjacency list**: `parent_id` references same table for tree structure.
- **Staff insight**: For deep hierarchies (>5 levels), use materialized path (`/1/3/7/`) or closure table pattern. Adjacency list requires recursive CTEs for descendant queries, which are slow on deep trees. Materialized path enables prefix-based subtree queries: `WHERE path LIKE '/1/3/%'`.
