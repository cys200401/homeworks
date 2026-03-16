import type { AnchorHTMLAttributes } from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

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

import HomePage from "@/app/page";

describe("Home page", () => {
  it("renders the Daily Paper landing content and sample report card", () => {
    render(<HomePage />);

    expect(
      screen.getByRole("heading", { name: "Daily Paper" }),
    ).toBeInTheDocument();
    expect(screen.getByText(/AI 论文日报/i)).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /2000年1月1日 AI论文日报（示例）/i }),
    ).toHaveAttribute("href", "/daily/2000-01-01");
    expect(
      screen.getByLabelText(/2000年1月1日 AI论文日报（示例） 统计/i),
    ).toHaveTextContent(/重点\s*2\s*篇/i);
    expect(
      screen
        .getAllByRole("link", { name: /打开工作台/i })
        .map((item) => item.getAttribute("href")),
    ).toContain("/u/research-lead");
  });
});
