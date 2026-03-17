import type { AnchorHTMLAttributes } from "react";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...props
  }: AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

vi.mock("@/components/traffic/TrafficBeacon", () => ({
  default: () => null,
}));

import UserWorkspace from "@/components/user/UserWorkspace";

const workspaceResponse = {
  user: {
    handle: "research-lead",
    displayName: "Research Lead",
    email: "research-lead@example.com",
    timezone: "America/Los_Angeles",
    delivery: {
      deliveryEnabled: true,
      deliveryLocalTime: "08:00:00",
      windowStartHour: 0,
      windowEndHour: 12,
      lookbackDays: 2,
      categories: ["cs.AI", "cs.LG", "cs.CL"],
      nextRunAt: "2026-03-16T15:00:00Z",
      lastRunAt: "2026-03-15T15:00:00Z",
    },
    themePrompt:
      "Editorial dashboard with warm paper texture, calm motion and rounded cards.",
    theme: {
      themeName: "editorial",
      fontPreset: "editorial",
      layoutDensity: "balanced",
      cardStyle: "panel",
      heroPattern: "mesh",
      borderRadius: "soft",
      motionLevel: "calm",
      palette: {
        background: "#f4efe5",
        foreground: "#18161a",
        accent: "#b45309",
        accentSoft: "#facc15",
        surface: "#fffaf1",
        surfaceAlt: "#efe3cf",
        border: "#1f2937",
      },
    },
    latestReportDate: "2026-03-15",
  },
  report: {
    date: "2026-03-15",
    title: "Research Lead 的个性化 AI 晨报",
    summary: "系统按用户配置筛出了重点论文。",
    totalPapers: 5,
    tags: ["智能体系统", "训练效率"],
    trends: "研究方向正在从单点模型竞赛转向系统能力建设。",
    publishedAt: "2026-03-15T15:00:00Z",
    theme: {
      themeName: "editorial",
      fontPreset: "editorial",
      layoutDensity: "balanced",
      cardStyle: "panel",
      heroPattern: "mesh",
      borderRadius: "soft",
      motionLevel: "calm",
      palette: {
        background: "#f4efe5",
        foreground: "#18161a",
        accent: "#b45309",
        accentSoft: "#facc15",
        surface: "#fffaf1",
        surfaceAlt: "#efe3cf",
        border: "#1f2937",
      },
    },
    source: {
      timezone: "America/Los_Angeles",
      effectiveLookbackDays: 4,
      searchExpanded: true,
      crawlMeta: {
        triggerMode: "due_delivery",
        triggeredAt: "2026-03-15T15:00:00Z",
        uniqueRecords: 8,
        upserted: 8,
      },
    },
    highlights: [
      {
        arxivId: "2603.15001v1",
        title: "Composable Agent Loops for Reliable Scientific Discovery",
        authors: ["Ada Lovelace"],
        abstract: "Test abstract",
        categories: ["cs.AI"],
        arxivUrl: "https://arxiv.org/abs/2603.15001",
        tldr: "通过可组合智能体循环提升科研任务可靠性。",
        problem: "问题",
        methodology: "方法",
        keyFindings: ["发现 1", "发现 2"],
        significance: "意义",
        limitations: "局限",
      },
    ],
    notables: [
      {
        arxivId: "2603.15002v1",
        title: "Sparse Preference Tuning for Long-Context Assistants",
        authors: ["Chelsea Finn"],
        abstract: "Test abstract",
        categories: ["cs.CL"],
        arxivUrl: "https://arxiv.org/abs/2603.15002",
        tldr: "稀疏偏好优化降低长上下文助手训练成本。",
        comment: "适合作为训练预算方向的跟踪项。",
      },
    ],
  },
};

describe("UserWorkspace", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("loads and renders the personalized workspace", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => workspaceResponse,
    } as Response);

    render(<UserWorkspace handle="research-lead" />);

    await waitFor(() => {
      expect(screen.getByText(/编辑时间窗与主题/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/编辑时间窗与主题/i)).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Research Lead" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", {
        name: /Research Lead 的个性化 AI 晨报/i,
      }),
    ).toBeInTheDocument();
    expect(screen.getByText(/当前主题 Prompt/i)).toBeInTheDocument();
    expect(screen.getByText(/最近自动抓取/i)).toBeInTheDocument();
    expect(screen.getByText(/到点自动抓取/i)).toBeInTheDocument();
    expect(screen.getByText(/趋势洞察/i)).toBeInTheDocument();
  });
});
