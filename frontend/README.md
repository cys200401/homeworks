# Daily Paper Frontend

`frontend/` 是 Daily Paper 的前台发布端：一个基于 Next.js App Router 的全静态站点，用于展示每日 AI 论文精选。

## 定位与约束

- 站点采用静态导出，`next.config.ts` 中固定为 `output: "export"`。
- 日报内容真源是 `data/daily/*.ts`。
- 前后端唯一数据契约是 `types/daily.ts`。
- 当前阶段不要改成服务端渲染，不要把日报生产逻辑迁入前端。

## 本地开发

在 `frontend/` 目录下执行：

```bash
npm run dev
```

默认打开 `http://localhost:3000` 即可查看首页和日报详情页。

## 本地验证

```bash
npm run test
npm run build
```

- `npm run test`：验证数据注册、页面渲染等基础行为。
- `npm run build`：验证新的日报数据是否能被静态导出。

## 日报数据来源

前端只消费已经生成好的日报文件，不负责抓取、推荐或深读。

- 日报文件目录：`data/daily/`
- 日报注册表：`data/daily/index.ts`
- 数据类型定义：`types/daily.ts`
- 生产操作手册：请查看仓库根目录 `docs/runbooks/daily-report-production.md`

## 新增日报的最小流程

### 1. 创建日报文件

在 `data/daily/` 下新增 `YYYY-MM-DD.ts`，并导出 `DailyReport`：

```ts
import type { DailyReport } from "@/types/daily";

export const report: DailyReport = {
  date: "2026-03-13",
  title: "2026年3月13日 AI论文日报",
  summary: "这里填写 3-5 句中文总览。",
  totalPapers: 24,
  tags: ["智能体", "多模态", "推理"],
  trends: "这里填写趋势洞察。",
  highlights: [],
  notables: [],
};
```

更完整的字段模板可直接参考：

- `data/daily/_example.ts`
- `data/daily/2000-01-01.ts`
- `types/daily.ts`

### 2. 注册日报

在 `data/daily/index.ts` 中新增 import，并把新日报插入 `reports` 数组最前面，保持最新日期在前。

### 3. 构建验证

```bash
npm run build
```

构建成功后，首页卡片和 `/daily/YYYY-MM-DD` 详情页会被静态生成。

## 关键数据结构

### `DailyReport`

- `date`: 日期，格式 `YYYY-MM-DD`
- `title`: 日报标题
- `summary`: 中文总览
- `totalPapers`: 爬虫抓取论文总数
- `highlights`: 重点论文列表
- `notables`: 推荐论文列表
- `trends`: 趋势洞察，可选
- `tags`: 标签列表

### `PaperHighlight`

在 `PaperBase` 基础上补充：

- `problem`
- `methodology`
- `keyFindings`
- `significance`
- `limitations`

### `PaperBrief`

在 `PaperBase` 基础上补充：

- `comment`

## 页面结构

### `/`

- 首页标题与副标题
- 日报卡片列表
- 若无数据则显示“暂无日报数据”

### `/daily/YYYY-MM-DD`

- 返回首页
- 日报头部
- 重点关注
- 也值得关注
- 可选趋势洞察

## 参考文件

- `app/page.tsx`
- `app/daily/[date]/page.tsx`
- `components/DailyCard.tsx`
- `components/PaperHighlight.tsx`
- `components/PaperBrief.tsx`
- `components/ReportHeader.tsx`
- `components/SectionDivider.tsx`
