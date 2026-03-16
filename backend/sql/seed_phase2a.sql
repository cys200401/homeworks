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

insert into users (
  id,
  handle,
  display_name,
  email,
  timezone,
  created_at,
  updated_at
)
values
  (
    '10101010-1010-1010-1010-101010101010',
    'research-lead',
    'Research Lead',
    'research-lead@example.com',
    'America/Los_Angeles',
    '2026-03-14T00:00:00Z',
    '2026-03-14T00:00:00Z'
  ),
  (
    '20202020-2020-2020-2020-202020202020',
    'vision-scout',
    'Vision Scout',
    'vision-scout@example.com',
    'Asia/Shanghai',
    '2026-03-14T00:00:00Z',
    '2026-03-14T00:00:00Z'
  )
on conflict (id) do update
set
  display_name = excluded.display_name,
  email = excluded.email,
  timezone = excluded.timezone,
  updated_at = excluded.updated_at;

insert into user_delivery_profiles (
  id,
  user_id,
  delivery_enabled,
  delivery_local_time,
  window_start_hour,
  window_end_hour,
  lookback_days,
  categories_json,
  next_run_at,
  last_run_at,
  created_at,
  updated_at
)
values
  (
    '30303030-3030-3030-3030-303030303030',
    '10101010-1010-1010-1010-101010101010',
    true,
    time '08:00',
    0,
    12,
    2,
    '["cs.AI", "cs.LG", "cs.CL"]'::jsonb,
    '2026-03-16T15:00:00Z',
    '2026-03-15T15:00:00Z',
    '2026-03-14T00:00:00Z',
    '2026-03-15T15:00:00Z'
  ),
  (
    '40404040-4040-4040-4040-404040404040',
    '20202020-2020-2020-2020-202020202020',
    true,
    time '08:30',
    8,
    23,
    3,
    '["cs.CV", "cs.AI", "cs.IR"]'::jsonb,
    '2026-03-16T00:30:00Z',
    '2026-03-15T00:30:00Z',
    '2026-03-14T00:00:00Z',
    '2026-03-15T00:30:00Z'
  )
on conflict (id) do update
set
  delivery_enabled = excluded.delivery_enabled,
  delivery_local_time = excluded.delivery_local_time,
  window_start_hour = excluded.window_start_hour,
  window_end_hour = excluded.window_end_hour,
  lookback_days = excluded.lookback_days,
  categories_json = excluded.categories_json,
  next_run_at = excluded.next_run_at,
  last_run_at = excluded.last_run_at,
  updated_at = excluded.updated_at;

insert into user_theme_profiles (
  id,
  user_id,
  prompt_text,
  theme_name,
  tokens_json,
  created_at,
  updated_at
)
values
  (
    '50505050-5050-5050-5050-505050505050',
    '10101010-1010-1010-1010-101010101010',
    'Editorial dashboard with warm paper texture, calm motion and rounded cards.',
    'editorial',
    '{
      "themeName": "editorial",
      "fontPreset": "editorial",
      "layoutDensity": "balanced",
      "cardStyle": "panel",
      "heroPattern": "mesh",
      "borderRadius": "soft",
      "motionLevel": "calm",
      "palette": {
        "background": "#f4efe5",
        "foreground": "#18161a",
        "accent": "#b45309",
        "accentSoft": "#facc15",
        "surface": "#fffaf1",
        "surfaceAlt": "#efe3cf",
        "border": "#1f2937"
      }
    }'::jsonb,
    '2026-03-14T00:00:00Z',
    '2026-03-15T15:00:00Z'
  ),
  (
    '60606060-6060-6060-6060-606060606060',
    '20202020-2020-2020-2020-202020202020',
    'Bold brutalist research UI with sharp corners, cobalt accents and compact density.',
    'brutalist',
    '{
      "themeName": "brutalist",
      "fontPreset": "modern",
      "layoutDensity": "compact",
      "cardStyle": "outline",
      "heroPattern": "rays",
      "borderRadius": "sharp",
      "motionLevel": "lively",
      "palette": {
        "background": "#f4f4f0",
        "foreground": "#111111",
        "accent": "#0047ff",
        "accentSoft": "#ffcc00",
        "surface": "#ffffff",
        "surfaceAlt": "#e7ebff",
        "border": "#111111"
      }
    }'::jsonb,
    '2026-03-14T00:00:00Z',
    '2026-03-15T00:30:00Z'
  )
