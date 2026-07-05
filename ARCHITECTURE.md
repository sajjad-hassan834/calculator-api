# FinanceCalculator.com — Database Architecture & System Design

> **Version:** 2.0.0
> **Status:** Approved Blueprint
> **Stack:** FastAPI + SQLAlchemy 2.0 + Supabase PostgreSQL + Supabase Auth + Supabase Storage
> **Author:** Senior Software Architect

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Naming Conventions & Standards](#2-naming-conventions--standards)
3. [Entity Relationship Diagram](#3-entity-relationship-diagram)
4. [Complete Database Tables](#4-complete-database-tables)
5. [Standard Columns](#5-standard-columns)
6. [Relationships Explained](#6-relationships-explained)
7. [Index Strategy](#7-index-strategy)
8. [Slug Strategy](#8-slug-strategy)
9. [SEO Architecture](#9-seo-architecture)
10. [Media Strategy](#10-media-strategy)
11. [Calculator Engine](#11-calculator-engine)
12. [Audit Logging](#12-audit-logging)
13. [Permissions & RBAC](#13-permissions--rbac)
14. [Scalability & Performance](#14-scalability--performance)
15. [Future-Proofing](#15-future-proofing)

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PUBLIC INTERNET                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        CDN (Cloudflare)                              │
│                     ┌──────────┬──────────┐                         │
│                     │  Static  │  API     │                         │
│                     │  Assets  │  Cache   │                         │
│                     └──────────┴──────────┘                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
┌───────────────────────────────┐  ┌───────────────────────────────┐
│   PUBLIC WEBSITE (React/Vite) │  │  ADMIN DASHBOARD (React/Vite) │
│   - Calculators               │  │  - Content Management         │
│   - Blog                      │  │  - Media Management           │
│   - Guides                    │  │  - User Management            │
│   - SEO Pages                 │  │  - Analytics                  │
│   - Search                    │  │  - Settings                   │
│   - Auth (Supabase)           │  │  - Auth (Supabase)            │
└───────────────┬───────────────┘  └───────────────┬───────────────┘
                │                                  │
                │           JWT (Supabase Auth)     │
                ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       FASTAPI BACKEND                               │
│                                                                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────┐ │
│  │ Public API │  │ Admin API  │  │ Auth APIs  │  │  Middleware   │ │
│  │  /api/v1   │  │  /admin    │  │ (delegated)│  │ Rate Limit,  │ │
│  │            │  │            │  │            │  │ CORS, Audit  │ │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  │ Logging,     │ │
│        │               │               │          │ Perms Check  │ │
│        ▼               ▼               ▼          └──────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                   SERVICE LAYER                             │     │
│  │  Calculator Engine  │  SEO Service  │  Media Service       │     │
│  │  Content Service    │  Cache Svc    │  Analytics Svc       │     │
│  │  Slug Service       │  Search Svc   │  Audit Svc           │     │
│  │  Permission Svc     │  SiteConfig   │  Email Svc           │     │
│  └──────────────────────────┬─────────────────────────────────┘     │
│                             │                                       │
│  ┌──────────────────────────▼─────────────────────────────────┐     │
│  │                    REPOSITORY LAYER                         │     │
│  │                      SQLAlchemy 2.0                        │     │
│  │                   AsyncSession + Unit of Work               │     │
│  └──────────────────────────┬─────────────────────────────────┘     │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     SUPABASE POSTGRESQL                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  public schema                                                │  │
│  │  - All application tables                                    │  │
│  │  - Row Level Security policies                               │  │
│  │  - Indexed for performance                                   │  │
│  │  - Partitioned tables for analytics                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  audit schema                                                 │  │
│  │  - Audit logs (separate schema for isolation)                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  auth schema (Supabase Managed)                               │  │
│  │  - users, identities, sessions                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────┬──────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      SUPABASE STORAGE                               │
│                                                                     │
│  Buckets:                                                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  media   │ │  avatars │ │  uploads │ │  exports │ │  temp    │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│                                                                     │
│  Media URLs stored in PostgreSQL → Files served via CDN            │
└─────────────────────────────────────────────────────────────────────┘
```

### Communication Flow

| Layer | Protocol | Authentication | Notes |
|-------|----------|---------------|-------|
| Browser → React App | HTTPS | — | Static files via CDN |
| React → FastAPI | HTTPS/REST | JWT (Bearer token) | Supabase Auth JWT |
| FastAPI → Supabase PG | PostgreSQL wire | Service role key | Internal only |
| FastAPI → Supabase Storage | HTTPS/REST | Service role key | File operations |
| React → Supabase Auth | HTTPS/REST | Client anon key | Login/signup |
| FastAPI → Supabase Auth | Admin API | Service role key | Admin operations |
| Admin → FastAPI | HTTPS/REST | JWT (elevated) | RBAC enforced |

**Key Design Decisions:**
- FastAPI is the single source of truth for business logic
- Supabase Auth handles authentication; FastAPI handles authorization (RBAC)
- All media metadata in PostgreSQL; binary files in Supabase Storage
- Every request goes through FastAPI (no direct DB access from client)
- Read-heavy endpoints use Redis caching (planned for Phase 3)

---

## 2. Naming Conventions & Standards

### Database Naming

| Convention | Rule | Example |
|------------|------|---------|
| Tables | snake_case, plural | `calculators`, `blog_posts` |
| Columns | snake_case | `created_at`, `is_published` |
| Primary Keys | `id` (UUID) | `id UUID PRIMARY KEY DEFAULT gen_random_uuid()` |
| Foreign Keys | `{table}_id` | `category_id`, `calculator_id` |
| Join Tables | `{table1}_{table2}` | `calculator_categories` |
| Indexes | `idx_{table}_{column}` | `idx_calculators_slug` |
| Unique Constraints | `uq_{table}_{column}` | `uq_calculators_slug` |
| Check Constraints | `ck_{table}_{description}` | `ck_calculators_sort_order_positive` |

### Standard Data Types

| Purpose | PostgreSQL Type | Notes |
|---------|----------------|-------|
| Primary Keys | `UUID` | `gen_random_uuid()` |
| Foreign Keys | `UUID` | Same type as PK |
| Short Strings | `VARCHAR(255)` | Names, titles |
| Long Strings | `TEXT` | Descriptions, content |
| URLs | `TEXT` | No length limit |
| Slugs | `VARCHAR(500)` | Indexed, unique |
| JSON | `JSONB` | Flexible metadata |
| Booleans | `BOOLEAN` | Default `false` |
| Integers | `INTEGER` | IDs, counts, orders |
| Decimals | `NUMERIC(20,10)` | Financial calculations |
| Timestamps | `TIMESTAMPTZ` | Always UTC |
| Money | `NUMERIC(12,2)` | Currency amounts |
| Enums | `VARCHAR(50)` with CHECK | Avoid PG ENUM for migration ease |

### Soft Delete Convention

All content tables use `deleted_at TIMESTAMPTZ`. Queries always filter `WHERE deleted_at IS NULL`.

### Status Convention

All content tables use `status VARCHAR(50)` with CHECK constraint for values: `draft`, `published`, `archived`, `scheduled`.

---

## 3. Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ENTITY RELATIONSHIPS                              │
│                          (1:1, 1:N, N:N Relationships)                     │
└─────────────────────────────────────────────────────────────────────────────┘

AUTH & USERS ────────────────────────────────────────────────────────────────
  users 1─1──► user_profiles
  users 1─N──► user_sessions
  users 1─N──► activity_logs
  users N─N──► roles (via user_roles)
  roles N─N──► permissions (via role_permissions)

CONTENT HIERARCHY ──────────────────────────────────────────────────────────
  categories 1─N──► calculators
  categories 1─N──► blog_posts
  categories 1─N──► guides
  categories 1─N──► categories (self-referential: parent/child)

CALCULATORS ────────────────────────────────────────────────────────────────
  calculators 1─N──► calculator_inputs
  calculators 1─N──► calculator_outputs
  calculators 1─N──► calculator_formulas
  calculators 1─N──► calculator_faqs
  calculators 1─N──► calculator_examples
  calculators 1─N──► calculator_references
  calculators 1─N──► calculator_charts
  calculators 1─N──► calculator_sections
  calculators N─N──► calculators (related_calculators)
  calculators 1─1──► seo_metadata
  calculators 1─N──► media (through calculator_media)
  calculators 1─N──► page_views
  calculators 1─N──► search_history

EDUCATIONAL CONTENT ────────────────────────────────────────────────────────
  guides 1─N──► guide_sections
  guides 1─1──► seo_metadata
  guides N─N──► calculators (through guide_calculators)

  blog_posts 1─N──► blog_sections
  blog_posts 1─1──► seo_metadata
  blog_posts N─N──► calculators (through blog_calculators)

PEOPLE ─────────────────────────────────────────────────────────────────────
  authors 1─N──► calculators
  authors 1─N──► blog_posts
  authors 1─N──► guides
  authors 1─1──► media (avatar)
  reviewers 1─N──► calculators
  reviewers 1─N──► blog_posts
  reviewers 1─N──► guides
  reviewers 1─1──► media (avatar)

SEO ────────────────────────────────────────────────────────────────────────
  seo_metadata 1─1──► calculators
  seo_metadata 1─1──► blog_posts
  seo_metadata 1─1──► guides
  seo_metadata 1─1──► pages (custom pages)
  redirects 1─N (standalone, no FK)
  sitemaps 1─N (standalone)

MEDIA ──────────────────────────────────────────────────────────────────────
  media 1─N──► media_folders (self-referential)
  media 1─N──► calculator_media (join)
  media 1─N──► blog_media (join)
  media 1─N──► guide_media (join)
  media_folders 1─N──► media_folders (self-referential)

SITE MANAGEMENT ────────────────────────────────────────────────────────────
  homepage_sections 1─N (ordered sections)
  navigation_items 1─N──► navigation_items (self-referential: parent/child)
  footer_columns 1─N──► footer_links
  advertisements 1─N (standalone)
  testimonials 1─N (standalone)
  newsletter_subscribers 1─N (standalone)

ANALYTICS ──────────────────────────────────────────────────────────────────
  page_views 1─1 (standalone, high volume)
  search_history 1─1 (standalone, high volume)
  popular_calculators 1─1 (materialized/aggregated)

FUTURE ─────────────────────────────────────────────────────────────────────
  bookmarks N─N──► calculators (user bookmarks)
  saved_calculations 1─N──► calculators
  notifications 1─N──► users
  ai_explanations 1─1──► calculators (future AI content)

AUDIT ──────────────────────────────────────────────────────────────────────
  audit_logs 1─1 (standalone, append-only)
```

---

## 4. Complete Database Tables

### 4.1 AUTHENTICATION & USERS

#### `users`
Managed by Supabase Auth in `auth.users`. We maintain a sync table.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| email | VARCHAR(255) | NO | — | UNIQUE |
| username | VARCHAR(100) | YES | — | UNIQUE |
| email_verified | BOOLEAN | NO | false | |
| phone | VARCHAR(50) | YES | — | |
| is_active | BOOLEAN | NO | true | |
| is_superadmin | BOOLEAN | NO | false | |
| last_login_at | TIMESTAMPTZ | YES | — | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

> Note: `users` table mirrors `auth.users` via Supabase webhook trigger. We never write directly to it.

#### `user_profiles`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| user_id | UUID | NO | — | FK → users.id, UNIQUE |
| display_name | VARCHAR(255) | YES | — | |
| avatar_url | TEXT | YES | — | |
| bio | TEXT | YES | — | |
| job_title | VARCHAR(255) | YES | — | |
| company | VARCHAR(255) | YES | — | |
| website_url | TEXT | YES | — | |
| social_links | JSONB | YES | '{}' | |
| preferences | JSONB | YES | '{}' | |
| timezone | VARCHAR(50) | YES | 'UTC' | |
| locale | VARCHAR(10) | YES | 'en-US' | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

#### `roles`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| name | VARCHAR(100) | NO | — | UNIQUE |
| slug | VARCHAR(100) | NO | — | UNIQUE |
| description | TEXT | YES | — | |
| is_system | BOOLEAN | NO | false | System roles cannot be deleted |
| sort_order | INTEGER | NO | 0 | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

**Seed Roles:** `super_admin`, `admin`, `seo_manager`, `content_writer`, `reviewer`, `editor`, `support`

#### `permissions`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| resource | VARCHAR(100) | NO | — | e.g. 'calculator', 'blog' |
| action | VARCHAR(100) | NO | — | e.g. 'create', 'edit', 'delete', 'publish' |
| description | TEXT | YES | — | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

**UNIQUE(resource, action)**

#### `role_permissions`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| role_id | UUID | NO | — | FK → roles.id |
| permission_id | UUID | NO | — | FK → permissions.id |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

**UNIQUE(role_id, permission_id)**

#### `user_roles`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| user_id | UUID | NO | — | FK → users.id |
| role_id | UUID | NO | — | FK → roles.id |
| granted_by | UUID | YES | — | FK → users.id |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

**UNIQUE(user_id, role_id)**

#### `user_sessions`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| user_id | UUID | NO | — | FK → users.id |
| token_jti | VARCHAR(255) | NO | — | UNIQUE, JWT ID |
| ip_address | INET | YES | — | |
| user_agent | TEXT | YES | — | |
| device_type | VARCHAR(50) | YES | — | |
| location | JSONB | YES | — | |
| is_active | BOOLEAN | NO | true | |
| last_activity_at | TIMESTAMPTZ | YES | — | |
| expires_at | TIMESTAMPTZ | NO | — | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

---

### 4.2 CONTENT — CATEGORIES

#### `categories`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| parent_id | UUID | YES | — | FK → categories.id |
| name | VARCHAR(255) | NO | — | |
| slug | VARCHAR(500) | NO | — | UNIQUE |
| description | TEXT | YES | — | |
| icon | VARCHAR(100) | YES | — | |
| color_hex | VARCHAR(7) | YES | — | e.g. '#FF5733' |
| seo_metadata_id | UUID | YES | — | FK → seo_metadata.id |
| sort_order | INTEGER | NO | 0 | |
| is_active | BOOLEAN | NO | true | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

---

### 4.3 CONTENT — CALCULATORS

#### `calculators`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| category_id | UUID | YES | — | FK → categories.id |
| author_id | UUID | YES | — | FK → authors.id |
| reviewer_id | UUID | YES | — | FK → reviewers.id |
| name | VARCHAR(255) | NO | — | |
| slug | VARCHAR(500) | NO | — | UNIQUE |
| short_description | VARCHAR(500) | YES | — | |
| description | TEXT | YES | — | |
| meta_description | TEXT | YES | — | |
| keywords | TEXT[] | YES | — | PostgreSQL array |
| calculator_type | VARCHAR(100) | NO | — | e.g. 'loan', 'investment', 'mortgage' |
| engine_type | VARCHAR(100) | NO | 'python' | 'python', 'javascript', 'formula' |
| engine_config | JSONB | YES | '{}' | |
| input_schema | JSONB | NO | — | JSON Schema for dynamic inputs |
| output_schema | JSONB | NO | — | JSON Schema for dynamic outputs |
| formula_expression | TEXT | YES | — | For formula-based calculators |
| default_values | JSONB | YES | '{}' | |
| validation_rules | JSONB | YES | '{}' | |
| currency | VARCHAR(3) | YES | 'USD' | |
| country | VARCHAR(2) | YES | 'US' | |
| is_featured | BOOLEAN | NO | false | |
| is_popular | BOOLEAN | NO | false | |
| is_calculator | BOOLEAN | NO | true | false for informational pages |
| is_active | BOOLEAN | NO | true | |
| is_published | BOOLEAN | NO | false | |
| status | VARCHAR(50) | NO | 'draft' | CK: draft/published/archived/scheduled |
| published_at | TIMESTAMPTZ | YES | — | |
| scheduled_at | TIMESTAMPTZ | YES | — | |
| sort_order | INTEGER | NO | 0 | |
| view_count | BIGINT | NO | 0 | |
| seo_metadata_id | UUID | YES | — | FK → seo_metadata.id |
| created_by | UUID | YES | — | FK → users.id |
| updated_by | UUID | YES | — | FK → users.id |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

#### `calculator_inputs`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| calculator_id | UUID | NO | — | FK → calculators.id |
| key | VARCHAR(100) | NO | — | Field identifier |
| label | VARCHAR(255) | NO | — | Display label |
| input_type | VARCHAR(50) | NO | — | text, number, select, range, currency, percentage, date, boolean |
| data_type | VARCHAR(50) | NO | 'number' | number, string, boolean, date |
| placeholder | VARCHAR(255) | YES | — | |
| help_text | TEXT | YES | — | |
| suffix | VARCHAR(50) | YES | — | e.g. 'years', '%', '$' |
| prefix | VARCHAR(50) | YES | — | e.g. '$', '€' |
| default_value | TEXT | YES | — | |
| min_value | NUMERIC(20,10) | YES | — | |
| max_value | NUMERIC(20,10) | YES | — | |
| step_value | NUMERIC(20,10) | YES | — | |
| options | JSONB | YES | — | For select/radio inputs: `[{"label":"Option A","value":"a"}]` |
| validation_rules | JSONB | YES | — | |
| conditional_rules | JSONB | YES | — | Show/hide logic |
| sort_order | INTEGER | NO | 0 | |
| is_required | BOOLEAN | NO | true | |
| is_visible | BOOLEAN | NO | true | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

**UNIQUE(calculator_id, key)**

#### `calculator_outputs`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| calculator_id | UUID | NO | — | FK → calculators.id |
| key | VARCHAR(100) | NO | — | Field identifier |
| label | VARCHAR(255) | NO | — | Display label |
| description | TEXT | YES | — | |
| output_type | VARCHAR(50) | NO | — | number, currency, percentage, string, chart_data |
| data_type | VARCHAR(50) | NO | 'number' | |
| prefix | VARCHAR(50) | YES | — | |
| suffix | VARCHAR(50) | YES | — | |
| format | VARCHAR(50) | YES | — | 'decimal', 'integer', 'percentage', 'currency' |
| decimal_places | INTEGER | NO | 2 | |
| is_primary | BOOLEAN | NO | false | Main output displayed prominently |
| is_visible | BOOLEAN | NO | true | |
| chart_data_mapping | JSONB | YES | — | Mapping for chart rendering |
| sort_order | INTEGER | NO | 0 | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

**UNIQUE(calculator_id, key)**

#### `calculator_formulas`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| calculator_id | UUID | NO | — | FK → calculators.id |
| name | VARCHAR(255) | NO | — | |
| description | TEXT | YES | — | |
| formula_text | TEXT | NO | — | Raw formula with LaTeX/math notation |
| formula_python | TEXT | YES | — | Python expression for evaluation |
| formula_javascript | TEXT | YES | — | JS expression for frontend preview |
| variables | JSONB | YES | — | Input variable definitions |
| sort_order | INTEGER | NO | 0 | |
| is_primary | BOOLEAN | NO | false | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

#### `calculator_faqs`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| calculator_id | UUID | NO | — | FK → calculators.id |
| question | TEXT | NO | — | |
| answer | TEXT | NO | — | Supports rich text/HTML |
| schema_type | VARCHAR(50) | NO | 'FAQPage' | For structured data |
| sort_order | INTEGER | NO | 0 | |
| is_published | BOOLEAN | NO | true | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

#### `calculator_examples`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| calculator_id | UUID | NO | — | FK → calculators.id |
| title | VARCHAR(255) | YES | — | |
| description | TEXT | YES | — | |
| input_values | JSONB | NO | — | Example input values |
| expected_outputs | JSONB | NO | — | Expected results |
| explanation | TEXT | YES | — | Step-by-step explanation |
| sort_order | INTEGER | NO | 0 | |
| is_featured | BOOLEAN | NO | false | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

#### `calculator_references`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| calculator_id | UUID | NO | — | FK → calculators.id |
| title | VARCHAR(255) | NO | — | |
| url | TEXT | YES | — | |
| source_name | VARCHAR(255) | YES | — | |
| citation_text | TEXT | YES | — | |
| sort_order | INTEGER | NO | 0 | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

#### `calculator_charts`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| calculator_id | UUID | NO | — | FK → calculators.id |
| chart_type | VARCHAR(50) | NO | — | line, bar, pie, doughnut, area, scatter |
| title | VARCHAR(255) | YES | — | |
| description | TEXT | YES | — | |
| data_mapping | JSONB | NO | — | Maps calculator outputs to chart axes |
| options | JSONB | YES | '{}' | Chart.js configuration overrides |
| width | INTEGER | YES | — | |
| height | INTEGER | YES | — | |
| is_primary | BOOLEAN | NO | false | |
| sort_order | INTEGER | NO | 0 | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

#### `calculator_sections`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| calculator_id | UUID | NO | — | FK → calculators.id |
| section_type | VARCHAR(50) | NO | — | 'content', 'tips', 'disclaimer', 'education', 'related' |
| title | VARCHAR(255) | NO | — | |
| content | TEXT | YES | — | Rich text/HTML |
| sort_order | INTEGER | NO | 0 | |
| is_published | BOOLEAN | NO | true | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

#### `related_calculators`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| calculator_id | UUID | NO | — | FK → calculators.id |
| related_calculator_id | UUID | NO | — | FK → calculators.id |
| relationship_type | VARCHAR(50) | NO | 'related' | 'related', 'alternative', 'complementary' |
| sort_order | INTEGER | NO | 0 | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

**UNIQUE(calculator_id, related_calculator_id)**
**CK: calculator_id != related_calculator_id**

---

### 4.4 CONTENT — EDUCATIONAL (GUIDES & BLOGS)

#### `guides`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| category_id | UUID | YES | — | FK → categories.id |
| author_id | UUID | YES | — | FK → authors.id |
| reviewer_id | UUID | YES | — | FK → reviewers.id |
| title | VARCHAR(500) | NO | — | |
| slug | VARCHAR(500) | NO | — | UNIQUE |
| subtitle | VARCHAR(500) | YES | — | |
| excerpt | TEXT | YES | — | |
| content | TEXT | YES | — | |
| cover_image_url | TEXT | YES | — | |
| reading_time_minutes | INTEGER | YES | — | |
| difficulty_level | VARCHAR(50) | YES | — | 'beginner', 'intermediate', 'advanced' |
| is_featured | BOOLEAN | NO | false | |
| is_active | BOOLEAN | NO | true | |
| is_published | BOOLEAN | NO | false | |
| status | VARCHAR(50) | NO | 'draft' | CK: draft/published/archived/scheduled |
| published_at | TIMESTAMPTZ | YES | — | |
| scheduled_at | TIMESTAMPTZ | YES | — | |
| sort_order | INTEGER | NO | 0 | |
| seo_metadata_id | UUID | YES | — | FK → seo_metadata.id |
| created_by | UUID | YES | — | FK → users.id |
| updated_by | UUID | YES | — | FK → users.id |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

#### `guide_sections`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| guide_id | UUID | NO | — | FK → guides.id |
| title | VARCHAR(255) | NO | — | |
| content | TEXT | NO | — | Rich text/HTML |
| section_type | VARCHAR(50) | YES | 'text' | 'text', 'image', 'code', 'table', 'cta', 'calculator_embed' |
| anchor_id | VARCHAR(255) | YES | — | For table of contents linking |
| calculator_id | UUID | YES | — | FK → calculators.id (for embed sections) |
| sort_order | INTEGER | NO | 0 | |
| is_published | BOOLEAN | NO | true | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

#### `guide_calculators` (Join Table)

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| guide_id | UUID | NO | — | FK → guides.id |
| calculator_id | UUID | NO | — | FK → calculators.id |
| sort_order | INTEGER | NO | 0 | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

**UNIQUE(guide_id, calculator_id)**

#### `blog_posts`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| category_id | UUID | YES | — | FK → categories.id |
| author_id | UUID | YES | — | FK → authors.id |
| reviewer_id | UUID | YES | — | FK → reviewers.id |
| title | VARCHAR(500) | NO | — | |
| slug | VARCHAR(500) | NO | — | UNIQUE |
| subtitle | VARCHAR(500) | YES | — | |
| excerpt | TEXT | YES | — | |
| content | TEXT | YES | — | |
| cover_image_url | TEXT | YES | — | |
| reading_time_minutes | INTEGER | YES | — | |
| is_featured | BOOLEAN | NO | false | |
| is_pinned | BOOLEAN | NO | false | |
| is_active | BOOLEAN | NO | true | |
| is_published | BOOLEAN | NO | false | |
| status | VARCHAR(50) | NO | 'draft' | CK: draft/published/archived/scheduled |
| published_at | TIMESTAMPTZ | YES | — | |
| scheduled_at | TIMESTAMPTZ | YES | — | |
| seo_metadata_id | UUID | YES | — | FK → seo_metadata.id |
| created_by | UUID | YES | — | FK → users.id |
| updated_by | UUID | YES | — | FK → users.id |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

#### `blog_sections`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| blog_post_id | UUID | NO | — | FK → blog_posts.id |
| title | VARCHAR(255) | NO | — | |
| content | TEXT | NO | — | |
| section_type | VARCHAR(50) | YES | 'text' | 'text', 'image', 'code', 'table', 'cta', 'calculator_embed' |
| anchor_id | VARCHAR(255) | YES | — | |
| calculator_id | UUID | YES | — | FK → calculators.id |
| sort_order | INTEGER | NO | 0 | |
| is_published | BOOLEAN | NO | true | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

#### `blog_calculators` (Join Table)

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| blog_post_id | UUID | NO | — | FK → blog_posts.id |
| calculator_id | UUID | NO | — | FK → calculators.id |
| sort_order | INTEGER | NO | 0 | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

**UNIQUE(blog_post_id, calculator_id)**

---

### 4.5 SEO

#### `seo_metadata`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| meta_title | VARCHAR(70) | YES | — | |
| meta_description | VARCHAR(160) | YES | — | |
| meta_keywords | TEXT[] | YES | — | |
| canonical_url | TEXT | YES | — | |
| og_title | VARCHAR(70) | YES | — | |
| og_description | VARCHAR(160) | YES | — | |
| og_image_url | TEXT | YES | — | |
| og_type | VARCHAR(50) | YES | 'website' | |
| twitter_card | VARCHAR(50) | YES | 'summary_large_image' | |
| twitter_title | VARCHAR(70) | YES | — | |
| twitter_description | VARCHAR(160) | YES | — | |
| twitter_image_url | TEXT | YES | — | |
| json_ld | JSONB | YES | — | Full JSON-LD structured data |
| faq_schema | JSONB | YES | — | FAQPage schema data |
| breadcrumb_schema | JSONB | YES | — | BreadcrumbList schema |
| robots | VARCHAR(255) | YES | 'index, follow' | |
| sitemap_priority | NUMERIC(2,1) | YES | 0.5 | 0.0 to 1.0 |
| sitemap_changefreq | VARCHAR(20) | YES | 'monthly' | always, hourly, daily, weekly, monthly, yearly, never |
| nofollow | BOOLEAN | NO | false | |
| noindex | BOOLEAN | NO | false | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

#### `redirects`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| source_url | TEXT | NO | — | UNIQUE |
| target_url | TEXT | NO | — | |
| redirect_type | INTEGER | NO | 301 | 301, 302 |
| is_active | BOOLEAN | NO | true | |
| hit_count | BIGINT | NO | 0 | |
| last_hit_at | TIMESTAMPTZ | YES | — | |
| created_by | UUID | YES | — | FK → users.id |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

#### `sitemaps`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| name | VARCHAR(255) | NO | — | |
| sitemap_type | VARCHAR(50) | NO | — | 'main', 'calculators', 'blogs', 'guides', 'custom' |
| entries | JSONB | NO | — | Array of URL entries |
| is_generated | BOOLEAN | NO | false | |
| generated_at | TIMESTAMPTZ | YES | — | |
| file_url | TEXT | YES | — | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

#### `custom_pages`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| title | VARCHAR(255) | NO | — | |
| slug | VARCHAR(500) | NO | — | UNIQUE |
| content | TEXT | YES | — | Rich text/HTML |
| template | VARCHAR(100) | YES | 'default' | |
| seo_metadata_id | UUID | YES | — | FK → seo_metadata.id |
| is_published | BOOLEAN | NO | false | |
| status | VARCHAR(50) | NO | 'draft' | |
| created_by | UUID | YES | — | FK → users.id |
| updated_by | UUID | YES | — | FK → users.id |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

---

### 4.6 MEDIA

#### `media_folders`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| parent_id | UUID | YES | — | FK → media_folders.id |
| name | VARCHAR(255) | NO | — | |
| slug | VARCHAR(255) | NO | — | |
| description | TEXT | YES | — | |
| sort_order | INTEGER | NO | 0 | |
| created_by | UUID | YES | — | FK → users.id |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

#### `media`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| folder_id | UUID | YES | — | FK → media_folders.id |
| filename | VARCHAR(255) | NO | — | Original filename |
| file_extension | VARCHAR(20) | NO | — | |
| mime_type | VARCHAR(100) | NO | — | |
| file_size_bytes | BIGINT | NO | — | |
| storage_bucket | VARCHAR(100) | NO | — | Supabase bucket name |
| storage_path | TEXT | NO | — | Full path in storage |
| public_url | TEXT | NO | — | Public CDN URL |
| alt_text | VARCHAR(500) | YES | — | |
| title | VARCHAR(255) | YES | — | |
| caption | TEXT | YES | — | |
| description | TEXT | YES | — | |
| media_type | VARCHAR(50) | NO | — | 'image', 'illustration', 'icon', 'pdf', 'download', 'avatar', 'video' |
| width | INTEGER | YES | — | For images |
| height | INTEGER | YES | — | For images |
| dominant_color | VARCHAR(7) | YES | — | Hex color |
| blur_hash | VARCHAR(255) | YES | — | For lazy loading placeholders |
| is_active | BOOLEAN | NO | true | |
| uploaded_by | UUID | YES | — | FK → users.id |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

#### `calculator_media` (Join)

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| calculator_id | UUID | NO | — | FK → calculators.id |
| media_id | UUID | NO | — | FK → media.id |
| media_type | VARCHAR(50) | NO | 'image' | 'image', 'icon', 'illustration', 'chart_image' |
| sort_order | INTEGER | NO | 0 | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

**UNIQUE(calculator_id, media_id, media_type)**

#### `blog_media` (Join)

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| blog_post_id | UUID | NO | — | FK → blog_posts.id |
| media_id | UUID | NO | — | FK → media.id |
| media_type | VARCHAR(50) | NO | 'image' | |
| sort_order | INTEGER | NO | 0 | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

**UNIQUE(blog_post_id, media_id)**

#### `guide_media` (Join)

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| guide_id | UUID | NO | — | FK → guides.id |
| media_id | UUID | NO | — | FK → media.id |
| media_type | VARCHAR(50) | NO | 'image' | |
| sort_order | INTEGER | NO | 0 | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

**UNIQUE(guide_id, media_id)**

---

### 4.7 SITE MANAGEMENT

#### `homepage_sections`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| section_key | VARCHAR(100) | NO | — | UNIQUE, e.g. 'hero', 'featured_calculators', 'popular_guides' |
| title | VARCHAR(255) | YES | — | |
| subtitle | TEXT | YES | — | |
| content | TEXT | YES | — | |
| section_type | VARCHAR(50) | NO | — | 'hero', 'featured', 'grid', 'list', 'cta', 'custom' |
| config | JSONB | YES | '{}' | Additional configuration |
| is_active | BOOLEAN | NO | true | |
| sort_order | INTEGER | NO | 0 | |
| created_by | UUID | YES | — | FK → users.id |
| updated_by | UUID | YES | — | FK → users.id |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

#### `navigation_items`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| parent_id | UUID | YES | — | FK → navigation_items.id |
| label | VARCHAR(255) | NO | — | |
| url | TEXT | YES | — | |
| page_reference_type | VARCHAR(50) | YES | — | 'calculator', 'blog', 'guide', 'page', 'category', 'external' |
| page_reference_id | UUID | YES | — | Polymorphic reference |
| icon | VARCHAR(100) | YES | — | |
| target | VARCHAR(20) | YES | '_self' | |
| is_active | BOOLEAN | NO | true | |
| is_mega_menu | BOOLEAN | NO | false | |
| mega_menu_config | JSONB | YES | — | Columns, sections for mega menu |
| sort_order | INTEGER | NO | 0 | |
| created_by | UUID | YES | — | FK → users.id |
| updated_by | UUID | YES | — | FK → users.id |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

#### `footer_columns`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| title | VARCHAR(255) | NO | — | |
| sort_order | INTEGER | NO | 0 | |
| is_active | BOOLEAN | NO | true | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

#### `footer_links`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| footer_column_id | UUID | NO | — | FK → footer_columns.id |
| label | VARCHAR(255) | NO | — | |
| url | TEXT | NO | — | |
| sort_order | INTEGER | NO | 0 | |
| is_active | BOOLEAN | NO | true | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

#### `advertisements`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| name | VARCHAR(255) | NO | — | |
| ad_type | VARCHAR(50) | NO | — | 'banner', 'sidebar', 'native', 'popup', 'in_content' |
| placement | VARCHAR(100) | NO | — | 'top', 'bottom', 'sidebar_left', 'sidebar_right', 'in_content', 'between_sections' |
| content | TEXT | YES | — | HTML/JS ad code |
| image_url | TEXT | YES | — | |
| link_url | TEXT | YES | — | |
| target_blank | BOOLEAN | NO | true | |
| is_responsive | BOOLEAN | NO | true | |
| width | INTEGER | YES | — | |
| height | INTEGER | YES | — | |
| start_date | TIMESTAMPTZ | YES | — | |
| end_date | TIMESTAMPTZ | YES | — | |
| max_impressions | BIGINT | YES | — | |
| max_clicks | BIGINT | YES | — | |
| current_impressions | BIGINT | NO | 0 | |
| current_clicks | BIGINT | NO | 0 | |
| is_active | BOOLEAN | NO | true | |
| created_by | UUID | YES | — | FK → users.id |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

#### `testimonials`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| author_name | VARCHAR(255) | NO | — | |
| author_title | VARCHAR(255) | YES | — | |
| author_avatar_url | TEXT | YES | — | |
| content | TEXT | NO | — | |
| rating | INTEGER | YES | — | CK: 1-5 |
| is_featured | BOOLEAN | NO | false | |
| is_active | BOOLEAN | NO | true | |
| sort_order | INTEGER | NO | 0 | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

#### `newsletter_subscribers`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| email | VARCHAR(255) | NO | — | UNIQUE |
| name | VARCHAR(255) | YES | — | |
| is_active | BOOLEAN | NO | true | |
| is_verified | BOOLEAN | NO | false | |
| verified_at | TIMESTAMPTZ | YES | — | |
| subscribed_at | TIMESTAMPTZ | NO | `NOW()` | |
| unsubscribed_at | TIMESTAMPTZ | YES | — | |
| metadata | JSONB | YES | — | Source, interests, etc. |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

---

### 4.8 PEOPLE

#### `authors`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| user_id | UUID | YES | — | FK → users.id, UNIQUE |
| name | VARCHAR(255) | NO | — | |
| slug | VARCHAR(500) | NO | — | UNIQUE |
| email | VARCHAR(255) | YES | — | |
| bio | TEXT | YES | — | |
| avatar_media_id | UUID | YES | — | FK → media.id |
| website_url | TEXT | YES | — | |
| social_links | JSONB | YES | '{}' | |
| expertise_areas | TEXT[] | YES | — | |
| is_active | BOOLEAN | NO | true | |
| sort_order | INTEGER | NO | 0 | |
| created_by | UUID | YES | — | FK → users.id |
| updated_by | UUID | YES | — | FK → users.id |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

#### `reviewers`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| user_id | UUID | YES | — | FK → users.id, UNIQUE |
| name | VARCHAR(255) | NO | — | |
| slug | VARCHAR(500) | NO | — | UNIQUE |
| email | VARCHAR(255) | YES | — | |
| title | VARCHAR(255) | YES | — | e.g. 'Certified Financial Analyst' |
| bio | TEXT | YES | — | |
| avatar_media_id | UUID | YES | — | FK → media.id |
| website_url | TEXT | YES | — | |
| social_links | JSONB | YES | '{}' | |
| credentials | TEXT[] | YES | — | e.g. ['CFA', 'MBA'] |
| is_active | BOOLEAN | NO | true | |
| sort_order | INTEGER | NO | 0 | |
| created_by | UUID | YES | — | FK → users.id |
| updated_by | UUID | YES | — | FK → users.id |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

---

### 4.9 SETTINGS

#### `site_settings`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| key | VARCHAR(100) | NO | — | UNIQUE |
| value | JSONB | NO | — | |
| description | TEXT | YES | — | |
| group | VARCHAR(100) | YES | 'general' | 'general', 'seo', 'social', 'analytics', 'email', 'features' |
| is_public | BOOLEAN | NO | false | Exposed to public API |
| created_by | UUID | YES | — | FK → users.id |
| updated_by | UUID | YES | — | FK → users.id |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

---

### 4.10 ANALYTICS

#### `page_views`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | BIGSERIAL | NO | — | PK |
| page_type | VARCHAR(50) | NO | — | 'calculator', 'blog', 'guide', 'home', 'page' |
| page_id | UUID | YES | — | Polymorphic reference |
| url | TEXT | NO | — | |
| referrer | TEXT | YES | — | |
| session_id | VARCHAR(255) | YES | — | |
| user_id | UUID | YES | — | FK → users.id (nullable for anonymous) |
| ip_address | INET | YES | — | Anonymized/truncated |
| user_agent | TEXT | YES | — | |
| device_type | VARCHAR(50) | YES | — | 'desktop', 'tablet', 'mobile' |
| browser | VARCHAR(100) | YES | — | |
| os | VARCHAR(100) | YES | — | |
| country | VARCHAR(2) | YES | — | |
| time_on_page | INTEGER | YES | — | Seconds |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

**Indexes:** `(page_type, page_id)`, `(created_at)`, `(session_id)`

#### `search_history`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | BIGSERIAL | NO | — | PK |
| query | TEXT | NO | — | |
| normalized_query | TEXT | YES | — | Lowercased, trimmed |
| result_count | INTEGER | NO | 0 | |
| user_id | UUID | YES | — | FK → users.id |
| session_id | VARCHAR(255) | YES | — | |
| clicked_result | UUID | YES | — | Calculator/blog/guide ID |
| clicked_result_type | VARCHAR(50) | YES | — | |
| ip_address | INET | YES | — | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

#### `popular_calculators` (Materialized View / Aggregated Table)

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| calculator_id | UUID | NO | — | FK → calculators.id, UNIQUE |
| view_count_24h | BIGINT | NO | 0 | |
| view_count_7d | BIGINT | NO | 0 | |
| view_count_30d | BIGINT | NO | 0 | |
| view_count_all | BIGINT | NO | 0 | |
| unique_visitors_30d | BIGINT | NO | 0 | |
| avg_time_on_page | NUMERIC(10,2) | YES | — | |
| rank_24h | INTEGER | YES | — | |
| rank_7d | INTEGER | YES | — | |
| rank_30d | INTEGER | YES | — | |
| last_calculated_at | TIMESTAMPTZ | NO | `NOW()` | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

---

### 4.11 AUDIT

#### `audit_logs`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | BIGSERIAL | NO | — | PK |
| user_id | UUID | YES | — | FK → users.id |
| action | VARCHAR(100) | NO | — | 'create', 'update', 'delete', 'publish', 'unpublish', 'login', 'logout', 'upload', 'setting_change', 'permission_change' |
| resource_type | VARCHAR(100) | NO | — | 'calculator', 'blog', 'guide', 'media', 'user', 'role', 'setting', 'advertisement' |
| resource_id | UUID | YES | — | |
| details | JSONB | YES | — | |
| changes | JSONB | YES | — | Before/after for updates: `{"before": {...}, "after": {...}}` |
| ip_address | INET | YES | — | |
| user_agent | TEXT | YES | — | |
| severity | VARCHAR(20) | NO | 'info' | 'info', 'warning', 'error', 'critical' |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

---

### 4.12 FUTURE TABLES

#### `bookmarks`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| user_id | UUID | NO | — | FK → users.id |
| calculator_id | UUID | NO | — | FK → calculators.id |
| notes | TEXT | YES | — | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

**UNIQUE(user_id, calculator_id)**

#### `saved_calculations`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| user_id | UUID | NO | — | FK → users.id |
| calculator_id | UUID | NO | — | FK → calculators.id |
| name | VARCHAR(255) | YES | — | |
| input_values | JSONB | NO | — | |
| output_values | JSONB | NO | — | |
| share_token | VARCHAR(100) | YES | — | UNIQUE, for sharing |
| is_shared | BOOLEAN | NO | false | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |
| deleted_at | TIMESTAMPTZ | YES | — | |

#### `notifications`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| user_id | UUID | NO | — | FK → users.id |
| type | VARCHAR(50) | NO | — | 'content_approved', 'content_rejected', 'review_requested', 'system' |
| title | VARCHAR(255) | NO | — | |
| message | TEXT | YES | — | |
| data | JSONB | YES | — | |
| is_read | BOOLEAN | NO | false | |
| read_at | TIMESTAMPTZ | YES | — | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |

#### `ai_explanations`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | UUID | NO | `gen_random_uuid()` | PK |
| calculator_id | UUID | NO | — | FK → calculators.id |
| explanation_type | VARCHAR(50) | NO | — | 'simple', 'detailed', 'technical', 'step_by_step' |
| content | TEXT | NO | — | |
| generated_by | VARCHAR(50) | NO | — | 'openai', 'claude', 'custom' |
| model_version | VARCHAR(100) | YES | — | |
| prompt_tokens | INTEGER | YES | — | |
| completion_tokens | INTEGER | YES | — | |
| is_active | BOOLEAN | NO | true | |
| created_at | TIMESTAMPTZ | NO | `NOW()` | |
| updated_at | TIMESTAMPTZ | NO | `NOW()` | |

---

## 5. Standard Columns

Every content table follows this standard column convention:

```sql
-- Standard columns for every content table:
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
slug            VARCHAR(500) NOT NULL UNIQUE  -- (where applicable)
created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
deleted_at      TIMESTAMPTZ                   -- Soft delete
created_by      UUID REFERENCES users(id)     -- Who created
updated_by      UUID REFERENCES users(id)     -- Who last updated
status          VARCHAR(50) NOT NULL DEFAULT 'draft'  -- draft/published/archived
is_active       BOOLEAN NOT NULL DEFAULT true
is_published    BOOLEAN NOT NULL DEFAULT false
sort_order      INTEGER NOT NULL DEFAULT 0
```

### Tables using ALL standard columns:
- `calculators` — Full standard
- `guides` — Full standard
- `blog_posts` — Full standard
- `categories` — No `created_by`/`updated_by`
- `custom_pages` — Full standard
- `advertisements` — Full standard
- `homepage_sections` — Full standard
- `navigation_items` — Full standard
- `media` — No `slug`, has `status` via `is_active`

### Tables using PARTIAL standard columns:
- Join tables: `id`, `created_at` only
- Child tables (inputs, outputs, etc.): `id`, `created_at`, `updated_at`
- Analytics tables: `id`, `created_at`
- Audit tables: `id`, `created_at`

### Audit Fields Convention

| Field | Purpose | Applied To |
|-------|---------|-----------|
| `created_at` | Record creation timestamp | ALL tables |
| `updated_at` | Last modification | ALL mutable tables |
| `deleted_at` | Soft delete flag | ALL content tables |
| `created_by` | User who created | Content, settings, navigation |
| `updated_by` | User who last modified | Content, settings, navigation |

---

## 6. Relationships Explained

### 6.1 Category Hierarchy (Self-Referential)

```
categories
  │
  ├── parent_id → categories.id (1:N)
  │
  ├── 1:N calculators
  ├── 1:N guides
  ├── 1:N blog_posts
  └── 1:N child categories
```

Categories form a tree. A category can have one parent (or be root) and many children. This enables unlimited depth for SEO content organization.

### 6.2 Calculator → All Sub-Entities

```
calculators (1) ──→ calculator_inputs (N)
               ──→ calculator_outputs (N)
               ──→ calculator_formulas (N)
               ──→ calculator_faqs (N)
               ──→ calculator_examples (N)
               ──→ calculator_references (N)
               ──→ calculator_charts (N)
               ──→ calculator_sections (N)
               ──→ seo_metadata (1:1)
               ──→ media (N:N via calculator_media)
               ──→ authors (N:1)
               ──→ reviewers (N:1)
```

Every calculator owns its inputs, outputs, formulas, FAQs, examples, references, charts, and educational sections. These are all **exclusive** to the calculator (cascade delete).

### 6.3 Polymorphic References

Several tables use polymorphic references where a single column references multiple possible tables:

| Table | Column | References |
|-------|--------|-----------|
| `page_views` | `page_type` + `page_id` | calculators, blog_posts, guides, custom_pages |
| `seo_metadata` | Referenced via FK columns | calculators, blog_posts, guides, custom_pages, categories |
| `navigation_items` | `page_reference_type` + `page_reference_id` | calculators, blog_posts, guides, categories, custom_pages |

**Implementation Strategy:** Use separate nullable FK columns rather than a single polymorphic FK. For example:

```sql
-- In seo_metadata, we DON'T do polymorphic. Instead:
-- calculators.seo_metadata_id → seo_metadata.id
-- blog_posts.seo_metadata_id → seo_metadata.id
-- guides.seo_metadata_id → seo_metadata.id
```

This provides referential integrity via actual foreign keys.

### 6.4 N:N Relationships (Join Tables)

| Join Table | Left | Right | Purpose |
|-----------|------|-------|---------|
| `related_calculators` | calculators | calculators | Related/alternative calculators |
| `guide_calculators` | guides | calculators | Calculators referenced in guides |
| `blog_calculators` | blog_posts | calculators | Calculators referenced in blogs |
| `calculator_media` | calculators | media | Images/icons for calculators |
| `blog_media` | blog_posts | media | Images for blog posts |
| `guide_media` | guides | media | Images for guides |
| `role_permissions` | roles | permissions | What each role can do |
| `user_roles` | users | roles | What roles each user has |

### 6.5 People → Content

```
authors (1) ──→ calculators (N)
          ──→ guides (N)
          ──→ blog_posts (N)
          ──→ media (1:1 for avatar)

reviewers (1) ──→ calculators (N)
           ──→ guides (N)
           ──→ blog_posts (N)
           ──→ media (1:1 for avatar)
```

Authors and reviewers are separate entities from system users, though optionally linked via `user_id`. This allows attributing content to people who may not have system accounts (e.g., guest authors).

### 6.6 SEO → Content (1:1)

```
seo_metadata (1) ←── calculators (1)
                 ←── blog_posts (1)
                 ←── guides (1)
                 ←── custom_pages (1)
                 ←── categories (1)
```

Each SEO-able entity has exactly one `seo_metadata` record (nullable). This avoids duplicating SEO columns across every content table and allows centralized SEO management.

### 6.7 Navigation Tree (Self-Referential)

```
navigation_items
  ├── parent_id → navigation_items.id
  ├── level_1_item
  │   ├── level_2_item
  │   │   └── level_3_item
  │   └── level_2_item
  └── level_1_item
```

Unlimited depth. Each item can reference any content type via `page_reference_type` + `page_reference_id`, or use a custom `url` for external links.

### 6.8 Media Folder Tree (Self-Referential)

```
media_folders
  ├── parent_id → media_folders.id
  ├── folder_1
  │   ├── subfolder_1
  │   └── subfolder_2
  └── folder_2
```

---

## 7. Index Strategy

### 7.1 Core Indexes

```sql
-- SLUG LOOKUPS (Critical for SEO performance)
CREATE UNIQUE INDEX idx_calculators_slug ON calculators(slug) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX idx_blog_posts_slug ON blog_posts(slug) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX idx_guides_slug ON guides(slug) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX idx_categories_slug ON categories(slug) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX idx_authors_slug ON authors(slug) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX idx_reviewers_slug ON reviewers(slug) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX idx_custom_pages_slug ON custom_pages(slug) WHERE deleted_at IS NULL;

-- FOREIGN KEY INDEXES
CREATE INDEX idx_calculators_category_id ON calculators(category_id);
CREATE INDEX idx_calculators_author_id ON calculators(author_id);
CREATE INDEX idx_calculators_reviewer_id ON calculators(reviewer_id);
CREATE INDEX idx_blog_posts_category_id ON blog_posts(category_id);
CREATE INDEX idx_blog_posts_author_id ON blog_posts(author_id);
CREATE INDEX idx_blog_posts_reviewer_id ON blog_posts(reviewer_id);
CREATE INDEX idx_guides_category_id ON guides(category_id);
CREATE INDEX idx_guides_author_id ON guides(author_id);
CREATE INDEX idx_guides_reviewer_id ON guides(reviewer_id);
CREATE INDEX idx_calculator_inputs_calculator_id ON calculator_inputs(calculator_id);
CREATE INDEX idx_calculator_outputs_calculator_id ON calculator_outputs(calculator_id);
CREATE INDEX idx_calculator_faqs_calculator_id ON calculator_faqs(calculator_id);
CREATE INDEX idx_guide_sections_guide_id ON guide_sections(guide_id);
CREATE INDEX idx_blog_sections_blog_post_id ON blog_sections(blog_post_id);

-- STATUS/PUBLISHED FILTERS
CREATE INDEX idx_calculators_status ON calculators(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_blog_posts_status ON blog_posts(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_guides_status ON guides(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_calculators_is_published ON calculators(is_published) WHERE is_published = true AND deleted_at IS NULL;
CREATE INDEX idx_blog_posts_is_published ON blog_posts(is_published) WHERE is_published = true AND deleted_at IS NULL;

-- DATE-BASED QUERIES
CREATE INDEX idx_calculators_published_at ON calculators(published_at DESC) WHERE is_published = true;
CREATE INDEX idx_blog_posts_published_at ON blog_posts(published_at DESC) WHERE is_published = true;
CREATE INDEX idx_guides_published_at ON guides(published_at DESC) WHERE is_published = true;
CREATE INDEX idx_page_views_created_at ON page_views(created_at DESC);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- SORT ORDER
CREATE INDEX idx_calculators_sort_order ON calculators(sort_order);
CREATE INDEX idx_categories_sort_order ON categories(sort_order, parent_id);

-- FEATURED/POPULAR
CREATE INDEX idx_calculators_is_featured ON calculators(is_featured) WHERE is_featured = true AND is_published = true;
CREATE INDEX idx_calculators_is_popular ON calculators(is_popular) WHERE is_popular = true AND is_published = true;

-- SEO LOOKUPS
CREATE INDEX idx_seo_metadata_meta_title ON seo_metadata(meta_title);

-- SEARCH (Full-text search)
CREATE INDEX idx_calculators_fts ON calculators USING GIN(
    to_tsvector('english', coalesce(name, '') || ' ' || coalesce(short_description, '') || ' ' || coalesce(description, ''))
) WHERE deleted_at IS NULL AND is_published = true;

CREATE INDEX idx_blog_posts_fts ON blog_posts USING GIN(
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(excerpt, '') || ' ' || coalesce(content, ''))
) WHERE deleted_at IS NULL AND is_published = true;

CREATE INDEX idx_guides_fts ON guides USING GIN(
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(excerpt, '') || ' ' || coalesce(content, ''))
) WHERE deleted_at IS NULL AND is_published = true;

-- UNIQUE CONSTRAINTS (instead of separate unique indexes)
-- Already defined in table DDL as UNIQUE constraints

-- COMPOSITE INDEXES
CREATE INDEX idx_calculators_category_published ON calculators(category_id, is_published) WHERE is_published = true;
CREATE INDEX idx_navigation_items_parent ON navigation_items(parent_id, sort_order) WHERE is_active = true;
CREATE INDEX idx_page_views_page ON page_views(page_type, page_id, created_at DESC);
CREATE INDEX idx_search_history_query ON search_history(normalized_query, created_at DESC);
CREATE INDEX idx_media_folder ON media(folder_id) WHERE deleted_at IS NULL;

-- AUDIT LOG LOOKUPS
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action, created_at DESC);

-- POLYMORPHIC LOOKUPS
CREATE INDEX idx_popular_calculators_rank ON popular_calculators(rank_30d) WHERE rank_30d IS NOT NULL;
```

### 7.2 Partial Index Strategy

All slug and unique indexes use `WHERE deleted_at IS NULL` to ensure uniqueness only among non-deleted records. This allows reuse of slugs after soft delete without conflicts.

### 7.3 Full-Text Search Strategy

PostgreSQL's built-in full-text search (`tsvector`/`tsquery`) handles initial search needs. For Phase 3, a dedicated search engine (MeiliSearch/Typesense) can be added. The GIN indexes support ranked search results.

---

## 8. Slug Strategy

### 8.1 Slug Generation Rules

| Rule | Description | Example |
|------|-------------|---------|
| Lowercase | All slugs are lowercase | `mortgage-calculator` |
| Hyphen-separated | Words separated by hyphens | `compound-interest-calculator` |
| No special chars | Only a-z, 0-9, hyphens | `loan-payment-calculator-2024` |
| Max length | 500 characters | |
| No trailing hyphens | Strip trailing hyphens | `calculator` not `calculator-` |
| No consecutive hyphens | Collapse multiple hyphens to one | `a-b-c` not `a--b--c` |
| Start with letter | Slugs must start with a letter | `calc-123` not `123-calc` |

### 8.2 Slug Uniqueness Scope

- **Global uniqueness:** calculators, blog_posts, guides, custom_pages, categories
- **Per-type uniqueness:** authors, reviewers, media_folders
- **No scope prefix needed** since slugs are globally unique across content types

### 8.3 Slug Conflict Resolution

```
Input: "Mortgage Calculator"
Slug:  "mortgage-calculator"

If "mortgage-calculator" exists:
  → "mortgage-calculator-1"
  → "mortgage-calculator-2"
```

### 8.4 Slug Service Logic

```python
# Pseudocode for slug service:
def generate_slug(text: str, model: Type, parent_id: UUID = None) -> str:
    base = slugify(text)
    slug = base
    counter = 1
    
    while model.query.filter_by(slug=slug, deleted_at=None).first():
        slug = f"{base}-{counter}"
        counter += 1
    
    return slug
```

### 8.5 Content Type Slug Patterns

| Content Type | Slug Pattern | Example |
|-------------|-------------|---------|
| Calculator | `{name}-calculator` | `mortgage-calculator` |
| Blog Post | `{title}` | `how-to-save-for-retirement` |
| Guide | `{title}-guide` | `investing-for-beginners-guide` |
| Category | `{name}` | `personal-finance` |
| Author | `{name}` | `john-doe` |
| Reviewer | `{name}` | `jane-smith` |
| Custom Page | `{title}` | `about-us` |
| Media Folder | `{name}` | `calculator-screenshots` |

---

## 9. SEO Architecture

### 9.1 Centralized SEO Metadata

Every SEO-able content type has a `seo_metadata_id` foreign key pointing to the `seo_metadata` table. This 1:1 relationship ensures:

1. Consistent SEO structure across all content types
2. Centralized SEO management from admin
3. Easy bulk SEO operations
4. Reusable SEO patterns

### 9.2 SEO Per Content Type

| Content Type | SEO Available | JSON-LD Schema Type |
|-------------|--------------|-------------------|
| Calculator | Yes | `SoftwareApplication` (with `applicationCategory: "FinanceApplication"`) |
| Blog Post | Yes | `Article` or `BlogPosting` |
| Guide | Yes | `Article` or `TechArticle` |
| Custom Page | Yes | `WebPage` |
| Category | Yes | `CollectionPage` |
| Homepage | Via settings | `WebSite` |

### 9.3 Schema.org Structured Data

Each content type generates specific JSON-LD:

**Calculator:**
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Mortgage Calculator",
  "description": "Calculate your monthly mortgage payments",
  "applicationCategory": "FinanceApplication",
  "operatingSystem": "All",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  }
}
```

**Blog Post:**
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "How to Save for Retirement",
  "author": {
    "@type": "Person",
    "name": "John Doe"
  },
  "datePublished": "2024-01-15",
  "description": "Learn the best strategies..."
}
```

### 9.4 FAQ Schema

The `calculator_faqs` table directly feeds `FAQPage` schema:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "How is mortgage interest calculated?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Mortgage interest is calculated using..."
    }
  }]
}
```

### 9.5 Breadcrumb Schema

Generated dynamically from category hierarchy and content type:

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://.../" },
    {"@type": "ListItem", "position": 2, "name": "Mortgage", "item": "https://.../mortgage" },
    {"@type": "ListItem", "position": 3, "name": "Mortgage Calculator", "item": "https://.../mortgage-calculator" }
  ]
}
```

### 9.6 Sitemap Strategy

Multiple sitemaps generated automatically:

| Sitemap | Contents | Frequency |
|---------|----------|-----------|
| `sitemap.xml` | Index of all sitemaps | Daily |
| `sitemap-calculators.xml` | All published calculators | Daily |
| `sitemap-blogs.xml` | All published blog posts | Daily |
| `sitemap-guides.xml` | All published guides | Weekly |
| `sitemap-categories.xml` | All active categories | Weekly |
| `sitemap-pages.xml` | All custom pages | Monthly |

### 9.7 Robots & Canonical

- **Canonical URLs:** Auto-generated from slug, stored in `seo_metadata.canonical_url`
- **Robots meta:** Customizable per page, defaults to `index, follow`
- **noindex/nofollow:** Toggle per page for thin content or duplicate pages
- **Hreflang:** Future internationalization support via `seo_metadata` JSONB field

---

## 10. Media Strategy

### 10.1 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MEDIA ARCHITECTURE                             │
│                                                                     │
│  User Upload                                                         │
│       │                                                              │
│       ▼                                                              │
│  FastAPI Media Service                                                │
│       │                                                              │
│       ├──▶ Validate file (type, size, dimensions)                   │
│       ├──▶ Generate unique filename                                 │
│       ├──▶ Upload to Supabase Storage                               │
│       ├──▶ Create record in media table                             │
│       └──▶ Return public_url                                        │
│                                                                     │
│  Storage Structure (Supabase Storage):                              │
│  media/{year}/{month}/{day}/{uuid}-{filename}.{ext}                 │
│  avatars/{year}/{month}/{day}/{uuid}-{filename}.{ext}              │
│                                                                     │
│  CDN: https://cdn.financecalculator.com/media/...                   │
└─────────────────────────────────────────────────────────────────────┘
```

### 10.2 Storage Buckets

| Bucket | Purpose | Public | Allowed Types |
|--------|---------|--------|---------------|
| `media` | Images, PDFs, downloads | Yes | All media types |
| `avatars` | Author/reviewer photos | Yes | Images only |
| `uploads` | Temporary user uploads | No | Any |
| `exports` | Generated PDFs, CSVs | No | PDF, CSV |
| `temp` | Processing temporary files | No | Any |

### 10.3 File Organization

Files stored in Supabase Storage with path:
```
{bucket}/{year}/{month}/{day}/{uuid}-{original_filename}
```

Example:
```
media/2024/01/15/a1b2c3d4-mortgage-calculator-screenshot.png
```

### 10.4 Media Table Process

1. User uploads file via admin API
2. FastAPI validates file (type, size, virus scan)
3. File is uploaded to Supabase Storage with generated path
4. Public URL is returned and stored in `media.public_url`
5. Record created in `media` table with all metadata
6. File is served via CDN (Cloudflare)

### 10.5 Image Optimization Strategy

| Operation | Implementation | Timing |
|-----------|---------------|--------|
| Resize | Supabase Image Transformation API | On-demand via URL params |
| WebP conversion | Cloudflare or imgproxy | On-demand |
| BlurHash generation | Server-side on upload | Upload time |
| Alt text | Required via admin UI | Content creation |
| Lazy loading | Native `loading="lazy"` | Frontend |
| Responsive images | `srcset` generation | Backend helper |

### 10.6 Supported Media Types

| Type | `media_type` | Extensions | Max Size |
|------|-------------|------------|----------|
| Image | `image` | .jpg, .jpeg, .png, .webp, .avif | 5MB |
| Illustration | `illustration` | .svg, .png, .webp | 2MB |
| Icon | `icon` | .svg, .png | 1MB |
| PDF | `pdf` | .pdf | 20MB |
| Download | `download` | .pdf, .csv, .xlsx, .docx | 20MB |
| Avatar | `avatar` | .jpg, .jpeg, .png, .webp | 2MB |
| Video | `video` | .mp4, .webm | 50MB |

---

## 11. Calculator Engine

### 11.1 Architecture Overview

The calculator engine is the core of the platform. It must support adding new calculators with **zero code changes** on either frontend or backend.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CALCULATOR ENGINE                                │
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐     │
│  │  Input       │    │  Computation │    │   Output         │     │
│  │  Validation  │───▶│  Engine      │───▶│   Formatting     │     │
│  └──────────────┘    └──────────────┘    └──────────────────┘     │
│                            │                                       │
│                            ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    ENGINE TYPES                               │ │
│  │                                                               │ │
│  │  Formula Engine:                                             │ │
│  │    calculators.formula_expression = "P * (r * (1+r)^n) / ..."│ │
│  │    Evaluated via safe Python eval()                           │ │
│  │                                                               │ │
│  │  Python Engine:                                               │ │
│  │    calculators.engine_type = "python"                         │ │
│  │    calculators.engine_config = {"handler": "loan_payment"}    │ │
│  │    Registered Python handler                                  │ │
│  │                                                               │ │
│  │  JavaScript Engine (Future):                                  │ │
│  │    calculators.engine_type = "javascript"                     │ │
│  │    calculators.engine_config = {"code": "function calc()..."} │ │
│  │    Executed via PyMiniRacer or similar                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    RENDERING LAYER                            │ │
│  │                                                               │ │
│  │  Frontend reads:                                              │ │
│  │  - calculators.input_schema  → Renders dynamic form           │ │
│  │  - calculators.output_schema → Renders results                │ │
│  │  - calculator_charts         → Renders charts                 │ │
│  │  - calculator_faqs           → Renders FAQ section            │ │
│  │                                                               │ │
│  │  No frontend code changes needed for new calculators          │ │
│  └──────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 11.2 Engine Types

| Engine | When to Use | Example |
|--------|------------|---------|
| `formula` | Simple mathematical expressions | `a * b / c` |
| `python` | Complex calculations with conditionals | Loan amortization schedule |
| `javascript` | Client-side only calculations | Real-time preview |

### 11.3 Input Schema Design (JSON Schema)

The `input_schema` field in `calculators` uses standard JSON Schema to define the form:

```json
{
  "type": "object",
  "properties": {
    "loan_amount": {
      "type": "number",
      "title": "Loan Amount",
      "default": 200000,
      "minimum": 1000,
      "maximum": 10000000,
      "prefix": "$"
    },
    "interest_rate": {
      "type": "number",
      "title": "Interest Rate",
      "default": 6.5,
      "minimum": 0,
      "maximum": 30,
      "suffix": "%"
    },
    "loan_term": {
      "type": "integer",
      "title": "Loan Term",
      "default": 30,
      "enum": [15, 20, 25, 30],
      "enumNames": ["15 years", "20 years", "25 years", "30 years"],
      "suffix": "years"
    }
  },
  "required": ["loan_amount", "interest_rate", "loan_term"]
}
```

### 11.4 Output Schema Design

```json
{
  "type": "object",
  "properties": {
    "monthly_payment": {
      "type": "number",
      "title": "Monthly Payment",
      "prefix": "$",
      "format": "currency",
      "is_primary": true
    },
    "total_interest": {
      "type": "number",
      "title": "Total Interest Paid",
      "prefix": "$",
      "format": "currency"
    },
    "total_payment": {
      "type": "number",
      "title": "Total Payment",
      "prefix": "$",
      "format": "currency"
    },
    "amortization_schedule": {
      "type": "array",
      "title": "Amortization Schedule",
      "items": {
        "type": "object",
        "properties": {
          "month": { "type": "integer" },
          "payment": { "type": "number" },
          "principal": { "type": "number" },
          "interest": { "type": "number" },
          "balance": { "type": "number" }
        }
      }
    }
  }
}
```

### 11.5 Formula Engine

For simple calculators, the `formula_expression` field contains a Python-compatible expression:

```
# Mortgage monthly payment
P * (r * (1 + r)**n) / ((1 + r)**n - 1)

# Where:
# P = loan_amount (principal)
# r = interest_rate / 12 / 100 (monthly rate)
# n = loan_term * 12 (number of months)
```

Variables in the expression map directly to calculator_input keys. The engine:
1. Receives input values from the request
2. Substitutes variables into the formula
3. Uses Redis for caching complex computations (Phase 3)
4. Returns computed outputs

### 11.6 Python Engine

For complex calculators requiring iteration, conditionals, or external data:

```python
# calculators.engine_config = {"handler": "loan_amortization"}
# File: app/calculators/loan_amortization.py

def calculate(inputs: dict) -> dict:
    """Calculate full amortization schedule."""
    P = inputs['loan_amount']
    r = inputs['interest_rate'] / 12 / 100
    n = inputs['loan_term'] * 12
    
    monthly = P * (r * (1 + r)**n) / ((1 + r)**n - 1)
    
    schedule = []
    balance = P
    for month in range(1, n + 1):
        interest = balance * r
        principal = monthly - interest
        balance -= principal
        schedule.append({
            'month': month,
            'payment': round(monthly, 2),
            'principal': round(principal, 2),
            'interest': round(interest, 2),
            'balance': round(max(balance, 0), 2)
        })
    
    return {
        'monthly_payment': round(monthly, 2),
        'total_interest': round(monthly * n - P, 2),
        'total_payment': round(monthly * n, 2),
        'amortization_schedule': schedule
    }
```

### 11.7 Adding a New Calculator (Zero Code Workflow)

```
Admin creates calculator via admin panel:
1. Set name, slug, category
2. Define input_schema (JSON Schema via UI builder)
3. Define output_schema
4. Write formula_expression or select python handler
5. Add calculator_inputs rows for each input
6. Add calculator_outputs rows for each output
7. Add FAQs, examples, charts, sections
8. Set SEO metadata
9. Assign author, reviewer
10. Publish

Result: New calculator live on public site. No frontend or backend code written.
```

### 11.8 Chart Engine

Charts are configured entirely in the database:

```json
// calculator_charts.data_mapping
{
  "chart_type": "line",
  "labels": {
    "source": "output",
    "key": "amortization_schedule",
    "label_field": "month"
  },
  "datasets": [
    {
      "label": "Balance",
      "source": "output",
      "key": "amortization_schedule",
      "value_field": "balance",
      "color": "#4F46E5",
      "fill": false
    },
    {
      "label": "Interest",
      "source": "output",
      "key": "amortization_schedule",
      "value_field": "interest",
      "color": "#EF4444",
      "fill": true
    }
  ]
}
```

---

## 12. Audit Logging

### 12.1 Audit Scope

Every important action is logged. The audit system is **append-only** — never modified or deleted.

| Action Category | Actions Tracked |
|----------------|----------------|
| Content | create, update, delete, restore, publish, unpublish, archive, schedule |
| Auth | login, logout, login_failed, password_reset, email_verify |
| Users | user_created, user_updated, user_deleted, role_changed |
| Media | upload, delete, update, move |
| Settings | setting_created, setting_updated, setting_deleted |
| SEO | seo_updated, redirect_created |
| Permissions | role_created, permission_changed, user_role_added, user_role_removed |
| System | migration_run, cache_cleared, backup_created |

### 12.2 Audit Log Details Field Convention

```json
{
  "resource_name": "Mortgage Calculator",
  "resource_slug": "mortgage-calculator",
  "endpoint": "/api/v1/calculators/abc-123",
  "method": "PUT",
  "status_code": 200,
  "duration_ms": 45,
  "additional_info": {}
}
```

### 12.3 Changes Field Convention

```json
{
  "before": {
    "name": "Mortgage Old",
    "is_published": false
  },
  "after": {
    "name": "Mortgage Calculator",
    "is_published": true
  },
  "changed_fields": ["name", "is_published"]
}
```

### 12.4 Audit Log Retention

| Severity | Retention | Table |
|----------|-----------|-------|
| info | 90 days | audit_logs |
| warning | 1 year | audit_logs |
| error | 3 years | audit_logs |
| critical | Forever | audit_logs (export to cold storage) |

### 12.5 Implementation Pattern

```python
# Pseudocode — Service layer calls audit service
class AuditService:
    async def log(
        user_id: UUID,
        action: str,
        resource_type: str,
        resource_id: UUID,
        details: dict = None,
        changes: dict = None,
        severity: str = "info"
    ):
        """
        - Extracts ip_address and user_agent from request context
        - Creates audit_logs record
        - Non-blocking (fire-and-forget or background task)
        """
```

---

## 13. Permissions & RBAC

### 13.1 Role Hierarchy

```
super_admin
  └── Full system access, cannot be restricted
admin
  └── All management features except system settings
editor
  └── Create, edit, publish content
seo_manager
  └── SEO metadata, redirects, sitemaps
content_writer
  └── Create and edit own content (cannot publish)
reviewer
  └── Review and approve content
support
  └── View content, manage newsletters, support inquiries
```

### 13.2 Permission Granularity

Permissions follow the pattern: `{resource}:{action}`

**Resources:** `calculator`, `blog_post`, `guide`, `category`, `media`, `page`, `navigation`, `footer`, `advertisement`, `setting`, `user`, `role`, `analytics`, `newsletter`, `testimonial`, `redirect`, `sitemap`, `audit_log`, `author`, `reviewer`

**Actions:** `create`, `read`, `update`, `delete`, `publish`, `unpublish`, `archive`, `restore`, `review`, `approve`, `reject`, `manage`

### 13.3 Sample Permission Matrix

| Permission | Super Admin | Admin | Editor | SEO Mgr | Writer | Reviewer | Support |
|-----------|:-----------:|:-----:|:------:|:-------:|:------:|:--------:|:-------:|
| calculator:create | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| calculator:read | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| calculator:update | ✅ | ✅ | ✅ | ❌ | ✅* | ❌ | ❌ |
| calculator:delete | ✅ | ✅* | ❌ | ❌ | ❌ | ❌ | ❌ |
| calculator:publish | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| calculator:review | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| seo:update | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| media:upload | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| users:manage | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| settings:manage | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| analytics:read | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

> *Own content only
> *Cannot delete published

### 13.4 Permission Check Flow

```
Request → JWT Middleware → Extract user_id
  → Load user roles + permissions (cached in Redis)
  → Check resource:action against user permissions
  → Allow/Deny (403 Forbidden)
```

### 13.5 Default Role Seeds

```sql
-- Inserted on first migration
INSERT INTO roles (name, slug, description, is_system) VALUES
  ('Super Admin', 'super-admin', 'Full system access', true),
  ('Admin', 'admin', 'Management access', true),
  ('Editor', 'editor', 'Create and publish content', true),
  ('SEO Manager', 'seo-manager', 'Manage SEO metadata', true),
  ('Content Writer', 'content-writer', 'Create content', true),
  ('Reviewer', 'reviewer', 'Review content', true),
  ('Support', 'support', 'Support access', true);
```

---

## 14. Scalability & Performance

### 14.1 Expected Scale

| Metric | Target |
|--------|--------|
| Calculators | 1,000+ |
| Blog posts | 10,000+ |
| Guides | 500+ |
| Page views/month | 10M+ |
| Media files | 50,000+ |
| Users | 100,000+ |
| API requests/second | 1,000+ |

### 14.2 Performance Strategies

| Strategy | Implementation | Impact |
|----------|---------------|--------|
| **Partial Indexes** | `WHERE deleted_at IS NULL` | Reduces index size significantly |
| **Covering Indexes** | Include frequently queried columns | Eliminates table lookups |
| **Connection Pooling** | PgBouncer (Supabase built-in) | Handles 1000+ concurrent connections |
| **Read Replicas** | Supabase read replicas for analytics | Isolates reporting queries |
| **Query Optimization** | N+1 prevention via SQLAlchemy eager loading | Eliminates query overhead |
| **Materialized Views** | `popular_calculators` refreshed periodically | Avoids expensive aggregation queries |
| **Table Partitioning** | `page_views` partitioned by month | Efficient time-range queries, easy archiving |
| **Full-Text Search** | GIN indexes on tsvector columns | Fast search without external dependencies |
| **Connection Management** | AsyncSession with connection pooling | Non-blocking I/O |

### 14.3 Partitioning Strategy

For high-volume tables (`page_views`, `audit_logs`, `search_history`):

```sql
-- Partition page_views by month
CREATE TABLE page_views (
    id BIGSERIAL,
    page_type VARCHAR(50),
    page_id UUID,
    url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE page_views_2024_01 PARTITION OF page_views
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE page_views_2024_02 PARTITION OF page_views
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

### 14.4 Caching Strategy (Phase 3)

| Cache Layer | What | TTL | Invalidation |
|-------------|------|-----|-------------|
| Redis | Calculator results | 1 hour | On calculator update |
| Redis | SEO metadata | 24 hours | On SEO update |
| Redis | User permissions | 1 hour | On role change |
| CDN | API responses | 5 minutes | Cache purge on publish |
| CDN | Static assets | 1 year | Cache bust via hash |

### 14.5 Database Connection Management

```
Max Connections: 300 (Supabase Pro)
Connection Pool:
  - Min: 10
  - Max: 50
  - Overflow: 20
  - Pool size calculation: (max_connections * 0.7) / app_instances
  - Reserve 30% connections for migrations, admin, monitoring

AsyncSession:
  - One session per request
  - Session per request pattern
  - Commit on success, rollback on error
```

---

## 15. Future-Proofing

### 15.1 Internationalization (i18n)

Current schema supports i18n via:

- JSONB fields for multilingual content: `calculator_i18n`, `blog_i18n`
- `locale` column in `site_settings`
- Future: Dedicated translation tables

**Recommended pattern for i18n tables:**
```sql
-- Future additions (Phase 4)
calculator_translations:
  - calculator_id → calculators.id
  - locale VARCHAR(10)
  - name VARCHAR(255)
  - description TEXT
  - UNIQUE(calculator_id, locale)
```

### 15.2 AI Assistant Integration

The `ai_explanations` table is ready for:
- AI-generated calculator explanations
- Step-by-step problem-solving
- Natural language query responses
- Personalized financial advice

### 15.3 Mobile App Support

Architecture already supports mobile:
- All data via REST API
- Supabase Auth for mobile auth
- Responsive media thumbnails
- Paginated endpoints for mobile performance

### 15.4 Analytics & Reporting

Tables support:
- Google Analytics 4 integration (via `page_views`)
- Custom dashboard (via `popular_calculators` + aggregation queries)
- Export to CSV/PDF (via `saved_calculations`)
- User behavior tracking (via `search_history`)

### 15.5 Multi-Tenant / White-Label

Schema supports extension for multi-tenant:
- Add `tenant_id` to all content tables
- Add `tenants` table with branding config
- Row-Level Security (RLS) per tenant

### 15.6 Content Versioning

Future `content_versions` table:

```sql
-- Future addition for content version history
content_versions:
  - id UUID PK
  - resource_type VARCHAR(50)
  - resource_id UUID
  - version_number INTEGER
  - data JSONB (full snapshot)
  - created_by UUID → users.id
  - created_at TIMESTAMPTZ
  - UNIQUE(resource_type, resource_id, version_number)
```

### 15.7 Scheduled Content

Implemented via `scheduled_at` column and a background worker:
- Cron job checks for content with `scheduled_at <= NOW()` AND `status = 'scheduled'`
- Updates to `status = 'published'`, sets `published_at`
- Sends notification to author

---

## Appendix A: Complete Table List

| # | Table | Schema | Type | Estimated Rows |
|---|-------|--------|------|---------------|
| 1 | users | public | Core | 100K |
| 2 | user_profiles | public | Core | 100K |
| 3 | roles | public | Auth | 10 |
| 4 | permissions | public | Auth | 100 |
| 5 | role_permissions | public | Auth | 200 |
| 6 | user_roles | public | Auth | 100K |
| 7 | user_sessions | public | Auth | 500K |
| 8 | categories | public | Content | 100 |
| 9 | calculators | public | Content | 1K |
| 10 | calculator_inputs | public | Content | 10K |
| 11 | calculator_outputs | public | Content | 10K |
| 12 | calculator_formulas | public | Content | 1K |
| 13 | calculator_faqs | public | Content | 10K |
| 14 | calculator_examples | public | Content | 5K |
| 15 | calculator_references | public | Content | 5K |
| 16 | calculator_charts | public | Content | 2K |
| 17 | calculator_sections | public | Content | 5K |
| 18 | related_calculators | public | Content | 5K |
| 19 | guides | public | Content | 500 |
| 20 | guide_sections | public | Content | 5K |
| 21 | guide_calculators | public | Content | 2K |
| 22 | blog_posts | public | Content | 10K |
| 23 | blog_sections | public | Content | 50K |
| 24 | blog_calculators | public | Content | 5K |
| 25 | seo_metadata | public | SEO | 15K |
| 26 | redirects | public | SEO | 1K |
| 27 | sitemaps | public | SEO | 10 |
| 28 | custom_pages | public | Content | 50 |
| 29 | media_folders | public | Media | 100 |
| 30 | media | public | Media | 50K |
| 31 | calculator_media | public | Media | 5K |
| 32 | blog_media | public | Media | 10K |
| 33 | guide_media | public | Media | 2K |
| 34 | homepage_sections | public | Site | 20 |
| 35 | navigation_items | public | Site | 100 |
| 36 | footer_columns | public | Site | 10 |
| 37 | footer_links | public | Site | 50 |
| 38 | advertisements | public | Site | 50 |
| 39 | testimonials | public | Site | 50 |
| 40 | newsletter_subscribers | public | Site | 100K |
| 41 | authors | public | People | 50 |
| 42 | reviewers | public | People | 20 |
| 43 | site_settings | public | Config | 100 |
| 44 | page_views | public | Analytics | 100M+ |
| 45 | search_history | public | Analytics | 10M+ |
| 46 | popular_calculators | public | Analytics | 1K |
| 47 | audit_logs | public | Audit | 10M+ |
| 48 | bookmarks | public | Future | 100K |
| 49 | saved_calculations | public | Future | 100K |
| 50 | notifications | public | Future | 500K |
| 51 | ai_explanations | public | Future | 5K |

---

## Appendix B: Best Practices

### Development Workflow

1. **All schema changes via Alembic migrations** — Never modify database directly
2. **Migration review process** — Every migration reviewed before production
3. **Seed data in migrations** — Default roles, permissions, settings
4. **Test on staging first** — Never run untested migrations on production

### Query Best Practices

1. **Always filter deleted_at IS NULL** for content queries
2. **Use selectinload** for related collections (avoid N+1)
3. **Use contains_eager** when filtering on joined tables
4. **Use lazyload** by default, eager load explicitly
5. **Use `with_for_update()`** for critical financial calculations (locking)
6. **Use `RETURNING`** clause for insert/update operations
7. **Use server-side cursors** for large result sets

### Security Best Practices

1. **Never expose internal IDs** — Use slugs or public UUIDs
2. **Never trust client input** — Validate on server with Pydantic
3. **Use parameterized queries** — SQLAlchemy handles this by default
4. **Row-Level Security (RLS)** enabled on all tables
5. **Rate limiting** on all public endpoints
6. **Input sanitization** for all rich text fields

### Migration Best Practices

1. **One migration per change** — Keep migrations atomic
2. **Test rollback** — Every migration must have a downgrade
3. **Backfill data** — Use batch processing for large tables
4. **Zero-downtime migrations** — Use `CREATE INDEX CONCURRENTLY` for production
5. **Lock timeouts** — Set `lock_timeout` to prevent blocking

---

## Appendix C: Naming Convention Quick Reference

| Element | Convention | Example |
|---------|-----------|---------|
| Database | `financecalculator_{env}` | `financecalculator_prod` |
| Schema | `public`, `audit` | `public` |
| Table | `snake_case` plural | `calculator_inputs` |
| Column | `snake_case` | `is_published` |
| Primary Key | `id` | `id UUID PK` |
| Foreign Key | `singular_table_id` | `calculator_id` |
| Join Table | `table1_table2` | `calculator_media` |
| Index | `idx_{table}_{cols}` | `idx_calculators_slug` |
| Unique | `uq_{table}_{cols}` | `uq_calculators_slug` |
| Check | `ck_{table}_{desc}` | `ck_calculators_status` |
| ENUM Values | `VARCHAR` with CHECK | `CK: draft/published/archived/scheduled` |
| JSONB Keys | `camelCase` | `isPrimary`, `sortOrder` |

---

> **Document Version:** 2.0.0
> **This document is the authoritative blueprint for all Phase 2 and Phase 3 development.**
> **Every table defined here will be implemented as SQLAlchemy 2.0 models in the next phase.**
> **The architecture is designed to scale to 1000+ calculators without architectural changes.**
