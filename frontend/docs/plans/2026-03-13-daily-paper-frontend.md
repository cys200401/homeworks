# Daily Paper Frontend Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将默认的 Next.js 初始项目重建为符合 `web-design` skill 规范的全静态 Daily Paper 日报站点。

**Architecture:** 基于 App Router 构建纯静态导出站点，所有日报数据以 TypeScript 文件保存在 `data/daily/`。页面由类型定义、数据注册表、可复用展示组件和统一的 Bauhaus 设计系统组成；通过构建时静态生成首页与日报详情页。

**Tech Stack:** Next.js 16、React 19、TypeScript、纯 CSS（BEM）、`next/font`、测试工具（待补充）。

---

### Task 1: 配置静态导出与测试基础

**Files:**
- Modify: `next.config.ts`
- Modify: `package.json`
- Create: `vitest.config.ts`
- Create: `vitest.setup.ts`
- Create: `tests/smoke/toDigest.test.ts`

**Step 1: Write the failing test**

为 `toDigest()` 编写一个最小失败测试，定义 `DailyReport -> DailyDigest` 的预期转换行为。

**Step 2: Run test to verify it fails**

Run: `npm run test -- tests/smoke/toDigest.test.ts`
Expected: FAIL，因为 `types/daily.ts` 与测试配置尚不存在。

**Step 3: Write minimal implementation**

补充测试运行环境，并准备后续类型文件与导出配置的实现入口。

**Step 4: Run test to verify it passes**

Run: `npm run test -- tests/smoke/toDigest.test.ts`
Expected: PASS。

### Task 2: 建立数据契约与示例日报

**Files:**
- Create: `types/daily.ts`
- Create: `data/daily/index.ts`
- Create: `data/daily/_example.ts`
- Create: `data/daily/2000-01-01.ts`
- Test: `tests/data/reports.test.ts`

**Step 1: Write the failing test**

编写测试验证：
- `reports` 至少含一个示例日报
- `2000-01-01` 已注册
- `toDigest()` 输出统计字段正确

**Step 2: Run test to verify it fails**

Run: `npm run test -- tests/data/reports.test.ts`
Expected: FAIL，因为数据层尚未创建。

**Step 3: Write minimal implementation**

严格按 skill 中的数据契约创建类型与示例数据，并在注册表中按最新优先顺序导出。

**Step 4: Run test to verify it passes**

Run: `npm run test -- tests/data/reports.test.ts`
Expected: PASS。

### Task 3: 实现首页与详情页结构

**Files:**
- Modify: `app/layout.tsx`
- Modify: `app/page.tsx`
- Create: `app/daily/[date]/page.tsx`
- Create: `components/DailyCard.tsx`
- Create: `components/PaperHighlight.tsx`
- Create: `components/PaperBrief.tsx`
- Create: `components/ReportHeader.tsx`
- Create: `components/SectionDivider.tsx`
- Test: `tests/pages/home.test.tsx`
- Test: `tests/pages/daily-page.test.tsx`

**Step 1: Write the failing test**

为首页与详情页编写测试，验证：
- 首页空/非空状态结构
- 详情页可根据日期渲染
- `generateStaticParams()` 与 `generateMetadata()` 行为正确

**Step 2: Run test to verify it fails**

Run: `npm run test -- tests/pages/home.test.tsx tests/pages/daily-page.test.tsx`
Expected: FAIL，因为页面与组件尚未实现。

**Step 3: Write minimal implementation**

实现布局、导航、页脚、首页卡片列表、详情页头区与论文展示组件，确保 `params` 按 Next.js 15+ Promise 方式处理。

**Step 4: Run test to verify it passes**

Run: `npm run test -- tests/pages/home.test.tsx tests/pages/daily-page.test.tsx`
Expected: PASS。

### Task 4: 应用 Bauhaus 设计系统

**Files:**
- Modify: `app/globals.css`

**Step 1: Write the failing test**

以样式 smoke test 或构建验证的方式，确认关键类名与页面可成功编译。

**Step 2: Run test to verify it fails**

Run: `npm run build`
Expected: FAIL 或样式未满足目标。

**Step 3: Write minimal implementation**

将设计系统中的颜色、字体、边框、硬阴影、几何装饰与分区节奏映射到 CSS 变量和组件类名，统一为 BEM 风格。

**Step 4: Run test to verify it passes**

Run: `npm run build`
Expected: PASS。

### Task 5: 补充 README 操作手册与最终验证

**Files:**
- Create: `README.md`

**Step 1: Write the failing test**

人工校验 README 是否覆盖 skill 规定的全部板块与代码模板。

**Step 2: Run test to verify it fails**

Run: 对照 `web-design` skill 检查 README
Expected: FAIL，直到所有板块完整。

**Step 3: Write minimal implementation**

撰写面向其他智能体的操作手册，明确新增日报的数据文件模板、注册方式、类型速查、组件清单与页面结构。

**Step 4: Run test to verify it passes**

Run: `npm run lint && npm run test && npm run build`
Expected: PASS。