on conflict (id) do update
set
  prompt_text = excluded.prompt_text,
  theme_name = excluded.theme_name,
  tokens_json = excluded.tokens_json,
  updated_at = excluded.updated_at;

insert into user_reports (
  id,
  user_id,
  report_date,
  status,
  title,
  summary,
  total_papers,
  tags_json,
  trends,
  highlights_json,
  notables_json,
  theme_tokens_json,
  source_meta_json,
  published_at,
  created_at,
  updated_at
)
values
  (
    '70707070-7070-7070-7070-707070707070',
    '10101010-1010-1010-1010-101010101010',
    '2026-03-15',
    'published',
    'Research Lead 的个性化 AI 晨报',
    '这份报告面向偏研究运营视角，优先保留了过去两天内凌晨到中午发布、且属于 cs.AI、cs.LG、cs.CL 的工作。筛选结果更偏向智能体、长上下文助手和训练效率，适合在早会前快速扫过重点方向。',
    5,
    '["智能体系统", "长上下文", "训练效率"]'::jsonb,
    '研究方向正在从单篇模型改进转向围绕检索、规划、反馈和部署效率的一体化系统能力。',
    '[
      {
        "arxivId": "2603.15001v1",
        "title": "Composable Agent Loops for Reliable Scientific Discovery",
        "authors": ["Ada Lovelace", "Alan Turing", "Fei-Fei Li"],
        "abstract": "We study how composable agent loops can improve reliability in scientific discovery workflows.",
        "categories": ["cs.AI", "cs.LG"],
        "arxivUrl": "https://arxiv.org/abs/2603.15001",
        "tldr": "通过可组合智能体循环提升科研任务可靠性。",
        "problem": "单轮推理链在科研任务中容易遗漏证据，缺乏持续纠错机制。",
        "methodology": "作者把规划、检索、执行和反思拆成可循环的代理模块，并通过预算控制减少无效迭代。",
        "keyFindings": [
          "科研问答和实验设计任务的成功率都明显提高。",
          "反思模块显著降低了错误结论累积。",
          "检索与规划交替进行比一次性长规划更稳健。"
        ],
        "significance": "这类闭环代理是未来研究助手产品的重要基础设施。",
        "limitations": "目前主要验证于受控基准，真实开放科研环境仍需补充实验。"
      },
      {
        "arxivId": "2603.15002v1",
        "title": "Sparse Preference Tuning for Long-Context Assistants",
        "authors": ["Daphne Koller", "Chelsea Finn"],
        "abstract": "This work studies sparse preference optimization for assistants operating over long context windows.",
        "categories": ["cs.CL", "cs.LG"],
        "arxivUrl": "https://arxiv.org/abs/2603.15002",
        "tldr": "稀疏偏好优化降低长上下文助手训练成本。",
        "problem": "长上下文助手的偏好训练成本高，且容易因为数据冗余带来收益递减。",
        "methodology": "论文通过稀疏标注采样和分段式偏好更新，只在高价值片段上施加监督。",
        "keyFindings": [
          "训练 token 消耗显著下降。",
          "对有用性和一致性的保持优于简单下采样基线。",
          "长上下文窗口上的对齐稳定性更好。"
        ],
        "significance": "对想控制训练成本的产品团队非常实用。",
        "limitations": "仍依赖高质量偏好数据筛选器。"
      }
    ]'::jsonb,
    '[
      {
        "arxivId": "2603.15003v1",
        "title": "Compact Diffusion Distillation for Edge Image Generation",
        "authors": ["Ian Goodfellow", "Jitendra Malik"],
        "abstract": "We distill multi-step diffusion models into lightweight generators suitable for edge deployment.",
        "categories": ["cs.CV", "cs.LG"],
        "arxivUrl": "https://arxiv.org/abs/2603.15003",
        "tldr": "蒸馏扩散模型以支持边缘端图像生成。",
        "comment": "适合作为生成模型压缩和部署方向的跟踪项。"
      },
      {
        "arxivId": "2603.15004v1",
        "title": "Grounded Video Reasoning with Temporal Evidence Chains",
        "authors": ["Andrew Ng", "Serena Yeung"],
        "abstract": "The paper presents a grounded reasoning framework that links temporal evidence chains for video question answering.",
        "categories": ["cs.CV", "cs.AI"],
        "arxivUrl": "https://arxiv.org/abs/2603.15004",
        "tldr": "时间证据链提升视频理解与验证能力。",
        "comment": "如果后续关注视频推理和证据可解释性，这篇值得补读。"
      },
      {
        "arxivId": "2603.15005v1",
        "title": "Retrieval-Efficient Memory Compression for Enterprise Agents",
        "authors": ["Mira Murati", "Percy Liang"],
        "abstract": "This paper studies memory compression strategies for enterprise copilots with persistent context.",
        "categories": ["cs.AI", "cs.IR"],
        "arxivUrl": "https://arxiv.org/abs/2603.15005",
        "tldr": "检索友好的记忆压缩提升企业级智能体吞吐。",
        "comment": "和研究助手、企业 Copilot 的长期记忆问题直接相关。"
      }
    ]'::jsonb,
    '{
      "themeName": "editorial",
      "fontPreset": "editorial",
      "layoutDensity": "balanced",
      "cardStyle": "panel",
      "heroPattern": "mesh",
      "borderRadius": "soft",
      "motionLevel": "calm",
      "palette": {
        "background": "#f4efe5",
        "foreground": "#18161a",
        "accent": "#b45309",
        "accentSoft": "#facc15",
        "surface": "#fffaf1",
        "surfaceAlt": "#efe3cf",
        "border": "#1f2937"
      }
    }'::jsonb,
    '{
      "generatedAt": "2026-03-15T15:00:00Z",
      "windowStartHour": 0,
      "windowEndHour": 12,
      "lookbackDays": 2,
      "categories": ["cs.AI", "cs.LG", "cs.CL"]
    }'::jsonb,
    '2026-03-15T15:00:00Z',
    '2026-03-15T15:00:00Z',
    '2026-03-15T15:00:00Z'
  ),
  (
    '80808080-8080-8080-8080-808080808080',
    '20202020-2020-2020-2020-202020202020',
    '2026-03-15',
    'published',
    'Vision Scout 的个性化 AI 晨报',
    '这份报告偏视觉与检索应用，按照上海时区的工作时间窗口筛选出最近三天内的 CV / AI / IR 论文。页面风格采用高对比、紧凑布局，更适合快速浏览大量视觉方向条目。',
    5,
    '["视觉推理", "多模态检索", "边缘部署"]'::jsonb,
    '视觉研究一边继续追求更强的时序与多模态推理，一边显著强化端侧部署和证据链可解释性。',
    '[
      {
        "arxivId": "2603.15006v1",
        "title": "Structured Memory Retrieval for Multimodal Research Assistants",
        "authors": ["Geoffrey Hinton", "Yoshua Bengio"],
        "abstract": "This paper introduces a structured memory retrieval scheme for multimodal assistants.",
        "categories": ["cs.IR", "cs.CV", "cs.CL"],
        "arxivUrl": "https://arxiv.org/abs/2603.15006",
        "tldr": "结构化记忆检索增强长文档多模态理解。",
        "problem": "图表、正文和附录信息分散时，传统检索难以稳定建立证据链。",
        "methodology": "作者构建跨模态图结构，把文本片段、图像区域和表格条目统一编码后做局部图遍历。",
        "keyFindings": [
          "科研问答与证据定位精度明显提升。",
          "多跳检索中的语义漂移显著下降。",
          "图表引用更准确，可解释性更强。"
        ],
        "significance": "对多模态科研助手和视觉检索产品都很关键。",
        "limitations": "结构化预处理成本较高，对文档解析质量敏感。"
      },
      {
        "arxivId": "2603.15004v1",
        "title": "Grounded Video Reasoning with Temporal Evidence Chains",
        "authors": ["Andrew Ng", "Serena Yeung"],
        "abstract": "The paper presents a grounded reasoning framework that links temporal evidence chains for video question answering.",
        "categories": ["cs.CV", "cs.AI"],
        "arxivUrl": "https://arxiv.org/abs/2603.15004",
        "tldr": "时间证据链提升视频理解与验证能力。",
        "problem": "视频推理常常缺乏可回溯的时序证据，导致答案不稳定。",
        "methodology": "系统把视频拆分为关键事件节点，并显式追踪跨帧证据链来支持回答和验证。",
        "keyFindings": [
          "在视频问答和描述验证上都超过强基线。",
          "证据链约束显著改善了可解释性。",
          "时间跨度较长的视频也能保持更稳定的定位精度。"
        ],
        "significance": "适合需要可信视频分析的应用场景。",
        "limitations": "对事件切分质量仍有一定依赖。"
      }
    ]'::jsonb,
    '[
      {
        "arxivId": "2603.15003v1",
        "title": "Compact Diffusion Distillation for Edge Image Generation",
        "authors": ["Ian Goodfellow", "Jitendra Malik"],
        "abstract": "We distill multi-step diffusion models into lightweight generators suitable for edge deployment.",
        "categories": ["cs.CV", "cs.LG"],
        "arxivUrl": "https://arxiv.org/abs/2603.15003",
        "tldr": "蒸馏扩散模型以支持边缘端图像生成。",
        "comment": "端侧生成和低延迟视觉产品可以直接关注。"
      },
      {
        "arxivId": "2603.15007v1",
        "title": "Efficient Multimodal Indexing for Open-World Visual Search",
        "authors": ["Alyosha Efros", "Li Fei-Fei"],
        "abstract": "We present a multimodal indexing stack for open-world visual search over web-scale corpora.",
        "categories": ["cs.CV", "cs.IR"],
        "arxivUrl": "https://arxiv.org/abs/2603.15007",
        "tldr": "开放世界视觉搜索的多模态索引方案。",
        "comment": "和视觉检索基础设施直接相关，适合工程视角跟进。"
      },
      {
        "arxivId": "2603.15008v1",
        "title": "Adaptive Camera Agents for Warehouse Robotics",
        "authors": ["Pieter Abbeel", "Chelsea Finn"],
        "abstract": "The paper studies adaptive camera placement agents for warehouse robotics under sparse supervision.",
        "categories": ["cs.RO", "cs.CV", "cs.AI"],
        "arxivUrl": "https://arxiv.org/abs/2603.15008",
        "tldr": "自适应相机代理优化仓储机器人感知。",
        "comment": "如果关注视觉与机器人交叉，这篇可作为潜力项。"
      }
    ]'::jsonb,
    '{
      "themeName": "brutalist",
      "fontPreset": "modern",
      "layoutDensity": "compact",
      "cardStyle": "outline",
      "heroPattern": "rays",
      "borderRadius": "sharp",
      "motionLevel": "lively",
      "palette": {
        "background": "#f4f4f0",
        "foreground": "#111111",
        "accent": "#0047ff",
        "accentSoft": "#ffcc00",
        "surface": "#ffffff",
        "surfaceAlt": "#e7ebff",
        "border": "#111111"
      }
    }'::jsonb,
    '{
      "generatedAt": "2026-03-15T00:30:00Z",
      "windowStartHour": 8,
      "windowEndHour": 23,
      "lookbackDays": 3,
      "categories": ["cs.CV", "cs.AI", "cs.IR"]
    }'::jsonb,
    '2026-03-15T00:30:00Z',
    '2026-03-15T00:30:00Z',
    '2026-03-15T00:30:00Z'
  )
