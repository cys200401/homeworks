# Daily Report Production Runbook

本手册用于在当前仓库内执行一次完整的日报生产流程。它只覆盖现有 skill 允许的工作方式，不引入新的推荐脚本或写报告脚本。

## 1. 适用范围

本手册适用于以下链路：

`crawler.py` -> 智能体基于终端输出推荐 -> `download_pdf.py` -> `pdf_to_txt.py` -> 写入 `frontend/data/daily/YYYY-MM-DD.ts` -> 更新 `frontend/data/daily/index.ts` -> `npm run build`

不适用于：

- 把推荐逻辑改成读取 `papers.json` 自动打分
- 把深读逻辑改成新的 Python 批处理脚本
- 把日报内容改为数据库真源

## 2. 前置条件

### 2.1 Python 环境

根据 `.qwen/skills/daily-paper/SKILL.md`，准备环境：

```bash
conda create -n arxiv python=3.10 -y
conda activate arxiv
pip install pypdf
```

额外说明：

- `pdf_to_txt.py` 依赖 `pypdf`，必须在已经安装该依赖的 conda 环境中运行。
- 本项目实操中验证通过的环境名称是 `arxiv`，后续命令默认都基于该环境。
- 如果你使用的是别的环境名，请保证其中已安装 `pypdf`，再执行 PDF/TXT 相关步骤。

### 2.2 Node 环境

前端验证使用：

```bash
cd frontend
npm install
```

如果 `node_modules` 已存在，可跳过安装。

## 3. 第一步：抓取 arXiv 元数据

进入脚本目录：

```bash
cd .qwen/skills/daily-paper
```

运行抓取命令：

```bash
python crawler.py \
  --start-date 2026-03-12 \
  --end-date 2026-03-12 \
  --limit 203 \
  --category cs.AI
```

### 输入

- arXiv API
- 日期范围
- 分类
- 限制数量

### 输出

- `papers.json`
- 终端中的“今日论文列表”

### 成功标志

终端应看到类似输出：

```text
抓取完成：原始记录 X 篇，去重后 Y 篇，输出 Z 篇。
已写入 .../papers.json
================================================================================
今日论文列表
================================================================================
```

### 推荐阶段硬规则

- 推荐必须基于 `crawler.py` 刚输出到终端的标题、摘要、分类、URL。
- 不能跳过终端输出，直接声称已经完成推荐。
- `papers.json` 只用于后续定位论文记录、`pdf_path` 和 `txt_path`，不是推荐依据真源。

## 4. 第二步：基于终端输出做推荐

阅读 `crawler.py` 终端输出后，按以下原则筛选候选论文：

- 主题相关性：是否值得进入当日日报
- 新颖性信号：问题设定、方法组合或应用场景是否有价值
- 信息密度：摘要是否足以支持“值得继续读”
- 多样性：不要全部选同一子方向

### 推荐产出要求

推荐阶段至少形成两类结果：

1. `highlights` 候选
   - 后续会补 PDF/TXT 并进行全文深读
2. `notables` 候选
   - 可基于摘要级理解写入，但不能伪装成全文结论

### 推荐阶段禁止事项

- 不要编造实验结果
- 不要把摘要理解写成“阅读全文结论”
- 如果信息不足，只能写“值得进一步核查”

## 5. 第三步：补 PDF

如果推荐论文需要进入 `highlights`，先下载 PDF：

```bash
python download_pdf.py --workers 8
```

### 输入

- `papers.json`

### 输出

- `paper_pdf/*.pdf`
- 回写后的 `papers.json`，其中部分或全部记录会带上 `pdf_path`

### 成功标志

终端应看到类似输出：

```text
PDF 下载完成：成功 X，跳过 Y，失败 Z，结果已写入 .../papers.json
```

### 常见失败场景

#### 场景 1：下载时出现 429 或大量失败

表现：

- 终端出现 `HTTP Error 429`
- 最终统计里 `失败` 大于 0

恢复步骤：

1. 等待 5 到 30 分钟
2. 不要使用 `--force`
3. 降低并发重新运行

```bash
python download_pdf.py --workers 2
```

说明：

- 已成功下载的 PDF 会被自动跳过
- 失败条目会继续重试
- `--force` 会重新下载已成功文件，增加限流风险，因此恢复阶段不要使用

#### 场景 2：`papers.json` 不存在

表现：

- 报错 `未找到输入文件`

恢复步骤：

1. 先重新运行 `crawler.py`
2. 确认 `.qwen/skills/daily-paper/papers.json` 已生成
3. 再运行 `download_pdf.py`

## 6. 第四步：提取 TXT

PDF 到位后提取全文文本：

```bash
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate arxiv
python pdf_to_txt.py --workers 4
```

### 输入

- `papers.json`
- `paper_pdf/*.pdf`

### 输出

- `paper_txt/*.txt`
- 回写后的 `papers.json`，记录中会带上 `txt_path`

### 成功标志

终端应看到类似输出：

```text
文本提取完成：成功 X，跳过 Y，失败 Z，结果已写入 .../papers.json
```

### 常见失败场景

#### 场景 1：缺少 `pdf_path`

表现：

- 终端出现 `缺少 pdf_path，无法提取文本`

恢复步骤：

1. 回到下载步骤，重新执行：

```bash
python download_pdf.py --workers 8
```

2. 如果刚遇到 429，改为低并发：

```bash
python download_pdf.py --workers 2
```

3. 下载成功后，再重跑：

```bash
python pdf_to_txt.py --workers 4
```

#### 场景 2：缺少 `pypdf`

表现：

- 报错提示当前环境缺少 `pypdf`

恢复步骤：

```bash
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate arxiv
pip install pypdf
```

