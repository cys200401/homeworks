## frontend test / build

- [ ] 在 `frontend/` 执行 `npm run test`。
- [ ] 在 `frontend/` 执行 `npm run build`。
- [ ] 确认首页 `/` 与至少一个 `/daily/YYYY-MM-DD` 页面可正常生成。
- [ ] 确认 `/admin` 页面构建后仍保留当前内部监控入口，不引入额外前台功能。

## backend /health / admin API

- [ ] 启动后端后，确认 `GET /health` 返回 200，且响应包含数据库可用状态。
- [ ] 确认 `GET /api/admin/overview` 返回系统健康、最近 stage 状态、最近错误数和 PV 汇总。
- [ ] 确认 `GET /api/admin/pipeline-runs` 可返回最近运行记录。
- [ ] 确认 `GET /api/admin/errors` 可返回最近错误记录。

## PostgreSQL 初始化与真实记录

- [ ] `DATABASE_URL` 指向目标 PostgreSQL 实例。
- [ ] 按顺序执行 `backend/sql/init.sql` 与 `backend/sql/seed_phase2a.sql`。
- [ ] 确认 `pipeline_runs`、`run_errors`、`traffic_daily_stats` 三张表已创建。
- [ ] 确认数据库中既能读取 seed 数据，也能保留新增真实记录。
- [ ] 通过 `POST /api/traffic/pv` 验证最小 PV 写入，确认 `traffic_daily_stats` 会产生新增真实记录。

## 环境变量与 CORS

- [ ] 后端已设置 `DATABASE_URL`。
- [ ] 后端已按前端访问域设置 `ADMIN_API_CORS_ORIGINS`。
- [ ] 前端已设置 `NEXT_PUBLIC_ADMIN_API_BASE_URL` 指向当前后端地址。
- [ ] 打开 `/admin` 并触发前台 PV 上报时，确认浏览器没有 CORS 错误。

## 前台公开、/admin 内部使用

- [ ] 确认前台公开范围只包括 `/` 与 `/daily/YYYY-MM-DD`。
- [ ] 确认 `/admin` 仅用于内部监控访问，不作为公开页面入口。
- [ ] 确认 README 与里程碑文档中的对外范围和内部范围描述一致。
- [ ] 确认本次上线目标是“可上线内测基线”，不是继续扩展功能或进入部署实现。
