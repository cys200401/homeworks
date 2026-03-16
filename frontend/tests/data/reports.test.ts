import { describe, expect, it } from "vitest";

import { reports } from "@/data/daily";
import { toDigest } from "@/types/daily";

describe("daily reports registry", () => {
  it("keeps reports sorted in descending date order", () => {
    const dates = reports.map((report) => report.date);
    const sortedDates = [...dates].sort((left, right) =>
      right.localeCompare(left),
    );

    expect(dates).toEqual(sortedDates);
    expect(new Set(dates).size).toBe(dates.length);
  });

  it("exposes consistent summary counts for the sample homepage digest", () => {
    const sampleReport = reports.find((report) => report.date === "2000-01-01");
    const digest = toDigest(sampleReport!);

    expect(digest.highlightCount).toBeGreaterThanOrEqual(2);
    expect(digest.notableCount).toBeGreaterThanOrEqual(3);
    expect(digest.tags.length).toBeGreaterThanOrEqual(3);
  });
});
