# Daily Paper Backend

这是 Daily Paper 当前的最小监控后台。

当前范围只包括：

- FastAPI 骨架
- PostgreSQL 连接
- `arxiv_papers`
- `users`
- `user_delivery_profiles`
- `user_theme_profiles`
- `user_reports`
- `pipeline_runs`
- `run_errors`
- `traffic_daily_stats`
- 只读 admin API
- `backend/scripts/run_stage.py` 运行记录包装层
- `POST /api/traffic/pv` 最小 PV 写入接口
- `backend/scripts/run_scheduled_pipeline.py` 统一定时调度脚本
- `backend/scripts/sync_arxiv_metadata.py` 每日元数据同步脚本
- `backend/scripts/run_due_deliveries.py` 个性化日报生成脚本
- 首页与日报详情页通过 `TrafficBeacon` 做最小 PV 上报

当前不包括：

- UV 去重
- 全量 PDF/TXT 缓存
- 多用户鉴权
- 把深读流程对所有论文自动化

## 环境变量

至少设置：

```bash
export DATABASE_URL="postgresql://yushi@localhost:5432/daily_paper"
```

可选：

```bash
export ADMIN_API_CORS_ORIGINS="http://localhost:3000"
```

如果本机 PostgreSQL 通过 Homebrew 安装，命令执行前可先补 PATH：

```bash
export PATH="/opt/homebrew/opt/postgresql@18/bin:$PATH"
```

## 安装依赖

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 初始化数据库

执行顺序固定为：

1. `sql/init.sql`
2. `sql/seed_phase2a.sql`

```bash
psql "$DATABASE_URL" -f sql/init.sql
psql "$DATABASE_URL" -f sql/seed_phase2a.sql
```

## 启动服务

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## `run_stage.py` 的用途

`backend/scripts/run_stage.py` 是一个很薄的包装层，用来在不修改原脚本职责的前提下，把真实命令的运行结果写入：

- `pipeline_runs`
- `run_errors`

它只负责记录，不接管内容生产逻辑。

### fail open 含义

运行记录层必须 fail open：

- 数据库不可用时，原始命令仍继续执行
- 写 `pipeline_runs` 失败时，只输出 warning，不改变原始命令成败
- 写 `run_errors` 失败时，只输出 warning，不改变原始命令成败
- 原始命令的 `stdout` / `stderr` / `exit code` 都原样透传

这意味着：

- 不能吞掉 `crawler.py` 的终端输出
- 不能改写 `download_pdf.py` / `pdf_to_txt.py` / `frontend build` 的原始日志
- 原始命令返回多少退出码，`run_stage.py` 最终就返回多少

### 包装执行示例

在仓库根目录执行：

```bash
export DATABASE_URL="postgresql://yushi@localhost:5432/daily_paper"
```

包装 `crawler.py`：

```bash
python backend/scripts/run_stage.py --stage crawler -- \
  python .qwen/skills/daily-paper/crawler.py \
  --start-date 2026-03-09 \
  --end-date 2026-03-11 \
  --limit 5
```

包装 `download_pdf.py`：

```bash
python backend/scripts/run_stage.py --stage download_pdf -- \
  python .qwen/skills/daily-paper/download_pdf.py --workers 2
```

包装 `pdf_to_txt.py`：

```bash
python backend/scripts/run_stage.py --stage pdf_to_txt -- \
  python .qwen/skills/daily-paper/pdf_to_txt.py --workers 2
```

包装前端构建：

```bash
cd frontend
python ../backend/scripts/run_stage.py --stage frontend_build -- npm run build
```

说明：

- `report_write` 这个 stage 目前只预留给后续最小写回记录，不在本批收尾里继续扩展
- 包装层放在 `backend/`，不修改 `.qwen/skills/daily-paper/` 下现有脚本

## `sync_arxiv_metadata.py`

这个脚本用于每天抓取最近几天的 arXiv AI 分类元数据，并 upsert 到 `arxiv_papers`。

默认策略：

- 抓取分类：`cs.AI,cs.CL,cs.CV,cs.IR,cs.LG,cs.RO`
- 回看窗口：最近 2 天
- 每分类上限：200
- 保留期：180 天
- 若首轮窗口抓取结果为 0，会自动向前扩 2 天并重试 1 次

示例：

```bash
python backend/scripts/sync_arxiv_metadata.py
```

说明：

- 当前只保存元数据，不保存全量 PDF/TXT
- 对于 200 篇/天量级，保存半年元数据的存储成本通常远小于全文缓存
- 如果需要更保守的磁盘策略，可调小 `--retention-days`
- 可通过 `--expand-step-days` 与 `--max-expansions` 调整空结果时的扩窗重试策略

## `run_due_deliveries.py`

这个脚本会扫描 `user_delivery_profiles.next_run_at <= now()` 的用户，并生成/更新当天的 `user_reports`。

示例：

```bash
python backend/scripts/run_due_deliveries.py
```

推荐的生产调度顺序：

1. `sync_arxiv_metadata.py`
2. `run_due_deliveries.py`

补充说明：

