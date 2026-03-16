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

import AdminPage from "@/app/admin/page";

function createDeferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });

  return { promise, resolve, reject };
}

describe("Admin page", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("renders loading state before requests resolve", () => {
    const deferred = createDeferred<Response>();
    vi.spyOn(globalThis, "fetch").mockReturnValue(deferred.promise);

    render(<AdminPage />);

    expect(screen.getByText(/正在加载后台概览/i)).toBeInTheDocument();
  });

  it("renders success state with overview and lists", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
      const url = String(input);

      if (url.endsWith("/api/admin/overview")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            health: { status: "ok", database: "ok" },
            latestStages: [
              { stage: "crawler", status: "succeeded" },
              { stage: "frontend_build", status: "succeeded" },
            ],
            recentErrorCount: 2,
            recentPv: [{ statDate: "2026-03-14", totalPv: 42 }],
          }),
        } as Response);
      }

      if (url.endsWith("/api/admin/pipeline-runs")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            items: [
              { id: "1", stage: "crawler", status: "succeeded" },
              { id: "2", stage: "frontend_build", status: "succeeded" },
            ],
          }),
        } as Response);
      }

      return Promise.resolve({
        ok: true,
        json: async () => ({
          items: [{ id: "e1", stage: "download_pdf", errorMessage: "HTTP 429" }],
        }),
      } as Response);
    });

    render(<AdminPage />);

    await waitFor(() => {
      expect(screen.getByText(/数据库状态/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/数据库状态/i)).toBeInTheDocument();
    expect(screen.getByText(/最近错误数/i)).toBeInTheDocument();
    expect(screen.getAllByText(/crawler/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/HTTP 429/i)).toBeInTheDocument();
  });

  it("renders error state when requests fail", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("network down"));

    render(<AdminPage />);

    await waitFor(() => {
      expect(screen.getByText(/后台数据暂时不可用/i)).toBeInTheDocument();
    });
  });
});