然后重新运行：

```bash
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate arxiv
python pdf_to_txt.py --workers 4
```

#### 场景 3：`pypdf` 已安装，但仍然报缺依赖

表现：

- 系统里某个 Python 环境已经装了 `pypdf`
- 但直接运行 `python pdf_to_txt.py ...` 仍报缺少 `pypdf`

根因：

- 命令没有在安装了 `pypdf` 的 conda 环境中执行

恢复步骤：

```bash
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate arxiv
python -m pip show pypdf
python pdf_to_txt.py --workers 4
```

如果 `python -m pip show pypdf` 查不到，再执行：

```bash
python -m pip install pypdf
```

## 7. 第五步：基于 TXT 做全文深读

只对已确定进入 `highlights` 的论文执行全文深读。

### 输入

- 推荐名单
- `papers.json` 中对应记录
- 推荐论文对应的 `paper_txt/*.txt`

### 规则

- `highlights` 必须来自全文深读结果
- `notables` 可以基于摘要级理解，但仍需遵守 `frontend/types/daily.ts`
- 若某篇推荐论文还没有 `txt_path`，不要把它写成 `highlight`

## 8. 第六步：写日报 TS 文件

进入前端目录前，先确认目标日期，例如 `2026-03-13`。

日报文件路径：

```text
frontend/data/daily/YYYY-MM-DD.ts
```

推荐参考文件：

- `frontend/types/daily.ts`
- `frontend/data/daily/_example.ts`
- `frontend/data/daily/2000-01-01.ts`
- `frontend/data/daily/2026-03-12.ts`

### 最低要求

- 文件必须导出 `report`
- 类型必须是 `DailyReport`
- 字段必须符合 `frontend/types/daily.ts`
- `summary`、`trends`、`tldr`、`problem`、`methodology`、`significance`、`comment` 等中文字段必须真实对应当前推荐/深读结果

### 最小模板

```ts
import type { DailyReport } from "@/types/daily";

export const report: DailyReport = {
  date: "2026-03-13",
  title: "2026年3月13日 AI论文日报",
  summary: "这里填写中文总览。",
  totalPapers: 24,
  tags: ["智能体", "多模态"],
  trends: "这里填写趋势洞察。",
  highlights: [],
  notables: [],
};
```

### 空日报也是合法结果

如果当天抓取结果为 0，或者不满足进入日报的条件，可以像 `frontend/data/daily/2026-03-12.ts` 一样写空日报：

- `totalPapers` 可为 `0`
- `highlights` 可为空数组
- `notables` 可为空数组

## 9. 第七步：更新日报注册表

修改文件：

```text
frontend/data/daily/index.ts
```

操作要求：

1. 新增当日日报 import
2. 把新日报放到 `reports` 数组最前面
3. 保持最新日期在前

示例：

```ts
import type { DailyReport } from "@/types/daily";
import { report as r20260313 } from "./2026-03-13";
import { report as r20260312 } from "./2026-03-12";
import { report as r20000101 } from "./2000-01-01";

export const reports: DailyReport[] = [r20260313, r20260312, r20000101];
```

## 10. 第八步：验证前端构建

进入前端目录：

```bash
cd frontend
```

先跑测试：

```bash
npm run test
```

再跑构建：

```bash
npm run build
```

### 成功标志

- 测试通过
- 构建成功退出
- 新日报可以在首页和 `/daily/YYYY-MM-DD` 静态详情页中被生成

## 11. 最小日报生产路径验证

当你想验证“整个路径能否跑通”时，按以下顺序执行：

```bash
cd .qwen/skills/daily-paper
python crawler.py --start-date 2026-03-12 --end-date 2026-03-12 --limit 203 --category cs.AI
python download_pdf.py --workers 8
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate arxiv
python pdf_to_txt.py --workers 4
cd ../../frontend
npm run test
npm run build
```

然后人工检查：

1. `papers.json` 是否已生成或更新
2. `paper_pdf/` 是否出现 PDF 文件
3. `paper_txt/` 是否出现 TXT 文件
4. 新日报文件是否位于 `frontend/data/daily/`
5. `frontend/data/daily/index.ts` 是否已注册新日报

## 12. 常见问题与恢复

### 12.1 crawler 返回 0 篇

可能原因：

- 指定日期确实没有论文
- 分类过窄

处理方式：

- 若这是事实结果，可以生成空日报
- 若需要提高覆盖率，下一次调整日期范围或分类后重新抓取

### 12.2 crawler 遭遇 429

处理方式：

1. 等待冷却
2. 重跑时拉长请求间隔

```bash
python crawler.py \
  --start-date 2026-03-12 \
  --end-date 2026-03-12 \
  --limit 203 \
  --category cs.AI \
  --request-interval 5 \
  --retries 6
```

### 12.3 下载阶段有失败项

恢复方式：

```bash
python download_pdf.py --workers 2
```

不要立即使用：

```bash
python download_pdf.py --workers 8 --force
```

### 12.4 TXT 阶段有失败项

先确认失败记录是否已有可用 PDF，再重跑：

```bash
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate arxiv
python pdf_to_txt.py --workers 4
```

如果只是部分失败，脚本会跳过已完成文件，继续处理剩余条目。

## 13. 发布前检查清单

发布前至少确认以下事项：

- 已读取 `crawler.py` 的终端输出并据此做推荐
- 每个 `highlight` 都有对应全文阅读依据
- `DailyReport` 字段完整且符合 `frontend/types/daily.ts`
- 新日报已注册到 `frontend/data/daily/index.ts`
- `npm run test` 已执行
- `npm run build` 已执行
- 如发生 429 或下载失败，已按恢复流程处理，而不是盲目使用 `--force`
