# Daily Paper

Daily Paper 是一个面向多用户个性化投送的 arXiv AI 论文系统。当前仓库包含三条主线：

- 元数据采集：每天抓取 arXiv AI 分类元数据并入库
- 个性化投送：按每个用户的时区、发表时间窗、分类和主题生成日报
- 前台发布：前端工作台按用户主题 token 动态渲染

## 当前版本状态

- 前台除了保留 `/`、`/daily/YYYY-MM-DD` 示例页外，已新增个性化工作台 `/u/[handle]` 和设置页 `/u/[handle]/settings`。
- 后端除了最小监控与 PV 统计外，已新增用户配置、主题配置、用户报告和 `arxiv_papers` 元数据表。
- 当前推荐的生产链路是：先每日同步 arXiv 元数据，再按用户配置生成报告。元数据池只保存论文基础信息，不保存全量 PDF/TXT，因此存储压力远低于全文缓存。

## 当前推荐部署链路

1. `backend/scripts/run_scheduled_pipeline.py` 作为统一定时入口，先同步 arXiv 元数据，再生成到期用户日报。
2. `backend/scripts/sync_arxiv_metadata.py` 每天抓最近几天的 AI 分类元数据并 upsert 到 PostgreSQL；若首轮日期窗口没有抓到结果，会自动向前扩窗后二次搜寻。
3. `backend/scripts/run_due_deliveries.py` 扫描到期用户并生成当天个性化报告；若所选回看日期没有命中论文，会自动扩大日期范围再筛选。
4. `frontend/` 读取用户报告和主题 token，在 `/u/[handle]` 工作台渲染。

## 仓库结构

```text
homeworks/
├── .qwen/skills/daily-paper/   # 抓取、下载 PDF、提取 TXT 的核心流程与约束
├── backend/                    # FastAPI + PostgreSQL + 元数据同步/个性化投送脚本
├── docs/runbooks/              # 操作手册
└── frontend/                   # Next.js 前端工作台
```

## 当前真源与存储策略

- 论文元数据真源：PostgreSQL `arxiv_papers`
- 用户投送配置真源：PostgreSQL `user_delivery_profiles`
- 用户主题真源：PostgreSQL `user_theme_profiles`
- 用户日报真源：PostgreSQL `user_reports`

说明：

- `arxiv_papers` 只保存元数据：`arxiv_id`、标题、作者、摘要、分类、URL、发布时间
- 默认不会为全量论文保存 PDF 和 TXT，因此每天抓取不会带来灾难性的磁盘占用
- 只有需要进入深读流程的重点论文，才建议按需运行 `.qwen/skills/daily-paper/download_pdf.py` 与 `pdf_to_txt.py`

## 当前最短工作流

1. 初始化数据库：`backend/sql/init.sql`、`backend/sql/seed_phase2a.sql`
2. 使用统一定时脚本：

```bash
python backend/scripts/run_scheduled_pipeline.py
```

3. 如需单独验证两个阶段，也可以分别执行：

```bash
python backend/scripts/sync_arxiv_metadata.py
python backend/scripts/run_due_deliveries.py
```

4. 启动后端与前端，访问：
   - `/u/research-lead`
   - `/u/vision-scout`

5. 如需对少量重点论文做深读，再按需使用：

```bash
python .qwen/skills/daily-paper/download_pdf.py --workers 2
python .qwen/skills/daily-paper/pdf_to_txt.py --workers 2
```

## GitHub CI

- 已新增 GitHub Actions 工作流：`.github/workflows/ci.yml`
- push 后会自动执行：
  - 后端 `python -m unittest discover -s backend/tests`
  - 前端 `npm test`
  - 前端 `npm run lint`
  - 前端 `npm run build`

## Vercel 环境变量

前端现在通过 Next.js 同源 `/api/*` 代理转发到后端，推荐在 Vercel 配置：

```bash
API_BASE_URL=https://your-railway-backend.example.com
```

说明：

- 生产环境请只设置服务端变量 `API_BASE_URL`
- 不要把 `NEXT_PUBLIC_API_BASE_URL` 或 `NEXT_PUBLIC_ADMIN_API_BASE_URL` 指到 Vercel 自己域名，否则 `/api/*` 代理可能递归请求自己
- 这样浏览器不会再因为回退到 `127.0.0.1` 导致工作台页面报错

## Railway 定时任务命令

后端部署在 Railway 时，定时任务直接执行下面这条命令即可：

```bash
python backend/scripts/run_scheduled_pipeline.py
```

如果你要补历史日期，或者想放大空结果重试窗口，也可以传同步参数：

```bash
python backend/scripts/run_scheduled_pipeline.py \
  --metadata-end-date 2026-03-15 \
  --metadata-lookback-days 1 \
  --metadata-expand-step-days 2 \
  --metadata-max-expansions 1
```

## 本地开发与验证

前端：

```bash
cd frontend
npm run test
npm run build
```

数据管线：

```bash
cd .qwen/skills/daily-paper
python crawler.py --start-date 2026-03-12 --end-date 2026-03-12 --limit 203 --category cs.AI
python download_pdf.py --workers 8
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate arxiv
python pdf_to_txt.py --workers 4
```

说明：

- `pdf_to_txt.py` 依赖 `pypdf`
- 请在已安装 `pypdf` 的 conda 环境中执行，当前实操验证通过的环境名为 `arxiv`

## 当前阶段不做的事

- 不把站点改成 SSR
- 不引入多用户系统
- 不引入支付、登录、社交分享
- 不把推荐和深读脚本化
- 不继续把 `/admin` 扩展成多用户后台或运维平台

## Phase 2A 本地入口

最小后台运行说明见：

- `backend/README.md`

当前 `backend/` 的定位是：

- 为内部监控提供最小 FastAPI + PostgreSQL 后台
- 提供 `/health`、`/api/admin/overview`、`/api/admin/pipeline-runs`、`/api/admin/errors`
- 为 `/admin` 页面提供只读监控数据

当前已验证：

- PostgreSQL 初始化与 seed 数据导入
- FastAPI 启动
- 4 个 API 真实返回数据
- `/admin` 路由可访问

当前未覆盖：

- 真实脚本运行状态自动写库
- 真实 PV 汇总写库
- UV 去重与事件平台

## 推荐阅读顺序

1. `.qwen/skills/daily-paper/SKILL.md`
2. `docs/runbooks/daily-report-production.md`
3. `frontend/README.md`
