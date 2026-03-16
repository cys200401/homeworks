create extension if not exists pgcrypto;

create table if not exists pipeline_runs (
  id uuid primary key default gen_random_uuid(),
  run_date date not null,
  stage text not null,
  status text not null,
  params_json jsonb,
  success_count integer not null default 0,
  failed_count integer not null default 0,
  skipped_count integer not null default 0,
  started_at timestamptz not null,
  finished_at timestamptz,
  duration_ms integer,
  notes text
);

create index if not exists pipeline_runs_stage_started_idx
  on pipeline_runs (stage, started_at desc);

create table if not exists run_errors (
  id uuid primary key default gen_random_uuid(),
  pipeline_run_id uuid references pipeline_runs(id) on delete set null,
  stage text not null,
  error_code text,
  error_message text not null,
  paper_arxiv_id text,
  raw_context jsonb,
  created_at timestamptz not null default now()
);

create index if not exists run_errors_created_idx
  on run_errors (created_at desc);

create table if not exists traffic_daily_stats (
  id uuid primary key default gen_random_uuid(),
  stat_date date not null,
  path text not null,
  page_type text not null,
  pv integer not null default 0,
  uv integer,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (stat_date, path)
);

create index if not exists traffic_daily_stats_date_idx
  on traffic_daily_stats (stat_date desc);

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  handle text not null unique,
  display_name text not null,
  email text unique,
  timezone text not null default 'UTC',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists users_handle_idx
  on users (handle);

create table if not exists user_delivery_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references users(id) on delete cascade,
  delivery_enabled boolean not null default true,
  delivery_local_time time not null default time '08:00',
  window_start_hour smallint not null default 0,
  window_end_hour smallint not null default 24,
  lookback_days integer not null default 1,
  categories_json jsonb not null default '["cs.AI"]'::jsonb,
  next_run_at timestamptz,
  last_run_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (window_start_hour between 0 and 23),
  check (window_end_hour between 0 and 24),
  check (lookback_days between 1 and 30),
  check (jsonb_typeof(categories_json) = 'array')
);

create index if not exists user_delivery_profiles_next_run_idx
  on user_delivery_profiles (delivery_enabled, next_run_at);

create table if not exists user_theme_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references users(id) on delete cascade,
  prompt_text text not null default '',
  theme_name text not null default 'editorial',
  tokens_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (jsonb_typeof(tokens_json) = 'object')
);

create table if not exists user_reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  report_date date not null,
  status text not null default 'published',
  title text not null,
  summary text not null,
  total_papers integer not null default 0,
  tags_json jsonb not null default '[]'::jsonb,
  trends text,
  highlights_json jsonb not null default '[]'::jsonb,
  notables_json jsonb not null default '[]'::jsonb,
  theme_tokens_json jsonb not null default '{}'::jsonb,
  source_meta_json jsonb not null default '{}'::jsonb,
  published_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, report_date),
  check (jsonb_typeof(tags_json) = 'array'),
  check (jsonb_typeof(highlights_json) = 'array'),
  check (jsonb_typeof(notables_json) = 'array'),
  check (jsonb_typeof(theme_tokens_json) = 'object'),
  check (jsonb_typeof(source_meta_json) = 'object')
);

create index if not exists user_reports_user_published_idx
  on user_reports (user_id, published_at desc);

create table if not exists arxiv_papers (
  arxiv_id text primary key,
  title text not null,
  authors_json jsonb not null default '[]'::jsonb,
  abstract text not null,
  categories_json jsonb not null default '[]'::jsonb,
  arxiv_url text not null,
  published_at timestamptz not null,
  first_seen_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now(),
  source text not null default 'arxiv',
  check (jsonb_typeof(authors_json) = 'array'),
  check (jsonb_typeof(categories_json) = 'array')
);

create index if not exists arxiv_papers_published_idx
  on arxiv_papers (published_at desc);