on conflict (id) do update
set
  title = excluded.title,
  summary = excluded.summary,
  total_papers = excluded.total_papers,
  tags_json = excluded.tags_json,
  trends = excluded.trends,
  highlights_json = excluded.highlights_json,
  notables_json = excluded.notables_json,
  theme_tokens_json = excluded.theme_tokens_json,
  source_meta_json = excluded.source_meta_json,
  published_at = excluded.published_at,
  updated_at = excluded.updated_at;

insert into arxiv_papers (
  arxiv_id,
  title,
  authors_json,
  abstract,
  categories_json,
  arxiv_url,
  published_at,
  first_seen_at,
  last_seen_at,
  source
)
values
  (
    '2603.15001v1',
    'Composable Agent Loops for Reliable Scientific Discovery',
    '["Ada Lovelace", "Alan Turing", "Fei-Fei Li"]'::jsonb,
    'We study how composable agent loops can improve reliability in scientific discovery workflows.',
    '["cs.AI", "cs.LG"]'::jsonb,
    'https://arxiv.org/abs/2603.15001',
    '2026-03-15T14:10:00Z',
    '2026-03-15T14:20:00Z',
    '2026-03-15T14:20:00Z',
    'seed'
  ),
  (
    '2603.15002v1',
    'Sparse Preference Tuning for Long-Context Assistants',
    '["Daphne Koller", "Chelsea Finn"]'::jsonb,
    'This work studies sparse preference optimization for assistants operating over long context windows.',
    '["cs.CL", "cs.LG"]'::jsonb,
    'https://arxiv.org/abs/2603.15002',
    '2026-03-15T18:20:00Z',
    '2026-03-15T18:30:00Z',
    '2026-03-15T18:30:00Z',
    'seed'
  ),
  (
    '2603.15003v1',
    'Compact Diffusion Distillation for Edge Image Generation',
    '["Ian Goodfellow", "Jitendra Malik"]'::jsonb,
    'We distill multi-step diffusion models into lightweight generators suitable for edge deployment.',
    '["cs.CV", "cs.LG"]'::jsonb,
    'https://arxiv.org/abs/2603.15003',
    '2026-03-15T02:40:00Z',
    '2026-03-15T03:00:00Z',
    '2026-03-15T03:00:00Z',
    'seed'
  ),
  (
    '2603.15004v1',
    'Grounded Video Reasoning with Temporal Evidence Chains',
    '["Andrew Ng", "Serena Yeung"]'::jsonb,
    'The paper presents a grounded reasoning framework that links temporal evidence chains for video question answering.',
    '["cs.CV", "cs.AI"]'::jsonb,
    'https://arxiv.org/abs/2603.15004',
    '2026-03-14T23:30:00Z',
    '2026-03-15T00:00:00Z',
    '2026-03-15T00:00:00Z',
    'seed'
  ),
  (
    '2603.15005v1',
    'Retrieval-Efficient Memory Compression for Enterprise Agents',
    '["Mira Murati", "Percy Liang"]'::jsonb,
    'This paper studies memory compression strategies for enterprise copilots with persistent context.',
    '["cs.AI", "cs.IR"]'::jsonb,
    'https://arxiv.org/abs/2603.15005',
    '2026-03-15T08:45:00Z',
    '2026-03-15T09:00:00Z',
    '2026-03-15T09:00:00Z',
    'seed'
  ),
  (
    '2603.15006v1',
    'Structured Memory Retrieval for Multimodal Research Assistants',
    '["Geoffrey Hinton", "Yoshua Bengio"]'::jsonb,
    'This paper introduces a structured memory retrieval scheme for multimodal assistants.',
    '["cs.IR", "cs.CV", "cs.CL"]'::jsonb,
    'https://arxiv.org/abs/2603.15006',
    '2026-03-15T00:25:00Z',
    '2026-03-15T00:40:00Z',
    '2026-03-15T00:40:00Z',
    'seed'
  ),
  (
    '2603.15007v1',
    'Efficient Multimodal Indexing for Open-World Visual Search',
    '["Alyosha Efros", "Li Fei-Fei"]'::jsonb,
    'We present a multimodal indexing stack for open-world visual search over web-scale corpora.',
    '["cs.CV", "cs.IR"]'::jsonb,
    'https://arxiv.org/abs/2603.15007',
    '2026-03-14T16:10:00Z',
    '2026-03-14T16:20:00Z',
    '2026-03-14T16:20:00Z',
    'seed'
  ),
  (
    '2603.15008v1',
    'Adaptive Camera Agents for Warehouse Robotics',
    '["Pieter Abbeel", "Chelsea Finn"]'::jsonb,
    'The paper studies adaptive camera placement agents for warehouse robotics under sparse supervision.',
    '["cs.RO", "cs.CV", "cs.AI"]'::jsonb,
    'https://arxiv.org/abs/2603.15008',
    '2026-03-13T12:05:00Z',
    '2026-03-13T12:30:00Z',
    '2026-03-13T12:30:00Z',
    'seed'
  )
on conflict (arxiv_id) do update
set
  title = excluded.title,
  authors_json = excluded.authors_json,
  abstract = excluded.abstract,
  categories_json = excluded.categories_json,
  arxiv_url = excluded.arxiv_url,
  published_at = excluded.published_at,
  last_seen_at = excluded.last_seen_at,
  source = excluded.source;
