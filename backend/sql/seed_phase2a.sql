insert into pipeline_runs (
  id,
  run_date,
  stage,
  status,
  params_json,
  success_count,
  failed_count,
  skipped_count,
  started_at,
  finished_at,
  duration_ms,
  notes
)
values
  (
    '11111111-1111-1111-1111-111111111111',
    '2026-03-14',
    'crawler',
    'succeeded',
    '{"category":"cs.CV","limit":4}',
    4,
    0,
    0,
    '2026-03-14T08:00:00Z',
    '2026-03-14T08:00:14Z',
    14000,
    'Phase 2A seed data'
  ),
  (
    '22222222-2222-2222-2222-222222222222',
    '2026-03-14',
    'download_pdf',
    'failed',
    '{"workers":2}',
    2,
    1,
    0,
    '2026-03-14T08:10:00Z',
    '2026-03-14T08:10:20Z',
    20000,
    'Seeded failed download run'
  ),
  (
    '33333333-3333-3333-3333-333333333333',
    '2026-03-14',
    'pdf_to_txt',
    'succeeded',
    '{"workers":2}',
    2,
    0,
    0,
    '2026-03-14T08:20:00Z',
    '2026-03-14T08:20:05Z',
    5000,
    'Seeded text extraction run'
  ),
  (
    '44444444-4444-4444-4444-444444444444',
    '2026-03-14',
    'report_write',
    'succeeded',
    '{"date":"2026-03-14"}',
    1,
    0,
    0,
    '2026-03-14T08:25:00Z',
    '2026-03-14T08:25:03Z',
    3000,
    'Seeded report write run'
  ),
  (
    '55555555-5555-5555-5555-555555555555',
    '2026-03-14',
    'frontend_build',
    'succeeded',
    '{"command":"npm run build"}',
    1,
    0,
    0,
    '2026-03-14T08:30:00Z',
    '2026-03-14T08:30:08Z',
    8000,
    'Seeded frontend build run'
  )
on conflict (id) do nothing;

insert into run_errors (
  id,
  pipeline_run_id,
  stage,
  error_code,
  error_message,
  paper_arxiv_id,
  raw_context,
  created_at
)
values
  (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    '22222222-2222-2222-2222-222222222222',
    'download_pdf',
    'HTTP_429',
    'HTTP Error 429 while downloading paper PDF',
    '2603.11380v1',
    '{"workers":2}',
    '2026-03-14T08:10:10Z'
  ),
  (
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    '33333333-3333-3333-3333-333333333333',
    'pdf_to_txt',
    'MISSING_PYPDF',
    'Current Python environment is missing pypdf',
    '2603.11325v1',
    '{"env":"system-python"}',
    '2026-03-14T08:19:00Z'
  )
on conflict (id) do nothing;

insert into traffic_daily_stats (
  id,
  stat_date,
  path,
  page_type,
  pv,
  uv,
  created_at,
  updated_at
)
values
  (
    'c1c1c1c1-c1c1-c1c1-c1c1-c1c1c1c1c1c1',
    '2026-03-12',
    '/',
    'home',
    120,
    null,
    '2026-03-12T23:59:00Z',
    '2026-03-12T23:59:00Z'
  ),
  (
    'd1d1d1d1-d1d1-d1d1-d1d1-d1d1d1d1d1d1',
    '2026-03-13',
    '/',
    'home',
    168,
    null,
    '2026-03-13T23:59:00Z',
    '2026-03-13T23:59:00Z'
  ),
  (
    'e1e1e1e1-e1e1-e1e1-e1e1-e1e1e1e1e1e1',
    '2026-03-14',
    '/',
    'home',
    214,
    null,
    '2026-03-14T23:59:00Z',
    '2026-03-14T23:59:00Z'
  ),
  (
    'f1f1f1f1-f1f1-f1f1-f1f1-f1f1f1f1f1f1',
    '2026-03-14',
    '/daily/2026-03-14',
    'daily',
    96,
    null,
    '2026-03-14T23:59:00Z',
    '2026-03-14T23:59:00Z'
  ),
  (
    'abababab-abab-abab-abab-abababababab',
    '2026-03-14',
    '/daily/2026-03-13',
    'daily',
    41,
    null,
    '2026-03-14T23:59:00Z',
    '2026-03-14T23:59:00Z'
  ),
  (
    'cdcdcdcd-cdcd-cdcd-cdcd-cdcdcdcdcdcd',
    '2026-03-14',
    '/daily/2026-03-12',
    'daily',
    28,
    null,
    '2026-03-14T23:59:00Z',
    '2026-03-14T23:59:00Z'
  )
on conflict (stat_date, path) do update
set
  pv = excluded.pv,
  uv = excluded.uv,
  updated_at = excluded.updated_at;
