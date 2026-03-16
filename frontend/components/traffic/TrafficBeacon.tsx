"use client";

import { useEffect } from "react";

type TrafficBeaconProps = {
  path: string;
  pageType: "home" | "daily";
};

const ADMIN_API_BASE_URL =
  process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL ?? "http://127.0.0.1:8000";

declare global {
  interface Window {
    __dailyPaperTrafficSentKeys?: Set<string>;
  }
}

function getSentKeys(): Set<string> {
  if (typeof window === "undefined") {
    return new Set<string>();
  }

  if (!window.__dailyPaperTrafficSentKeys) {
    window.__dailyPaperTrafficSentKeys = new Set<string>();
  }

  return window.__dailyPaperTrafficSentKeys;
}

export function resetTrafficBeaconDeduplicationForTests() {
  if (typeof window !== "undefined") {
    window.__dailyPaperTrafficSentKeys = new Set<string>();
  }
}

export default function TrafficBeacon({
  path,
  pageType,
}: TrafficBeaconProps) {
  useEffect(() => {
    if (typeof window === "undefined" || typeof fetch !== "function") {
      return;
    }

    const requestKey = `${pageType}:${path}`;
    const sentKeys = getSentKeys();

    if (process.env.NODE_ENV !== "production" && sentKeys.has(requestKey)) {
      return;
    }

    sentKeys.add(requestKey);

    void fetch(`${ADMIN_API_BASE_URL}/api/traffic/pv`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        path,
        pageType,
      }),
      keepalive: true,
    }).catch((error: unknown) => {
      if (process.env.NODE_ENV !== "test") {
        console.warn("traffic beacon failed", error);
      }
    });
  }, [pageType, path]);

  return null;
}
