import { describe, expect, it } from "vitest";

import { toDigest, type DailyReport } from "@/types/daily";

describe("toDigest", () => {
  it("converts a report into homepage digest stats", () => {
    const report: DailyReport = {
      date: "2026-03-13",
      title: "2026年3月13日 AI论文日报",
      summary: "今天的研究集中在智能体推理、视频生成和多模态对齐。",
      totalPapers: 42,
      tags: ["智能体", "视频生成", "多模态"],
      trends: "多模态模型正进一步走向统一推理接口。",
      highlights: [
        {
          arxivId: "2603.00001v1",
          title: "A Highlight Paper",
          authors: ["Ada Lovelace"],
          abstract: "Abstract",
          categories: ["cs.AI"],
          arxivUrl: "https://arxiv.org/abs/2603.00001",
          tldr: "重点论文摘要",
          problem: "研究问题",
          methodology: "方法描述",
          keyFindings: ["发现一", "发现二"],
          significance: "意义说明",
        },
      ],
      notables: [
        {
          arxivId: "2603.00002v1",
          title: "A Notable Paper",
          authors: ["Grace Hopper"],
          abstract: "Abstract",
          categories: ["cs.LG"],
          arxivUrl: "https://arxiv.org/abs/2603.00002",
          tldr: "推荐论文摘要",
          comment: "值得关注",
        },
      ],
    };

    expect(toDigest(report)).toEqual({
      date: "2026-03-13",
      title: "2026年3月13日 AI论文日报",
      summary: "今天的研究集中在智能体推理、视频生成和多模态对齐。",
      totalPapers: 42,
      highlightCount: 1,
      notableCount: 1,
      tags: ["智能体", "视频生成", "多模态"],
    });
  });
});
