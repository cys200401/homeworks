import { render, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import TrafficBeacon, {
  resetTrafficBeaconDeduplicationForTests,
} from "@/components/traffic/TrafficBeacon";

describe("TrafficBeacon", () => {
  afterEach(() => {
    resetTrafficBeaconDeduplicationForTests();
    vi.restoreAllMocks();
  });

  it("sends one PV request for a page", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue({ ok: true } as Response);

    render(<TrafficBeacon path="/" pageType="home" />);

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledTimes(1);
    });
  });

  it("deduplicates repeated effects for the same page key", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue({ ok: true } as Response);

    const { rerender } = render(<TrafficBeacon path="/" pageType="home" />);
    rerender(<TrafficBeacon path="/" pageType="home" />);

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledTimes(1);
    });
  });

  it("fails open when reporting throws", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockRejectedValue(new Error("network down"));

    expect(() => {
      render(<TrafficBeacon path="/daily/2026-03-14" pageType="daily" />);
    }).not.toThrow();

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledTimes(1);
    });
  });
});
