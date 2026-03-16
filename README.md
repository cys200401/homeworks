# Daily Paper

Daily Paper 是一个 AI 驱动的 arXiv 论文日报系统。当前仓库聚焦两条主线：

- 内容生产：抓取论文、推荐、深读、生成日报数据文件
- 前台发布：把日报数据渲染为可导出的静态网站

## 当前版本状态

- 当前基线为 `v0.1 internal`：前台静态日报与最小监控后台都已落地，当前目标是冻结一个可上线内测基线。
- 前台公开范围是 `/` 与 `/daily/YYYY-MM-DD`；日报内容继续以 `frontend/data/daily/*.ts` 为真源。
- `/admin` 已存在，但定位是内部监控入口；它通过 `NEXT_PUBLIC_ADMIN_API_BASE_URL` 读取后端 `/health`、`/api/admin/overview`、`/api/admin/pipeline-runs`、`/api/admin/errors`。
- 当前数据库范围是 `pipeline_runs`、`run_errors`、`traffic_daily_stats`，用于最小运行记录与 PV 汇总，且允许 seed 数据与新增真实记录并存。

## 内测部署目标

- 这一步不扩功能、不改业务逻辑，只整理当前基线，让后续部署可控。
- 部署目标是：前台公开访问，`/admin` 内部使用，后端只承载健康检查、只读 admin API 与最小 PV 写入。
- 部署前只检查前端 `test/build`、后端 `/health`/admin API、PostgreSQL 初始化与真实记录、环境变量与 CORS。
- 当前边界见 `docs/milestones/v0.1-internal.md` 与 `docs/checklists/pre-deploy-checklist.md`。

当前阶段仍严格遵守 `.qwen/skills/daily-paper/SKILL.md` 的边界：推荐与深读由智能体完成，不新增 `recommend_papers.py`、`write_report.py` 一类脚本来接管核心流程。

## 仓库结构

```text
homeworks/
├── .qwen/skills/daily-paper/   # 抓取、下载 PDF、提取 TXT 的核心流程与约束
├── backend/                    # Phase 2A 最小监控后台（FastAPI + PostgreSQL）
├── docs/runbooks/              # 操作手册
└── frontend/                   # Next.js 静态网站
```

## 当前真源

- 抓取结果真源：`.qwen/skills/daily-paper/papers.json`
- 日报内容真源：`frontend/data/daily/*.ts`
- 日报注册入口：`frontend/data/daily/index.ts`
- 数据契约：`frontend/types/daily.ts`

## 当前最短工作流

1. 在 `.qwen/skills/daily-paper/` 运行 `crawler.py` 抓取论文元数据，并读取终端输出做推荐。
2. 如需深读，运行 `download_pdf.py` 与 `pdf_to_txt.py` 补齐推荐论文全文。
3. 将结果写入 `frontend/data/daily/YYYY-MM-DD.ts`。
4. 更新 `frontend/data/daily/index.ts`。
5. 在 `frontend/` 运行 `npm run build` 验证静态站可导出。

完整操作手册见：

- `docs/runbooks/daily-report-production.md`
- `docs/milestones/v0.1-internal.md`
- `docs/checklists/pre-deploy-checklist.md`

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
