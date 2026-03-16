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
