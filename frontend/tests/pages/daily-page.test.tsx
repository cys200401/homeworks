import type { AnchorHTMLAttributes } from "react";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  notFound: vi.fn(() => {
    throw new Error("NEXT_NOT_FOUND");
  }),
}));

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

import DailyPage, {
  generateMetadata,
  generateStaticParams,
} from "@/app/daily/[date]/page";
import { reports } from "@/data/daily";
import { notFound } from "next/navigation";

describe("Daily report page", () => {
  beforeEach(() => {
    vi.mocked(notFound).mockClear();
  });

  it("generates static params from registered reports", async () => {
    await expect(generateStaticParams()).resolves.toEqual(
      reports.map((report) => ({ date: report.date })),
    );
  });

  it("generates metadata from async params", async () => {
    await expect(
      generateMetadata({
        params: Promise.resolve({ date: "2000-01-01" }),
      }),
    ).resolves.toMatchObject({
      title: "2000年1月1日 AI论文日报（示例） | Daily Paper",
    });
  });

  it("renders the sample report and its sections", async () => {
    render(
      await DailyPage({
        params: Promise.resolve({ date: "2000-01-01" }),
      }),
    );

    expect(
      screen.getByRole("link", { name: /返回首页/i }),
    ).toHaveAttribute("href", "/");
    expect(
      screen.getByRole("heading", {
        name: "2000年1月1日 AI论文日报（示例）",
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /重点关注/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /也值得关注/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /趋势洞察/i }),
    ).toBeInTheDocument();
  });

  it("calls notFound for unknown dates", async () => {
    await expect(
      DailyPage({
        params: Promise.resolve({ date: "1999-12-31" }),
      }),
    ).rejects.toThrow("NEXT_NOT_FOUND");
    expect(notFound).toHaveBeenCalledTimes(1);
  });
});
