import type { DailyReport } from "@/types/daily";

export const report: DailyReport = {
  date: "2099-12-31",
  title: "2099年12月31日 AI论文日报（示例模板）",
  summary:
    "这是一份仅用于参考的数据模板，展示日报文件需要满足的完整字段结构。重点论文需要基于全文进行更深入的中文解读，推荐论文则提供摘要级别的速览。维护者可以直接复制本文件作为新日报的起点，并按实际论文内容替换所有字段。趋势洞察和标签用于帮助首页与详情页形成统一的主题表达。",
  totalPapers: 18,
  tags: ["示例模板", "智能体", "多模态"],
  trends:
    "日报模板建议围绕当日最突出的研究主题组织内容，例如智能体、世界模型或高效训练。",
  highlights: [
    {
      arxivId: "9912.00001v1",
      title: "Example Foundation Models for Coordinated Agents",
      authors: ["Lin Example", "Ming Demo"],
      abstract:
        "This example paper studies how a unified language model can plan and coordinate multiple agents under constrained communication budgets.",
      categories: ["cs.AI", "cs.MA"],
      arxivUrl: "https://arxiv.org/abs/9912.00001",
      tldr: "统一模型协调多智能体任务执行。",
      problem: "论文关注受限通信条件下，多智能体系统如何共享计划与分工信息。",
      methodology:
        "作者构建了一个分层式协调框架，由统一语言模型生成全局计划，再将子任务分配给具备不同工具能力的执行代理。为了控制通信成本，方法在关键节点才交换压缩后的状态摘要。",
      keyFindings: [
        "在三类协同任务上，相比独立代理基线取得更高成功率。",
        "压缩通信策略能显著降低消息数量而保持性能稳定。",
      ],
      significance: "这类协调机制有助于推动真实复杂环境中的多智能体部署。",
      limitations: "实验环境仍以模拟任务为主，离真实生产场景还有距离。",
    },
  ],
  notables: [
    {
      arxivId: "9912.00002v1",
      title: "Example Efficient Vision-Language Alignment",
      authors: ["Q. Sample", "R. Placeholder"],
      abstract:
        "This example work presents a lightweight recipe for aligning visual and textual representations under limited compute.",
      categories: ["cs.CV", "cs.CL"],
      arxivUrl: "https://arxiv.org/abs/9912.00002",
      tldr: "低算力下实现视觉语言高效对齐。",
      comment: "适合作为资源受限场景中的工程参考。",
    },
  ],
};