- 若用户配置的原始回看日期范围内没有命中论文，报告生成会自动扩大日期范围后再筛一次
- 扩搜后仍然优先保留用户分类过滤，不会回退到无关分类的 demo 论文

## `run_scheduled_pipeline.py`

这个脚本把元数据同步和个性化投送串成一条定时命令，适合直接挂到 Railway 的 cron/job。

默认命令：

```bash
python backend/scripts/run_scheduled_pipeline.py
```

如果只想跑其中一个阶段：

```bash
python backend/scripts/run_scheduled_pipeline.py --skip-deliveries
python backend/scripts/run_scheduled_pipeline.py --skip-sync
```

如果要给同步阶段传自定义日期窗口：

```bash
python backend/scripts/run_scheduled_pipeline.py \
  --metadata-end-date 2026-03-15 \
  --metadata-lookback-days 1 \
  --metadata-expand-step-days 2 \
  --metadata-max-expansions 1
```

## `POST /api/traffic/pv`

这个接口用于首页和日报详情页的最小 PV 汇总写入。

最小入参只有：

```json
{
  "path": "/daily/2026-03-14",
  "pageType": "daily"
}
```

约束：

- 客户端不传 `stat_date`
- `stat_date` 由服务端按当天日期生成
- 当前只做 PV，不做 UV

本地验证示例：

```bash
curl -X POST http://127.0.0.1:8000/api/traffic/pv \
  -H "Content-Type: application/json" \
  -d '{"path":"/","pageType":"home"}'
```

## `TrafficBeacon` 的作用

前端通过 `frontend/components/traffic/TrafficBeacon.tsx` 做最小客户端上报：

- 首页挂 `path="/"`, `pageType="home"`
- 日报详情页挂 `path="/daily/YYYY-MM-DD"`, `pageType="daily"`

这样可以保持：

- `app/page.tsx` 继续是原来的 server/static 页面
- `app/daily/[date]/page.tsx` 继续是原来的 server/static 页面
- 只额外挂一个很小的客户端 beacon

### 开发环境去重策略

为了避免 React / Next 开发模式下 `useEffect` 重复触发导致 PV 翻倍，`TrafficBeacon` 在开发环境会按 `pageType:path` 做一次最小去重。

例如：

- `home:/`
- `daily:/daily/2026-03-14`

同一个 key 在开发环境只会上报一次。

### fail open 含义

PV 上报也保持 fail open：

- 上报失败不会影响页面渲染
- 后端未启动不会导致首页或日报页白屏
- 静态页面仍可正常访问

## 本地验证

### 1. 验证 4 个 API

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/admin/overview
curl http://127.0.0.1:8000/api/admin/pipeline-runs
curl http://127.0.0.1:8000/api/admin/errors
```

### 1.1 验证运行记录包装层

```bash
python backend/scripts/run_stage.py --stage crawler -- \
  python .qwen/skills/daily-paper/crawler.py \
  --start-date 2026-03-09 \
  --end-date 2026-03-11 \
  --limit 2
```

然后检查：

```bash
curl "http://127.0.0.1:8000/api/admin/pipeline-runs?limit=5"
curl "http://127.0.0.1:8000/api/admin/errors?limit=5"
```

### 1.2 验证 PV 写入

```bash
curl -X POST http://127.0.0.1:8000/api/traffic/pv \
  -H "Content-Type: application/json" \
  -d '{"path":"/daily/2026-03-14","pageType":"daily"}'
```

或直接访问：

- `http://localhost:3000/`
- `http://localhost:3000/daily/2026-03-14`

### 2. 启动前端并访问 `/admin`

```bash
cd ../frontend
npm run dev
```

浏览器打开：

```text
http://localhost:3000/admin
```

### 3. 前端跨域说明

本地联调时，如果前端运行在 `http://localhost:3000`，后端建议设置：

```bash
export ADMIN_API_CORS_ORIGINS="http://localhost:3000"
```

## 当前已验证范围

以下范围已经完成真实联调验证：

- PostgreSQL 可连接
- `sql/init.sql` 可成功建表
- `sql/seed_phase2a.sql` 可成功写入手工测试数据
- FastAPI 可启动
- 4 个接口可真实返回数据：
  - `GET /health`
  - `GET /api/admin/overview`
  - `GET /api/admin/pipeline-runs`
  - `GET /api/admin/errors`
- `POST /api/traffic/pv` 可真实写入 `traffic_daily_stats`
- 首页 PV 可真实写库
- 日报详情页 PV 可真实写库
- `run_stage.py` 包装真实 `frontend build` 可写入 `pipeline_runs`
- `run_stage.py` 包装真实 `crawler.py` 可写入 `pipeline_runs`
- 失败运行可真实写入 `run_errors`
- CORS 已允许 `http://localhost:3000`
- `frontend` dev server 可启动
- `/admin` 路由真实可访问，初始 loading 状态符合预期
- `/admin` 当前读取的是“seed 数据 + 新增真实记录”的混合结果，接口默认按最新时间倒序返回

## 当前未覆盖范围

当前仍未覆盖这些内容：

- UV 去重
- `page_events`
- `papers` / `report_papers`
- 更复杂的后台组件体系
- 任何把内容生产逻辑迁入后端的做法
