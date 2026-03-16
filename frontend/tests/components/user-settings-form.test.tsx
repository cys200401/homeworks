import type { AnchorHTMLAttributes } from "react";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

const push = vi.fn();
const refresh = vi.fn();

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

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push,
    refresh,
  }),
}));

vi.mock("@/components/traffic/TrafficBeacon", () => ({
  default: () => null,
}));

import UserSettingsForm from "@/components/user/UserSettingsForm";

const profileResponse = {
  handle: "vision-scout",
  displayName: "Vision Scout",
  email: "vision-scout@example.com",
  timezone: "Asia/Shanghai",
  delivery: {
    deliveryEnabled: true,
    deliveryLocalTime: "08:30:00",
    windowStartHour: 8,
    windowEndHour: 23,
    lookbackDays: 3,
    categories: ["cs.CV", "cs.AI", "cs.IR"],
    nextRunAt: "2026-03-16T00:30:00Z",
    lastRunAt: "2026-03-15T00:30:00Z",
  },
  themePrompt:
    "Bold brutalist research UI with sharp corners, cobalt accents and compact density.",
  theme: {
    themeName: "brutalist",
    fontPreset: "modern",
    layoutDensity: "compact",
    cardStyle: "outline",
    heroPattern: "rays",
    borderRadius: "sharp",
    motionLevel: "lively",
    palette: {
      background: "#f4f4f0",
      foreground: "#111111",
      accent: "#0047ff",
      accentSoft: "#ffcc00",
      surface: "#ffffff",
      surfaceAlt: "#e7ebff",
      border: "#111111",
    },
  },
  latestReportDate: "2026-03-15",
};

describe("UserSettingsForm", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
    push.mockReset();
    refresh.mockReset();
  });

  it("loads the saved profile and shows editable settings", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => profileResponse,
    } as Response);

    render(<UserSettingsForm handle="vision-scout" />);

    await waitFor(() => {
      expect(screen.getByDisplayValue("Vision Scout")).toBeInTheDocument();
    });

    expect(screen.getByDisplayValue("Asia/Shanghai")).toBeInTheDocument();
    expect(
      screen.getByText(/这里配置每个终端用户自己的投送时间/i),
    ).toBeInTheDocument();
    expect(
      screen.getByDisplayValue(
        /Bold brutalist research UI with sharp corners/i,
      ),
    ).toBeInTheDocument();
  });

  it("saves the theme prompt and updates preview state", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch");
    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        json: async () => profileResponse,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          promptText:
            "Editorial dashboard with warm paper texture, calm motion and rounded cards.",
          theme: {
            themeName: "editorial",
            fontPreset: "editorial",
            layoutDensity: "balanced",
            cardStyle: "panel",
            heroPattern: "mesh",
            borderRadius: "round",
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
        }),
      } as Response);

    render(<UserSettingsForm handle="vision-scout" />);

    await waitFor(() => {
      expect(screen.getByDisplayValue("Vision Scout")).toBeInTheDocument();
    });

    fireEvent.change(
      screen.getByPlaceholderText(
        /Editorial dashboard with warm paper texture/i,
      ),
      {
        target: {
          value:
            "Editorial dashboard with warm paper texture, calm motion and rounded cards.",
        },
      },
    );
    fireEvent.click(screen.getByRole("button", { name: /保存主题 Prompt/i }));

    await waitFor(() => {
      expect(screen.getByText(/主题 Prompt 已保存/i)).toBeInTheDocument();
    });

    expect(fetchMock).toHaveBeenLastCalledWith(
      expect.stringMatching(/\/api\/users\/vision-scout\/theme$/),
      expect.objectContaining({
        method: "PUT",
      }),
    );
  });
});
